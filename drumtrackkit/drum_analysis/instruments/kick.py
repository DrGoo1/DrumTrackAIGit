# drum_analysis/instruments/kick.py

"""
Enhanced kick drum analyzer for the DrumTracKAI framework.

This module provides specialized analysis for kick drum sounds, with the ability to
detect various playing techniques, beater types, and pedal techniques.
"""

import numpy as np
import librosa
import scipy.signal
import logging
from typing import Dict, Any, Optional, Tuple, List

logger = logging.getLogger(__name__)


class KickAnalyzer:
    """
    Analyzer for kick drum samples.

    This class provides specialized analysis for kick drum sounds,
    including playing technique detection and pedal technique analysis.
    """

    def __init__(self):
        """Initialize the kick analyzer."""
        self.instrument_type = 'kick'

    def analyze(self, y: np.ndarray, sr: int, purpose: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze a kick drum sample.

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

        # Kick-specific features
        features['low_end_energy'] = float(self._calculate_low_end_energy(spec))
        features['attack_sharpness'] = float(self._calculate_attack_sharpness(y, sr))

        # Detect playing technique
        technique, confidence = self._detect_playing_technique(y, sr, spec)
        features['playing_technique'] = technique
        features['technique_confidence'] = float(confidence)

        # Detect beater type
        beater_type, confidence = self._detect_beater_type(y, sr, spec)
        features['beater_type'] = beater_type
        features['beater_confidence'] = float(confidence)

        # Add technique-specific features
        if technique == 'buried':
            features['burial_depth'] = self._calculate_burial_depth(y, sr)
        elif technique == 'rebound':
            features['rebound_quality'] = self._calculate_rebound_quality(y, sr)

        # Add purpose-specific features
        if purpose == 'sonic_reference':
            features['resonance_length'] = self._calculate_resonance_length(y, sr)
            features['tone_fullness'] = self._calculate_tone_fullness(y, sr, spec)
        elif purpose == 'technique_training':
            features['consistency'] = self._analyze_consistency(y, sr)
            features['double_pedal_detection'] = self._detect_double_pedal(y, sr)
        elif purpose == 'style_examples':
            features['pattern_complexity'] = self._analyze_pattern_complexity(y, sr)
            features['dynamic_pattern'] = self._analyze_dynamic_pattern(y, sr)

        return features

    def _calculate_low_end_energy(self, spec: np.ndarray) -> float:
        """
        Calculate the amount of low-frequency energy.

        Args:
            spec: Spectrogram

        Returns:
            Low end energy ratio (0.0 to 1.0)
        """
        # Sum across time
        spec_sum = np.sum(spec, axis=1)

        # Calculate the ratio of energy below 200Hz
        low_idx = int(len(spec_sum) * 0.1)  # Approximate for 200Hz

        low_energy = np.sum(spec_sum[:low_idx])
        total_energy = np.sum(spec_sum)

        if total_energy > 0:
            return float(low_energy / total_energy)
        else:
            return 0.0

    def _calculate_attack_sharpness(self, y: np.ndarray, sr: int) -> float:
        """
        Calculate how sharp the attack is.

        Args:
            y: Audio data
            sr: Sample rate

        Returns:
            Attack sharpness score (0.0 to 1.0)
        """
        # Get envelope
        env = np.abs(y)

        # Find peak
        peak_idx = np.argmax(env)
        peak_amp = env[peak_idx]

        if peak_idx == 0 or peak_amp == 0:
            return 0.0

        # Calculate the duration of the attack (time to reach peak from 10% of peak)
        attack_threshold = peak_amp * 0.1
        attack_start_idx = 0

        for i in range(peak_idx - 1, 0, -1):
            if env[i] < attack_threshold:
                attack_start_idx = i
                break

        attack_duration = (peak_idx - attack_start_idx) / sr

        if attack_duration == 0:
            return 1.0  # Immediate attack (sharpest)

        # Calculate the slope of the attack
        attack_slope = (peak_amp - env[attack_start_idx]) / attack_duration

        # Normalize to 0-1 range (higher = sharper)
        normalized_slope = min(1.0, attack_slope / (peak_amp * 100))

        return float(normalized_slope)

    def _detect_playing_technique(self, y: np.ndarray, sr: int,
                                  spec: Optional[np.ndarray] = None) -> Tuple[str, float]:
        """
        Detect the playing technique used on the kick drum.

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
        env = np.abs(y)
        peak_idx = np.argmax(env)
        peak_amp = env[peak_idx]

        # Calculate attack time and decay rate
        attack_time = self._calculate_attack_time(y, sr)
        decay_rate = self._calculate_decay_rate(env)

        # Calculate low frequency content
        low_end = self._calculate_low_end_energy(spec)

        # Calculate sustain length
        sustain_length = self._calculate_sustain_length(y, sr)

        # Buried beater characteristics:
        # - Shorter sustain (damped)
        # - Less pronounced attack
        # - More controlled low end
        buried_score = (
                (1.0 if sustain_length < 0.4 else 0.5) +  # Shorter sustain
                (1.0 if attack_time > 0.01 else 0.5) +  # Less sharp attack
                (1.0 if decay_rate > 5.0 else 0.5) +  # Faster decay
                (1.0 if 0.4 < low_end < 0.7 else 0.5)  # Controlled low end
        )

        # Rebound technique characteristics:
        # - Longer sustain
        # - Sharper attack
        # - More low-end resonance
        rebound_score = (
                (1.0 if sustain_length > 0.4 else 0.5) +  # Longer sustain
                (1.0 if attack_time < 0.01 else 0.5) +  # Sharper attack
                (1.0 if decay_rate < 5.0 else 0.5) +  # Slower decay
                (1.0 if low_end > 0.6 else 0.5)  # More low end
        )

        # Heel-down characteristics:
        # - Less power
        # - More controlled attack
        # - More mid/high frequencies
        heel_down_score = (
                (1.0 if peak_amp < 0.7 else 0.5) +  # Less power
                (1.0 if attack_time > 0.015 else 0.5) +  # More controlled attack
                (1.0 if low_end < 0.6 else 0.5) +  # Less low end
                (1.0 if decay_rate > 4.0 else 0.5)  # Faster decay
        )

        # Heel-up characteristics:
        # - More power
        # - Sharper attack
        # - More low-end
        heel_up_score = (
                (1.0 if peak_amp > 0.7 else 0.5) +  # More power
                (1.0 if attack_time < 0.015 else 0.5) +  # Sharper attack
                (1.0 if low_end > 0.6 else 0.5) +  # More low end
                (1.0 if decay_rate < 4.0 else 0.5)  # Slower decay (more resonance)
        )

        # Determine technique based on highest score
        scores = {
            'buried': buried_score,
            'rebound': rebound_score,
            'heel_down': heel_down_score,
            'heel_up': heel_up_score
        }

        technique = max(scores, key=scores.get)
        max_score = scores[technique]

        # Convert score to confidence (4 questions, each worth 1 point, max total = 4)
        confidence = max_score / 4

        return technique, confidence

    def _detect_beater_type(self, y: np.ndarray, sr: int,
                            spec: Optional[np.ndarray] = None) -> Tuple[str, float]:
        """
        Detect the type of beater used on the kick drum.

        Args:
            y: Audio data
            sr: Sample rate
            spec: Optional pre-computed spectrogram

        Returns:
            Tuple of (beater_type, confidence)
        """
        # Compute spectral features if not provided
        if spec is None:
            spec = np.abs(librosa.stft(y))

        # Extract spectral features
        spectral_centroid = np.mean(librosa.feature.spectral_centroid(S=spec, sr=sr))
        spectral_contrast = np.mean(librosa.feature.spectral_contrast(S=spec, sr=sr))

        # Calculate attack characteristics
        attack_sharpness = self._calculate_attack_sharpness(y, sr)

        # Calculate frequency band distribution
        band_energies = self._calculate_band_energies(spec)
        low_ratio = band_energies['low'] / band_energies['total'] if band_energies['total'] > 0 else 0
        mid_ratio = band_energies['mid'] / band_energies['total'] if band_energies['total'] > 0 else 0
        high_ratio = band_energies['high'] / band_energies['total'] if band_energies['total'] > 0 else 0

        # Felt beater characteristics:
        # - Softer attack
        # - More low/mid frequencies
        # - Less high-end
        felt_score = (
                (1.0 if attack_sharpness < 0.6 else 0.5) +  # Softer attack
                (1.0 if spectral_centroid < 500 else 0.5) +  # Lower spectral centroid
                (1.0 if high_ratio < 0.1 else 0.5) +  # Less high frequency content
                (1.0 if low_ratio > 0.7 else 0.5)  # More low frequency content
        )

        # Plastic/wood beater characteristics:
        # - Sharper attack
        # - More balanced frequency distribution
        # - More high-end click
        plastic_score = (
                (1.0 if attack_sharpness > 0.6 else 0.5) +  # Sharper attack
                (1.0 if spectral_centroid > 500 else 0.5) +  # Higher spectral centroid
                (1.0 if high_ratio > 0.1 else 0.5) +  # More high frequency content
                (1.0 if mid_ratio > 0.2 else 0.5)  # More mid frequency content
        )

        # Determine beater type based on highest score
        scores = {
            'felt': felt_score,
            'plastic': plastic_score
        }

        beater_type = max(scores, key=scores.get)
        max_score = scores[beater_type]

        # Convert score to confidence (4 questions, each worth 1 point, max total = 4)
        confidence = max_score / 4

        return beater_type, confidence

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

        # Find peak
        peak_idx = np.argmax(env)

        if peak_idx >= len(env) - 1:
            return 0.0

        # Extract decay portion
        decay = env[peak_idx:]

        if len(decay) < 2:
            return 0.0

        try:
            # Estimate decay rate using exponential fit
            time = np.arange(len(decay))
            log_decay = np.log(decay + 1e-10)  # Avoid log(0)

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

    def _calculate_band_energies(self, spec: np.ndarray) -> Dict[str, float]:
        """
        Calculate energy in different frequency bands.

        Args:
            spec: Spectrogram

        Returns:
            Dictionary with energy in different bands
        """
        # Sum across time
        spec_sum = np.sum(spec, axis=1)

        # Calculate band boundaries (these are bin indices, not actual frequencies)
        low_idx = int(len(spec_sum) * 0.1)  # Low frequencies
        mid_idx = int(len(spec_sum) * 0.4)  # Mid frequencies

        # Calculate energies
        low_energy = np.sum(spec_sum[:low_idx])
        mid_energy = np.sum(spec_sum[low_idx:mid_idx])
        high_energy = np.sum(spec_sum[mid_idx:])
        total_energy = low_energy + mid_energy + high_energy

        return {
            'low': float(low_energy),
            'mid': float(mid_energy),
            'high': float(high_energy),
            'total': float(total_energy)
        }

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

    def _calculate_burial_depth(self, y: np.ndarray, sr: int) -> float:
        """
        Calculate how deeply the beater is buried into the head.

        Args:
            y: Audio data
            sr: Sample rate

        Returns:
            Burial depth score (0.0 to 1.0)
        """
        # Burial depth affects:
        # - Decay rate (faster = deeper burial)
        # - Sustain length (shorter = deeper burial)
        # - Low-end resonance (less = deeper burial)

        # Calculate decay rate
        env = np.abs(y)
        decay_rate = self._calculate_decay_rate(env)

        # Calculate sustain length
        sustain_length = self._calculate_sustain_length(y, sr)

        # Calculate low-end resonance
        spec = np.abs(librosa.stft(y))
        low_end = self._calculate_low_end_energy(spec)

        # Calculate burial depth based on these factors
        # Normalize each factor to 0-1 range where 1 = deeper burial

        # Decay rate: Faster decay (higher value) indicates deeper burial
        decay_factor = min(1.0, decay_rate / 10.0)

        # Sustain: Shorter sustain indicates deeper burial
        sustain_factor = 1.0 - min(1.0, sustain_length / 0.8)

        # Low-end: Less low-end resonance indicates deeper burial
        resonance_factor = 1.0 - min(1.0, low_end / 0.8)

        # Combine factors
        burial_depth = (decay_factor * 0.4) + (sustain_factor * 0.4) + (resonance_factor * 0.2)

        return float(burial_depth)

    def _calculate_rebound_quality(self, y: np.ndarray, sr: int) -> float:
        """
        Calculate the quality of beater rebound.

        Args:
            y: Audio data
            sr: Sample rate

        Returns:
            Rebound quality score (0.0 to 1.0)
        """
        # Good rebound characteristics:
        # - Good sustain
        # - Natural decay profile
        # - Rich low end resonance

        # Calculate sustain length
        sustain_length = self._calculate_sustain_length(y, sr)

        # Calculate decay profile naturalness
        env = np.abs(y)
        decay_rate = self._calculate_decay_rate(env)

        # Ideal decay rate for natural kick drum
        decay_factor = 1.0 - min(1.0, abs(decay_rate - 3.0) / 3.0)

        # Calculate low-end resonance
        spec = np.abs(librosa.stft(y))
        low_end = self._calculate_low_end_energy(spec)

        # Combine factors
        rebound_quality = (
                (min(1.0, sustain_length / 0.6) * 0.4) +  # Normalize sustain length
                (decay_factor * 0.3) +  # Decay profile
                (min(1.0, low_end / 0.7) * 0.3)  # Low-end resonance
        )

        return float(rebound_quality)

    def _calculate_resonance_length(self, y: np.ndarray, sr: int) -> float:
        """
        Calculate the resonance length of the kick drum.

        Args:
            y: Audio data
            sr: Sample rate

        Returns:
            Resonance length in seconds
        """
        # This is similar to sustain length but focused on the low frequency components

        # Filter to emphasize low frequencies
        b, a = scipy.signal.butter(4, 200 / (sr / 2), 'low')
        y_low = scipy.signal.filtfilt(b, a, y)

        # Get envelope of low frequency content
        env_low = np.abs(y_low)

        # Find peak
        peak_idx = np.argmax(env_low)
        peak_amp = env_low[peak_idx]

        if peak_idx >= len(env_low) - 1 or peak_amp == 0:
            return 0.0

        # Find where amplitude drops to 10% of peak
        threshold = peak_amp * 0.1
        end_idx = len(env_low)

        for i in range(peak_idx, len(env_low)):
            if env_low[i] < threshold:
                end_idx = i
                break

        resonance_length = (end_idx - peak_idx) / sr

        return float(resonance_length)

    def _calculate_tone_fullness(self, y: np.ndarray, sr: int, spec: np.ndarray) -> float:
        """
        Calculate the fullness of the kick drum tone.

        Args:
            y: Audio data
            sr: Sample rate
            spec: Spectrogram

        Returns:
            Tone fullness score (0.0 to 1.0)
        """
        # Full kick tone has:
        # - Good low-end
        # - Appropriate mid punch
        # - Balanced high-end click
        # - Natural decay profile

        # Calculate frequency band distribution
        band_energies = self._calculate_band_energies(spec)
        low_ratio = band_energies['low'] / band_energies['total'] if band_energies['total'] > 0 else 0
        mid_ratio = band_energies['mid'] / band_energies['total'] if band_energies['total'] > 0 else 0
        high_ratio = band_energies['high'] / band_energies['total'] if band_energies['total'] > 0 else 0

        # Ideal kick drum frequency distribution
        low_factor = 1.0 - min(1.0, abs(low_ratio - 0.6) / 0.6)
        mid_factor = 1.0 - min(1.0, abs(mid_ratio - 0.3) / 0.3)
        high_factor = 1.0 - min(1.0, abs(high_ratio - 0.1) / 0.1)

        # Calculate decay profile naturalness
        env = np.abs(y)
        decay_rate = self._calculate_decay_rate(env)

        # Ideal decay rate for natural kick drum
        decay_factor = 1.0 - min(1.0, abs(decay_rate - 3.0) / 3.0)

        # Combine factors
        fullness = (
                (low_factor * 0.5) +  # Low-end balance
                (mid_factor * 0.2) +  # Mid-range punch
                (high_factor * 0.1) +  # High-end click
                (decay_factor * 0.2)  # Natural decay
        )

        return float(fullness)

    def _analyze_consistency(self, y: np.ndarray, sr: int) -> float:
        """
        Analyze the consistency of kick drum hits.

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

        # Calculate spectral consistency
        spectral_consistency = 0.8  # Default value

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
                        spectral_consistency = float(np.mean(similarities))
        except Exception as e:
            logger.debug(f"Error calculating spectral consistency: {e}")

        # Combine factors
        consistency = (timing_consistency * 0.5) + (dynamic_consistency * 0.3) + (spectral_consistency * 0.2)

        return float(consistency)

    def _detect_double_pedal(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """
        Detect and analyze double pedal usage.

        Args:
            y: Audio data
            sr: Sample rate

        Returns:
            Dictionary with double pedal analysis
        """
        # Features suggesting double pedal:
        # - Very rapid succession of kicks
        # - Slight timbral differences between alternating hits
        # - Specific rhythm patterns

        # Detect onsets
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        onsets = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr)

        if len(onsets) < 4:  # Need multiple hits to analyze
            return {
                'double_pedal_detected': False,
                'confidence': 0.0,
                'speed': 0.0,
                'evenness': 0.0
            }

        # Calculate inter-onset intervals
        onset_times = librosa.frames_to_time(onsets, sr=sr)
        intervals = np.diff(onset_times)

        # Check for very rapid intervals (double pedal typically allows faster playing)
        # Typical threshold: 16th notes at 180+ BPM = intervals < 0.08s
        rapid_intervals = np.sum(intervals < 0.08)
        rapid_ratio = rapid_intervals / len(intervals)

        # Check for alternating pattern in dynamics or timbre
        onset_strengths = onset_env[onsets]

        # Calculate alternating pattern score
        alternating_score = 0.0

        if len(onset_strengths) >= 4:
            # Check for pattern in dynamics (like strong-weak-strong-weak)
            odd_indices = np.arange(0, len(onset_strengths), 2)
            even_indices = np.arange(1, len(onset_strengths), 2)

            if len(odd_indices) > 0 and len(even_indices) > 0:
                odd_mean = np.mean(onset_strengths[odd_indices])
                even_mean = np.mean(onset_strengths[even_indices])

                # Calculate ratio between odd and even hits
                dynamic_ratio = abs(odd_mean - even_mean) / max(odd_mean, even_mean)

                # Higher ratio suggests more alternating pattern
                alternating_score = min(1.0, dynamic_ratio * 3)

        # Calculate speed (BPM) based on the intervals
        if len(intervals) > 0:
            # Convert to BPM (beats per minute)
            # Assuming intervals represent 8th notes or 16th notes
            bpm_8th = 60 / np.median(intervals) / 2
            bpm_16th = 60 / np.median(intervals) / 4

            # Choose the most reasonable BPM (typically between 60-240)
            if 60 <= bpm_8th <= 240:
                bpm = bpm_8th
            elif 60 <= bpm_16th <= 240:
                bpm = bpm_16th
            else:
                bpm = 120  # Default fallback
        else:
            bpm = 120

        # Calculate evenness of intervals
        evenness = 1.0 - min(1.0, np.std(intervals) / np.mean(intervals))

        # Combine factors to determine if double pedal is being used
        double_pedal_score = (rapid_ratio * 0.6) + (alternating_score * 0.4)
        double_pedal_detected = double_pedal_score > 0.4  # Threshold

        return {
            'double_pedal_detected': bool(double_pedal_detected),
            'confidence': float(double_pedal_score),
            'speed': float(bpm),
            'evenness': float(evenness)
        }

    def _analyze_pattern_complexity(self, y: np.ndarray, sr: int) -> float:
        """
        Analyze the complexity of a kick drum pattern.

        Args:
            y: Audio data
            sr: Sample rate

        Returns:
            Pattern complexity score (1.0 to 10.0)
        """
        # Extract onset pattern
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        onsets = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr)

        if len(onsets) < 3:
            return 1.0  # Not enough onsets to analyze

        # Calculate inter-onset intervals
        onset_times = librosa.frames_to_time(onsets, sr=sr)
        intervals = np.diff(onset_times)

        # Estimate tempo
        if len(intervals) > 0:
            tempo = 60 / np.median(intervals)

            # Normalize to reasonable range
            tempo = max(min(tempo, 240), 40)

            # Calculate beat duration
            beat_duration = 60 / tempo
        else:
            beat_duration = 0.5  # Default (120 BPM)

        # Convert onset times to beat positions
        beat_positions = onset_times / beat_duration

        # Quantize to 16th notes
        quantized_positions = np.round(beat_positions * 4) / 4

        # Count unique positions within a bar (assume 4/4 time)
        unique_positions = set()
        for pos in quantized_positions:
            bar_position = pos % 4  # Position within a 4-beat bar
            unique_positions.add(bar_position)

        # Calculate rhythmic density
        density = len(unique_positions) / 16  # 16 16th-notes in a 4/4 bar

        # Calculate syncopation score
        syncopation = 0.0
        for pos in unique_positions:
            # Check if position is on an off-beat
            is_off_beat = not (pos * 4).is_integer()  # Not on a quarter note

            if is_off_beat:
                syncopation += 0.1  # Increase syncopation score for each off-beat hit

        # Combine factors
        complexity = 1.0 + (density * 5) + (syncopation * 4)

        return float(min(10.0, complexity))

    def _analyze_dynamic_pattern(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """
        Analyze the dynamic pattern of kick hits.

        Args:
            y: Audio data
            sr: Sample rate

        Returns:
            Dictionary with dynamic pattern analysis
        """
        # Extract onset pattern
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        onsets = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr)

        if len(onsets) < 3:
            return {
                'dynamic_range': 0.0,
                'pattern_type': 'constant',
                'ghost_note_count': 0
            }

        # Get onset strengths
        onset_strengths = onset_env[onsets]

        # Calculate dynamic range
        if len(onset_strengths) > 0:
            min_strength = np.min(onset_strengths)
            max_strength = np.max(onset_strengths)

            if max_strength > 0:
                dynamic_range = (max_strength - min_strength) / max_strength
            else:
                dynamic_range = 0.0
        else:
            dynamic_range = 0.0

        # Normalize strengths
        if max_strength > 0:
            norm_strengths = onset_strengths / max_strength
        else:
            norm_strengths = onset_strengths

        # Count ghost notes (very quiet hits, < 30% of max)
        ghost_count = np.sum(norm_strengths < 0.3)

        # Detect pattern type
        if dynamic_range < 0.2:
            pattern_type = 'constant'
        elif np.std(norm_strengths) < 0.2:
            pattern_type = 'gradual'
        else:
            # Check for alternating pattern
            alternating = True
            for i in range(2, len(norm_strengths)):
                if abs(norm_strengths[i] - norm_strengths[i - 2]) > 0.3:
                    alternating = False
                    break

            if alternating:
                pattern_type = 'alternating'
            else:
                pattern_type = 'varied'

        return {
            'dynamic_range': float(dynamic_range),
            'pattern_type': pattern_type,
            'ghost_note_count': int(ghost_count)
        }