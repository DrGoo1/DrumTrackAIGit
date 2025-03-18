# drum_analysis/instruments/tom.py

"""
Enhanced tom drum analyzer for the DrumTracKAI framework.

This module provides specialized analysis for tom drum sounds, with the ability to
detect various playing techniques, articulations, and tom sizes.
"""

import numpy as np
import librosa
import scipy.signal
import logging
from typing import Dict, Any, Optional, Tuple, List

logger = logging.getLogger(__name__)


class TomAnalyzer:
    """
    Analyzer for tom drum samples.

    This class provides specialized analysis for tom drum sounds,
    including playing technique detection and size estimation.
    """

    def __init__(self):
        """Initialize the tom analyzer."""
        self.instrument_type = 'tom'

    def analyze(self, y: np.ndarray, sr: int, purpose: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze a tom drum sample.

        Args:
            y: Audio data
            sr: Sample rate
            purpose: Optional purpose classification

        Returns:
            Dictionary of analysis features
        """
        # Basic features
        features = {}

        # Calculate basic features
        features['rms_energy'] = float(np.sqrt(np.mean(y ** 2)))
        features['peak_amplitude'] = float(np.max(np.abs(y)))

        # Spectral features
        spec = np.abs(librosa.stft(y))

        features['spectral_centroid'] = float(np.mean(librosa.feature.spectral_centroid(S=spec, sr=sr)))
        features['spectral_bandwidth'] = float(np.mean(librosa.feature.spectral_bandwidth(S=spec, sr=sr)))
        features['spectral_rolloff'] = float(np.mean(librosa.feature.spectral_rolloff(S=spec, sr=sr)))

        # Tom-specific features
        features['resonance'] = self._calculate_resonance(y, sr)
        features['pitch'] = self._estimate_pitch(y, sr)

        # Detect tom size
        size, confidence = self._estimate_size(y, sr, spec)
        features['tom_size'] = size
        features['size_confidence'] = float(confidence)

        # Detect playing technique
        technique, confidence = self._detect_playing_technique(y, sr, spec)
        features['playing_technique'] = technique
        features['technique_confidence'] = float(confidence)

        # Add purpose-specific features
        if purpose == 'sonic_reference':
            features['tone_fullness'] = self._calculate_tone_fullness(y, sr, spec)
            features['attack_quality'] = self._calculate_attack_quality(y, sr)
        elif purpose == 'technique_training':
            features['roll_quality'] = self._analyze_roll_quality(y, sr)
            features['consistency'] = self._analyze_consistency(y, sr)
        elif purpose == 'style_examples':
            features['fill_complexity'] = self._analyze_fill_complexity(y, sr)
            features['multi_tom_detection'] = self._detect_multi_tom(y, sr, spec)

        return features

    def _calculate_resonance(self, y: np.ndarray, sr: int) -> float:
        """
        Calculate the resonance of a tom drum.

        Args:
            y: Audio data
            sr: Sample rate

        Returns:
            Resonance score (0.0 to 1.0)
        """
        # Calculate amplitude envelope
        env = np.abs(y)

        # Find the peak
        peak_idx = np.argmax(env)
        peak_amp = env[peak_idx]

        if peak_idx >= len(env) - 1 or peak_amp == 0:
            return 0.0

        # Calculate decay rate
        decay_rate = self._calculate_decay_rate(env[peak_idx:])

        # Calculate sustain length (time to decay to 10% of peak)
        threshold = peak_amp * 0.1
        end_idx = len(env)

        for i in range(peak_idx, len(env)):
            if env[i] < threshold:
                end_idx = i
                break

        sustain_length = (end_idx - peak_idx) / sr

        # Calculate pitch stability
        try:
            # Extract pitch over time
            pitches, magnitudes = librosa.piptrack(y=y, sr=sr)

            # Focus on the strongest frequencies
            pitch_idx = np.argmax(magnitudes, axis=0)
            pitch_values = np.array([pitches[idx, t] for t, idx in enumerate(pitch_idx)])

            # Calculate stability as inverse of standard deviation
            if len(pitch_values) > 0 and np.mean(pitch_values) > 0:
                pitch_stability = 1.0 - min(1.0, np.std(pitch_values) / np.mean(pitch_values))
            else:
                pitch_stability = 0.5  # Default value
        except Exception as e:
            logger.debug(f"Error calculating pitch stability: {e}")
            pitch_stability = 0.5  # Default value

        # Combine factors
        # - Slower decay rate = more resonance
        # - Longer sustain = more resonance
        # - Stable pitch = more resonance
        resonance = (
                (1.0 - min(1.0, decay_rate / 10.0)) * 0.4 +  # Inverse of decay rate
                min(1.0, sustain_length / 1.0) * 0.4 +  # Normalized sustain length
                pitch_stability * 0.2  # Pitch stability
        )

        return float(resonance)

    def _estimate_pitch(self, y: np.ndarray, sr: int) -> float:
        """
        Estimate the fundamental pitch of a tom drum.

        Args:
            y: Audio data
            sr: Sample rate

        Returns:
            Estimated pitch in Hz
        """
        # Apply bandpass filter to focus on typical tom frequencies (60-300 Hz)
        # This helps eliminate noise and focus on the fundamental
        lowcut = 60.0
        highcut = 300.0
        b, a = scipy.signal.butter(4, [lowcut / (sr / 2), highcut / (sr / 2)], 'band')
        y_filtered = scipy.signal.filtfilt(b, a, y)

        try:
            # Extract onset for cleaner pitch estimation
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            onsets = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr, units='samples')

            if len(onsets) > 0:
                # Use first onset
                onset_idx = onsets[0]
                # Extract segment after onset
                segment_start = onset_idx
                segment_end = min(onset_idx + int(0.2 * sr), len(y_filtered))  # 200ms segment
                if segment_end > segment_start:
                    segment = y_filtered[segment_start:segment_end]
                else:
                    segment = y_filtered
            else:
                segment = y_filtered

            # Estimate pitch using autocorrelation
            if len(segment) > 0:
                r = librosa.autocorrelate(segment)

                # Find peaks in autocorrelation
                peaks = scipy.signal.find_peaks(r)[0]

                if len(peaks) > 0:
                    # Find the first significant peak (excluding zero lag)
                    significant_peaks = peaks[peaks > 10]  # Skip very early peaks

                    if len(significant_peaks) > 0:
                        first_peak = significant_peaks[0]

                        # Convert lag to frequency
                        pitch = sr / first_peak

                        # Sanity check: typical tom frequencies
                        if 60 <= pitch <= 300:
                            return float(pitch)

            # Fallback: use pitch tracking
            pitches, magnitudes = librosa.piptrack(y=y_filtered, sr=sr)

            # Take the average of the most prominent pitches
            pitch_idx = np.argmax(magnitudes, axis=0)
            pitch_values = np.array([pitches[idx, t] for t, idx in enumerate(pitch_idx)])

            # Filter to focus on the most reliable portions
            reliable_pitches = pitch_values[magnitudes[pitch_idx, np.arange(len(pitch_idx))] > 0.1 * np.max(magnitudes)]

            if len(reliable_pitches) > 0:
                # Use the median to avoid outliers
                pitch = np.median(reliable_pitches)

                # Sanity check: typical tom frequencies
                if 60 <= pitch <= 300:
                    return float(pitch)
        except Exception as e:
            logger.debug(f"Error estimating pitch: {e}")

        # Default fallbacks based on spectral centroid if other methods fail
        spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))

        # Very rough approximation based on centroid
        if spectral_centroid < 200:
            return 80.0  # Floor tom
        elif spectral_centroid < 400:
            return 120.0  # Mid tom
        else:
            return 180.0  # High tom

    def _estimate_size(self, y: np.ndarray, sr: int,
                       spec: Optional[np.ndarray] = None) -> Tuple[str, float]:
        """
        Estimate the size of the tom.

        Args:
            y: Audio data
            sr: Sample rate
            spec: Optional pre-computed spectrogram

        Returns:
            Tuple of (size, confidence)
        """
        # Compute spectral features if not provided
        if spec is None:
            spec = np.abs(librosa.stft(y))

        # Extract key features for classification
        spectral_centroid = np.mean(librosa.feature.spectral_centroid(S=spec, sr=sr))

        # Estimate fundamental pitch
        pitch = self._estimate_pitch(y, sr)

        # Calculate resonance
        resonance = self._calculate_resonance(y, sr)

        # Calculate attack characteristics
        attack_time = self._calculate_attack_time(y, sr)

        # Calculate sustain length
        sustain_length = self._calculate_sustain_length(y, sr)

        # Small tom characteristics:
        # - Higher pitch (typically > 150 Hz)
        # - Higher spectral centroid
        # - Shorter sustain
        # - Less resonance
        small_score = (
                (1.0 if pitch > 150 else 0.5) +
                (1.0 if spectral_centroid > 400 else 0.5) +
                (1.0 if sustain_length < 0.6 else 0.5) +
                (1.0 if resonance < 0.6 else 0.5)
        )

        # Medium tom characteristics:
        # - Medium pitch (typically 100-150 Hz)
        # - Medium spectral centroid
        # - Medium sustain
        # - Medium resonance
        medium_score = (
                (1.0 if 100 <= pitch <= 150 else 0.5) +
                (1.0 if 250 <= spectral_centroid <= 400 else 0.5) +
                (1.0 if 0.6 <= sustain_length <= 0.8 else 0.5) +
                (1.0 if 0.5 <= resonance <= 0.7 else 0.5)
        )

        # Floor tom characteristics:
        # - Lower pitch (typically < 100 Hz)
        # - Lower spectral centroid
        # - Longer sustain
        # - More resonance
        floor_score = (
                (1.0 if pitch < 100 else 0.5) +
                (1.0 if spectral_centroid < 250 else 0.5) +
                (1.0 if sustain_length > 0.8 else 0.5) +
                (1.0 if resonance > 0.7 else 0.5)
        )

        # Determine tom size based on highest score
        scores = {
            'small': small_score,
            'medium': medium_score,
            'floor': floor_score
        }

        size = max(scores, key=scores.get)
        max_score = scores[size]

        # Convert score to confidence (4 questions, each worth 1 point, max total = 4)
        confidence = max_score / 4

        return size, confidence

    def _detect_playing_technique(self, y: np.ndarray, sr: int,
                                  spec: Optional[np.ndarray] = None) -> Tuple[str, float]:
        """
        Detect the playing technique used on the tom.

        Args:
            y: Audio data
            sr: Sample rate
            spec: Optional pre-computed spectrogram

        Returns:
            Tuple of (technique, confidence)
        """
        # Compute spectral features if not provided
        if spec is None:
            spec = np.abs(librosa.stft(y))

        # Extract key features for classification
        spectral_centroid = np.mean(librosa.feature.spectral_centroid(S=spec, sr=sr))
        spectral_contrast = np.mean(librosa.feature.spectral_contrast(S=spec, sr=sr))

        # Calculate attack characteristics
        attack_time = self._calculate_attack_time(y, sr)
        attack_slope = self._calculate_attack_slope(y, sr)

        # Calculate transient-to-sustain ratio
        transient_ratio = self._calculate_transient_ratio(y, sr)

        # Center hit characteristics:
        # - Balanced frequency response
        # - Clear fundamental
        # - Moderate attack time
        center_score = (
                (1.0 if 0.005 < attack_time < 0.02 else 0.5) +
                (1.0 if transient_ratio < 0.7 else 0.5) +
                (1.0 if spectral_contrast > 15 else 0.5) +
                (1.0 if self._has_clear_fundamental(y, sr) else 0.5)
        )

        # Edge hit characteristics:
        # - Higher frequency content
        # - Less pronounced fundamental
        # - Slightly shorter sustain
        edge_score = (
                (1.0 if spectral_centroid > 300 else 0.5) +
                (1.0 if not self._has_clear_fundamental(y, sr) else 0.5) +
                (1.0 if attack_time < 0.01 else 0.5) +
                (1.0 if transient_ratio > 0.6 else 0.5)
        )

        # Rimshot characteristics:
        # - Very high frequency content
        # - Sharp attack
        # - Strong transient
        # - Less resonance
        rimshot_score = (
                (1.0 if spectral_centroid > 500 else 0.5) +
                (1.0 if attack_time < 0.005 else 0.5) +
                (1.0 if attack_slope > 0.8 else 0.5) +
                (1.0 if transient_ratio > 0.8 else 0.5)
        )

        # Roll characteristics:
        # - Multiple rapid onsets
        # - Sustained energy
        # - Less defined attack
        roll_score = (
                (1.0 if self._detect_multiple_onsets(y, sr) else 0.0) +
                (1.0 if attack_slope < 0.5 else 0.5) +
                (1.0 if attack_time > 0.02 else 0.5) +
                (1.0 if transient_ratio < 0.5 else 0.5)
        )

        # Determine technique based on highest score
        scores = {
            'center_hit': center_score,
            'edge_hit': edge_score,
            'rimshot': rimshot_score,
            'roll': roll_score
        }

        technique = max(scores, key=scores.get)
        max_score = scores[technique]

        # Convert score to confidence (4 questions, each worth 1 point, max total = 4)
        confidence = max_score / 4

        return technique, confidence

    def _calculate_attack_time(self, y: np.ndarray, sr: int) -> float:
        """
        Calculate the attack time of the sound.

        Args:
            y: Audio data
            sr: Sample rate

        Returns:
            Attack time in seconds
        """
        # Get envelope
        env = np.abs(y)

        # Find peak
        peak_idx = np.argmax(env)
        peak_amp = env[peak_idx]

        if peak_idx == 0 or peak_amp == 0:
            return 0.0

        # Find the start of the attack (10% of peak amplitude)
        threshold = peak_amp * 0.1
        start_idx = 0

        for i in range(peak_idx, 0, -1):
            if env[i] < threshold:
                start_idx = i
                break

        attack_time = (peak_idx - start_idx) / sr

        return float(attack_time)

    def _calculate_attack_slope(self, y: np.ndarray, sr: int) -> float:
        """
        Calculate the slope of the attack.

        Args:
            y: Audio data
            sr: Sample rate

        Returns:
            Attack slope (0.0 to 1.0)
        """
        # Get envelope
        env = np.abs(y)

        # Find peak
        peak_idx = np.argmax(env)
        peak_amp = env[peak_idx]

        if peak_idx == 0 or peak_amp == 0:
            return 0.0

        # Find the start of the attack (10% of peak amplitude)
        threshold = peak_amp * 0.1
        start_idx = 0

        for i in range(peak_idx, 0, -1):
            if env[i] < threshold:
                start_idx = i
                break

        attack_duration = (peak_idx - start_idx) / sr

        if attack_duration == 0:
            return 1.0  # Immediate attack (sharpest)

        # Calculate the slope of the attack
        attack_slope = (peak_amp - env[start_idx]) / attack_duration

        # Normalize to 0-1 range (higher = sharper)
        normalized_slope = min(1.0, attack_slope / (peak_amp * 100))

        return float(normalized_slope)

    def _calculate_decay_rate(self, env: np.ndarray) -> float:
        """
        Calculate the decay rate of a signal envelope.

        Args:
            env: Amplitude envelope

        Returns:
            Decay rate (higher = faster decay)
        """
        if len(env) < 2:
            return 0.0

        try:
            # Estimate decay rate using exponential fit
            time = np.arange(len(env))
            log_decay = np.log(env + 1e-10)  # Avoid log(0)

            # Linear regression on log decay
            if len(time) > 1:
                polyfit = np.polyfit(time, log_decay, 1)
                decay_rate = -polyfit[0]  # Negative slope
                return float(decay_rate * 1000)  # Scale for readability
            else:
                return 0.0
        except Exception as e:
            logger.debug(f"Error calculating decay rate: {e}")
            return 0.0

    def _calculate_sustain_length(self, y: np.ndarray, sr: int) -> float:
        """
        Calculate how long the sound sustains.

        Args:
            y: Audio data
            sr: Sample rate

        Returns:
            Sustain length in seconds
        """
        # Get envelope
        env = np.abs(y)

        # Find peak
        peak_idx = np.argmax(env)
        peak_amp = env[peak_idx]

        if peak_idx >= len(env) - 1 or peak_amp == 0:
            return 0.0

        # Find where amplitude drops to 10% of peak
        threshold = peak_amp * 0.1
        end_idx = len(env)

        for i in range(peak_idx, len(env)):
            if env[i] < threshold:
                end_idx = i
                break

        sustain_length = (end_idx - peak_idx) / sr

        return float(sustain_length)

    def _calculate_transient_ratio(self, y: np.ndarray, sr: int) -> float:
        """
        Calculate the ratio of transient to sustain energy.

        Args:
            y: Audio data
            sr: Sample rate

        Returns:
            Transient ratio (0.0 to 1.0)
        """
        env = np.abs(y)

        # Find peak
        peak_idx = np.argmax(env)

        if peak_idx >= len(y) - 1:
            return 0.0

        # Define transient and sustain regions
        transient_end = min(peak_idx + int(0.02 * sr), len(y))  # First 20ms including attack
        sustain_end = len(y)

        # Calculate energy in each region
        transient_energy = np.sum(env[:transient_end] ** 2)
        total_energy = np.sum(env ** 2)

        if total_energy == 0:
            return 0.0

        # Calculate ratio
        transient_ratio = transient_energy / total_energy

        return float(transient_ratio)

    def _has_clear_fundamental(self, y: np.ndarray, sr: int) -> bool:
        """
        Determine if the sound has a clear fundamental frequency.

        Args:
            y: Audio data
            sr: Sample rate

        Returns:
            True if a clear fundamental is detected
        """
        try:
            # Apply bandpass filter to focus on typical tom frequencies
            lowcut = 60.0
            highcut = 300.0
            b, a = scipy.signal.butter(4, [lowcut / (sr / 2), highcut / (sr / 2)], 'band')
            y_filtered = scipy.signal.filtfilt(b, a, y)

            # Calculate onset for cleaner analysis
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            onsets = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr, units='samples')

            if len(onsets) > 0:
                # Use segment after first onset
                onset_idx = onsets[0]
                segment_start = onset_idx
                segment_end = min(onset_idx + int(0.2 * sr), len(y_filtered))
                if segment_end > segment_start:
                    segment = y_filtered[segment_start:segment_end]
                else:
                    segment = y_filtered
            else:
                segment = y_filtered

            # Calculate power spectrum
            spec = np.abs(librosa.stft(segment)) ** 2

            # Sum across time
            spec_sum = np.sum(spec, axis=1)

            if len(spec_sum) > 0:
                # Find peaks in the spectrum
                peaks, _ = scipy.signal.find_peaks(spec_sum, height=0.1 * np.max(spec_sum))

                if len(peaks) > 0:
                    # Find the largest peak
                    main_peak = peaks[np.argmax(spec_sum[peaks])]

                    # Check if the main peak is significantly stronger than others
                    main_peak_height = spec_sum[main_peak]
                    other_peaks = [p for p in peaks if p != main_peak]

                    if other_peaks:
                        other_peak_heights = spec_sum[other_peaks]
                        max_other_height = np.max(other_peak_heights)

                        # If main peak is at least 1.5 times higher than others, it's a clear fundamental
                        if main_peak_height > 1.5 * max_other_height:
                            return True
        except Exception as e:
            logger.debug(f"Error checking fundamental: {e}")

        return False

    def _detect_multiple_onsets(self, y: np.ndarray, sr: int) -> bool:
        """
        Detect if there are multiple rapid onsets (e.g., for rolls).

        Args:
            y: Audio data
            sr: Sample rate

        Returns:
            True if multiple rapid onsets are detected
        """
        # Use onset detection
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        onsets = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr, units='time')

        # Check for multiple onsets in a short time
        if len(onsets) < 2:
            return False

        # Calculate time between consecutive onsets
        onset_diffs = np.diff(onsets)

        # Check for at least one pair of onsets that are close together
        # (typical for rolls: 16th notes at 100BPM = 0.15s, 32nd notes = 0.075s)
        return np.any(onset_diffs < 0.15)

    def _calculate_tone_fullness(self, y: np.ndarray, sr: int, spec: np.ndarray) -> float:
        """
        Calculate the tonal fullness of the tom.

        Args:
            y: Audio data
            sr: Sample rate
            spec: Spectrogram

        Returns:
            Tone fullness score (0.0 to 1.0)
        """
        # Full tom tone has:
        # - Clear fundamental
        # - Good harmonic content
        # - Appropriate resonance
        # - Balanced frequency distribution

        # Check for clear fundamental
        has_fundamental = self._has_clear_fundamental(y, sr)

        # Calculate resonance
        resonance = self._calculate_resonance(y, sr)

        # Calculate spectral centroid
        spectral_centroid = np.mean(librosa.feature.spectral_centroid(S=spec, sr=sr))

        # Calculate frequency band distribution
        # Sum across time
        spec_sum = np.sum(spec, axis=1)

        # Determine ideal band distribution based on tom size
        size, _ = self._estimate_size(y, sr, spec)

        if size == 'small':
            # Small toms have more high-mid content
            ideal_low = 0.3
            ideal_mid = 0.5
            ideal_high = 0.2
            ideal_centroid = 400
        elif size == 'medium':
            # Medium toms have balanced content
            ideal_low = 0.4
            ideal_mid = 0.4
            ideal_high = 0.2
            ideal_centroid = 300
        else:  # floor
            # Floor toms have more low content
            ideal_low = 0.6
            ideal_mid = 0.3
            ideal_high = 0.1
            ideal_centroid = 200

        # Calculate band boundaries
        low_idx = int(len(spec_sum) * 0.15)
        mid_idx = int(len(spec_sum) * 0.5)

        # Calculate band energies
        total_energy = np.sum(spec_sum)
        if total_energy > 0:
            low_ratio = np.sum(spec_sum[:low_idx]) / total_energy
            mid_ratio = np.sum(spec_sum[low_idx:mid_idx]) / total_energy
            high_ratio = np.sum(spec_sum[mid_idx:]) / total_energy
        else:
            low_ratio = mid_ratio = high_ratio = 0

        # Calculate deviation from ideal
        band_deviation = (
                abs(low_ratio - ideal_low) +
                abs(mid_ratio - ideal_mid) +
                abs(high_ratio - ideal_high)
        )

        # Calculate centroid deviation from ideal
        centroid_deviation = abs(spectral_centroid - ideal_centroid) / ideal_centroid

        # Combine factors
        fullness = (
                (1.0 if has_fundamental else 0.5) * 0.3 +
                resonance * 0.3 +
                (1.0 - min(1.0, band_deviation)) * 0.2 +
                (1.0 - min(1.0, centroid_deviation)) * 0.2
        )

        return float(fullness)

    def _calculate_attack_quality(self, y: np.ndarray, sr: int) -> float:
        """
        Calculate the quality of the attack.

        Args:
            y: Audio data
            sr: Sample rate

        Returns:
            Attack quality score (0.0 to 1.0)
        """
        # Good attack characteristics:
        # - Appropriate attack time (not too fast, not too slow)
        # - Clean onset
        # - Good transient definition

        # Calculate attack time
        attack_time = self._calculate_attack_time(y, sr)

        # Calculate attack slope
        attack_slope = self._calculate_attack_slope(y, sr)

        # Determine ideal attack time based on tom size
        size, _ = self._estimate_size(y, sr)

        if size == 'small':
            ideal_attack = 0.01
        elif size == 'medium':
            ideal_attack = 0.015
        else:  # floor
            ideal_attack = 0.02

        # Calculate deviation from ideal attack time
        attack_deviation = abs(attack_time - ideal_attack) / ideal_attack

        # Calculate onset clarity
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        onset_strength = np.max(onset_env)

        # Normalize onset strength
        norm_onset = min(1.0, onset_strength / 5.0)

        # Calculate transient definition (ratio of transient to sustain)
        transient_ratio = self._calculate_transient_ratio(y, sr)

        # For toms, ideal transient ratio is around 0.4-0.6
        transient_quality = 1.0 - min(1.0, abs(transient_ratio - 0.5) * 2)

        # Combine factors
        quality = (
                (1.0 - min(1.0, attack_deviation)) * 0.3 +
                norm_onset * 0.3 +
                attack_slope * 0.2 +
                transient_quality * 0.2
        )

        return float(quality)

    def _analyze_roll_quality(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """
        Analyze the quality of a drum roll.

        Args:
            y: Audio data
            sr: Sample rate

        Returns:
            Dictionary with roll analysis
        """
        # Detect onsets
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        onsets = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr, units='time')

        if len(onsets) < 3:
            return {
                'is_roll': False,
                'speed': 0.0,
                'evenness': 0.0,
                'quality': 0.0
            }

        # Calculate inter-onset intervals
        intervals = np.diff(onsets)

        # Calculate average interval (in seconds)
        avg_interval = np.mean(intervals)

        # Calculate speed in strokes per second
        speed = 1.0 / avg_interval if avg_interval > 0 else 0.0

        # Detect if it's actually a roll (based on speed)
        is_roll = speed > 4.0  # Faster than 8th notes at 120 BPM

        if not is_roll:
            return {
                'is_roll': False,
                'speed': float(speed),
                'evenness': 0.0,
                'quality': 0.0
            }

        # Calculate evenness (consistency of intervals)
        evenness = 1.0 - min(1.0, np.std(intervals) / avg_interval)

        # Get onset strengths
        onset_strengths = onset_env[librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr)]

        # Calculate dynamic consistency
        if len(onset_strengths) > 1:
            dynamic_consistency = 1.0 - min(1.0, np.std(onset_strengths) / np.mean(onset_strengths))
        else:
            dynamic_consistency = 1.0

        # Combine factors for overall quality
        quality = (evenness * 0.6) + (dynamic_consistency * 0.4)

        return {
            'is_roll': True,
            'speed': float(speed),
            'evenness': float(evenness),
            'dynamic_consistency': float(dynamic_consistency),
            'quality': float(quality)
        }

    def _analyze_consistency(self, y: np.ndarray, sr: int) -> float:
        """
        Analyze the consistency of tom hits.

        Args:
            y: Audio data
            sr: Sample rate

        Returns:
            Consistency score (0.0 to 1.0)
        """
        # For consistency analysis, we need multiple hits

        # Detect onsets
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        onsets = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr)

        if len(onsets) < 2:
            return 1.0  # Not enough onsets to analyze consistency

        # Get onset strengths
        onset_strengths = onset_env[onsets]

        # Calculate timing consistency
        onset_times = librosa.frames_to_time(onsets, sr=sr)
        intervals = np.diff(onset_times)

        timing_consistency = 1.0 - min(1.0, np.std(intervals) / np.mean(intervals))

        # Calculate dynamic consistency
        dynamic_consistency = 1.0 - min(1.0, np.std(onset_strengths) / np.mean(onset_strengths))

        # Calculate timbral consistency
        timbral_consistency = 0.8  # Default value

        try:
            # Extract short segments around each onset
            segments = []
            for onset in onsets:
                start = max(0, onset - 1)  # 1 frame before onset
                end = min(len(onset_env), onset + 4)  # 4 frames after onset

                if start < end and start < len(y) and end <= len(y):
                    frame_length = 2048  # STFT frame length
                    start_sample = librosa.frames_to_samples(start, hop_length=512)[0]
                    end_sample = librosa.frames_to_samples(end, hop_length=512)[0]

                    if end_sample > start_sample and end_sample <= len(y):
                        segment = y[start_sample:end_sample]
                        segments.append(segment)

            # Compare spectral content of segments
            if len(segments) >= 2:
                segment_specs = []
                for segment in segments:
                    if len(segment) >= 2048:
                        segment_spec = np.abs(librosa.stft(segment, n_fft=2048, hop_length=512))
                        segment_specs.append(np.mean(segment_spec, axis=1))

                # Calculate pairwise similarities
                if len(segment_specs) >= 2:
                    similarities = []
                    for i in range(len(segment_specs)):
                        for j in range(i + 1, len(segment_specs)):
                            # Normalize spectra
                            spec1 = segment_specs[i] / np.sum(segment_specs[i])
                            spec2 = segment_specs[j] / np.sum(segment_specs[j])

                            # Calculate cosine similarity
                            similarity = np.sum(spec1 * spec2) / (
                                        np.sqrt(np.sum(spec1 ** 2)) * np.sqrt(np.sum(spec2 ** 2)))
                            similarities.append(similarity)

                    if similarities:
                        timbral_consistency = float(np.mean(similarities))
        except Exception as e:
            logger.debug(f"Error calculating timbral consistency: {e}")

        # Combine factors
        consistency = (timing_consistency * 0.4) + (dynamic_consistency * 0.3) + (timbral_consistency * 0.3)

        return float(consistency)

    def _analyze_fill_complexity(self, y: np.ndarray, sr: int) -> float:
        """
        Analyze the complexity of a tom fill.

        Args:
            y: Audio data
            sr: Sample rate

        Returns:
            Fill complexity score (1.0 to 10.0)
        """
        # Extract onset pattern
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        onsets = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr)

        if len(onsets) < 3:
            return 1.0  # Not enough onsets to analyze

        # Calculate inter-onset intervals
        onset_times = librosa.frames_to_time(onsets, sr=sr)
        intervals = np.diff(onset_times)

        # Calculate rhythmic density
        duration = onset_times[-1] - onset_times[0]
        density = len(onsets) / duration if duration > 0 else 0

        # Normalize density to 0-1 range (typical fill density range: 1-8 notes per second)
        norm_density = min(1.0, density / 8.0)

        # Calculate variability in intervals
        interval_variability = np.std(intervals) / np.mean(intervals) if np.mean(intervals) > 0 else 0

        # Calculate dynamic variability
        onset_strengths = onset_env[onsets]
        dynamic_variability = np.std(onset_strengths) / np.mean(onset_strengths) if np.mean(onset_strengths) > 0 else 0

        # Check for pitch variations (potential multi-tom usage)
        has_pitch_variation = self._detect_multi_tom(y, sr)['multi_tom_detected']

        # Calculate rhythmic pattern complexity
        pattern_complexity = 0.5  # Default value

        if len(intervals) >= 2:
            # Look for patterns like accelerating/decelerating fills
            is_accelerating = all(intervals[i] > intervals[i + 1] for i in range(len(intervals) - 1))
            is_decelerating = all(intervals[i] < intervals[i + 1] for i in range(len(intervals) - 1))

            if is_accelerating or is_decelerating:
                pattern_complexity = 0.7

            # Check for more complex patterns like groupings
            groupings = []
            threshold = np.mean(intervals) * 0.2  # 20% threshold for grouping

            current_group = [intervals[0]]
            for i in range(1, len(intervals)):
                if abs(intervals[i] - intervals[i - 1]) < threshold:
                    current_group.append(intervals[i])
                else:
                    groupings.append(current_group)
                    current_group = [intervals[i]]

            if current_group:
                groupings.append(current_group)

            if len(groupings) > 1:
                pattern_complexity = 0.8

                # Check for alternating patterns
                if len(groupings) >= 3:
                    pattern_complexity = 0.9

        # Combine factors for overall complexity
        complexity = (
                norm_density * 0.3 +
                min(1.0, interval_variability) * 0.2 +
                min(1.0, dynamic_variability) * 0.2 +
                (1.0 if has_pitch_variation else 0.5) * 0.2 +
                pattern_complexity * 0.1
        )

        # Scale to 1-10 range
        complexity = 1.0 + (complexity * 9.0)

        return float(complexity)

    def _detect_multi_tom(self, y: np.ndarray, sr: int,
                          spec: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """
        Detect and analyze multi-tom patterns.

        Args:
            y: Audio data
            sr: Sample rate
            spec: Optional pre-computed spectrogram

        Returns:
            Dictionary with multi-tom analysis
        """
        # Detect onsets
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        onsets = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr, units='samples')

        if len(onsets) < 2:
            return {
                'multi_tom_detected': False,
                'tom_count': 1,
                'pattern_type': 'single'
            }

        # Extract onset segments for pitch analysis
        segments = []
        pitches = []

        for i, onset in enumerate(onsets):
            # Determine segment end (next onset or end of signal)
            if i < len(onsets) - 1:
                segment_end = onsets[i + 1]
            else:
                segment_end = len(y)

            # Use max 100ms segment
            segment_end = min(segment_end, onset + int(0.1 * sr))

            if segment_end > onset:
                segment = y[onset:segment_end]
                segments.append(segment)

                # Estimate pitch
                try:
                    # Simple pitch estimation
                    segment_pitch = self._estimate_segment_pitch(segment, sr)
                    pitches.append(segment_pitch)
                except Exception as e:
                    logger.debug(f"Error estimating segment pitch: {e}")
                    pitches.append(0)

        if len(pitches) < 2:
            return {
                'multi_tom_detected': False,
                'tom_count': 1,
                'pattern_type': 'single'
            }

        # Cluster pitches to identify distinct toms
        unique_toms = self._cluster_pitches(pitches)

        # Determine if multiple toms are used
        multi_tom = len(unique_toms) > 1

        if not multi_tom:
            return {
                'multi_tom_detected': False,
                'tom_count': 1,
                'pattern_type': 'single'
            }

        # Identify pattern type
        pattern_type = self._identify_pattern_type(unique_toms)

        return {
            'multi_tom_detected': True,
            'tom_count': len(unique_toms),
            'pattern_type': pattern_type
        }

    def _estimate_segment_pitch(self, segment: np.ndarray, sr: int) -> float:
        """
        Estimate the pitch of a short segment.

        Args:
            segment: Audio segment
            sr: Sample rate

        Returns:
            Estimated pitch in Hz
        """
        if len(segment) < 512:
            # Pad if too short
            segment = np.pad(segment, (0, 512 - len(segment)))

        # Apply bandpass filter to focus on typical tom frequencies
        lowcut = 60.0
        highcut = 300.0
        b, a = scipy.signal.butter(4, [lowcut / (sr / 2), highcut / (sr / 2)], 'band')
        filtered = scipy.signal.filtfilt(b, a, segment)

        # Calculate spectrum
        spec = np.abs(librosa.stft(filtered, n_fft=2048, hop_length=512))
        spec_sum = np.sum(spec, axis=1)

        # Find the peak
        if len(spec_sum) > 0:
            peak_idx = np.argmax(spec_sum)

            # Convert bin index to frequency
            peak_freq = peak_idx * sr / 2048

            # Sanity check for typical tom range
            if 60 <= peak_freq <= 300:
                return float(peak_freq)

        # Fallback
        return 150.0

    def _cluster_pitches(self, pitches: List[float]) -> List[float]:
        """
        Cluster pitches to identify distinct toms.

        Args:
            pitches: List of estimated pitches

        Returns:
            List of unique tom pitches
        """
        if not pitches:
            return []

        # Sort pitches
        sorted_pitches = sorted(pitches)

        # Find significant gaps to identify clusters
        clusters = []
        current_cluster = [sorted_pitches[0]]

        for i in range(1, len(sorted_pitches)):
            # If difference is more than 15% of previous pitch, consider it a different tom
            if sorted_pitches[i] - sorted_pitches[i - 1] > 0.15 * sorted_pitches[i - 1]:
                clusters.append(current_cluster)
                current_cluster = [sorted_pitches[i]]
            else:
                current_cluster.append(sorted_pitches[i])

        clusters.append(current_cluster)

        # Calculate mean pitch for each cluster
        unique_toms = [float(np.mean(cluster)) for cluster in clusters]

        return unique_toms

    def _identify_pattern_type(self, unique_toms: List[float]) -> str:
        """
        Identify the type of multi-tom pattern.

        Args:
            unique_toms: List of unique tom pitches

        Returns:
            Pattern type description
        """
        # Sort by pitch
        toms = sorted(unique_toms)

        if len(toms) == 2:
            return "high_low"
        elif len(toms) == 3:
            return "high_mid_low"
        elif len(toms) == 4:
            return "quad_toms"
        else:
            return f"multi_tom_{len(toms)}"