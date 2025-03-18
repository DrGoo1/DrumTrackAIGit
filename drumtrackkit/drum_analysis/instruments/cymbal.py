# drum_analysis/instruments/cymbal.py

"""
Enhanced cymbal analyzer for the DrumTracKAI framework.

This module provides specialized analysis for cymbal sounds, with the ability to
differentiate between different cymbal types (hi-hat, ride, crash) and detect
various articulations.
"""

import numpy as np
import librosa
import scipy.signal
import logging
from typing import Dict, Any, Optional, Tuple, List

logger = logging.getLogger(__name__)


class CymbalAnalyzer:
    """
    Analyzer for cymbal drum samples.

    This class provides specialized analysis for cymbal drum sounds,
    including hi-hat, ride, and crash cymbal differentiation.
    """

    def __init__(self):
        """Initialize the cymbal analyzer."""
        self.instrument_type = 'cymbal'

    def analyze(self, y: np.ndarray, sr: int, purpose: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze a cymbal drum sample.

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

        # Spectral features for cymbal analysis
        spec = np.abs(librosa.stft(y))

        # Compute overall spectral features
        features['spectral_centroid'] = float(np.mean(librosa.feature.spectral_centroid(S=spec, sr=sr)))
        features['spectral_bandwidth'] = float(np.mean(librosa.feature.spectral_bandwidth(S=spec, sr=sr)))
        features['spectral_rolloff'] = float(np.mean(librosa.feature.spectral_rolloff(S=spec, sr=sr)))
        features['spectral_flatness'] = float(np.mean(librosa.feature.spectral_flatness(y=y)))

        # High frequency content is particularly important for cymbals
        features['high_frequency_content'] = float(np.sum(spec[int(len(spec) * 0.6):]) / np.sum(spec))

        # Calculate sustain length - time until decay to 10% of peak amplitude
        peak_idx = np.argmax(np.abs(y))
        peak_amp = np.abs(y[peak_idx])
        threshold = peak_amp * 0.1

        # Find where amplitude falls below threshold
        decay_idx = len(y)
        for i in range(peak_idx, len(y)):
            if np.abs(y[i]) < threshold:
                decay_idx = i
                break

        features['sustain_length'] = float((decay_idx - peak_idx) / sr)

        # Detect cymbal type and articulation
        cymbal_type, articulation = self._detect_cymbal_type(y, sr, spec)
        features['cymbal_type'] = cymbal_type

        # Add articulation information based on cymbal type
        if cymbal_type == 'hihat':
            features['hihat_state'] = articulation
        elif cymbal_type == 'ride':
            features['ride_articulation'] = articulation
        elif cymbal_type == 'crash':
            features['crash_articulation'] = articulation

        # Add purpose-specific features
        if purpose == 'sonic_reference':
            features['ping_detection'] = self._detect_ping(y, sr)
            features['clarity_score'] = self._calculate_clarity_score(y, sr, spec)
        elif purpose == 'technique_training':
            features['consistency'] = self._analyze_consistency(y, sr)
            features['decay_profile'] = self._analyze_decay_profile(y, sr)
        elif purpose == 'style_examples':
            features['pattern_complexity'] = self._analyze_pattern_complexity(y, sr)

            # Detect multiple instruments in a track
            if self._is_multi_instrument_track(y, sr):
                features['instruments_detected'] = self._detect_instruments(y, sr)

        return features

    def _detect_cymbal_type(self, y: np.ndarray, sr: int,
                            spec: Optional[np.ndarray] = None) -> Tuple[str, str]:
        """
        Detect the type of cymbal and its articulation.

        Args:
            y: Audio data
            sr: Sample rate
            spec: Optional pre-computed spectrogram

        Returns:
            Tuple of (cymbal_type, articulation)
        """
        # Compute spectral features if not provided
        if spec is None:
            spec = np.abs(librosa.stft(y))

        # Extract key features for classification
        spectral_centroid = np.mean(librosa.feature.spectral_centroid(S=spec, sr=sr))
        spectral_bandwidth = np.mean(librosa.feature.spectral_bandwidth(S=spec, sr=sr))
        spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(S=spec, sr=sr))

        # Duration features
        duration = len(y) / sr

        # Envelope features
        env = np.abs(y)
        peak_idx = np.argmax(env)
        decay_rate = self._calculate_decay_rate(env[peak_idx:])

        # Frequency band energy distribution
        band_energies = self._calculate_band_energies(spec)
        low_ratio = band_energies['low'] / band_energies['total']
        mid_ratio = band_energies['mid'] / band_energies['total']
        high_ratio = band_energies['high'] / band_energies['total']

        # Attack characteristics
        attack_strength = self._calculate_attack_strength(y, sr)

        # Onset detection for pattern analysis
        onsets = librosa.onset.onset_detect(y=y, sr=sr)
        onset_count = len(onsets)

        # Classify cymbal type using the features

        # Hi-hat characteristics:
        # - Usually shorter duration
        # - High spectral centroid
        # - Fast decay rate
        # - Often has more defined attacks
        hihat_score = (
                (1.0 if duration < 1.0 else 0.5) +  # Shorter duration
                (1.0 if spectral_centroid > 4000 else 0.5) +  # Higher frequencies
                (1.0 if decay_rate > 5.0 else 0.5) +  # Fast decay
                (1.0 if attack_strength > 0.7 else 0.5) +  # Strong attack
                (1.0 if high_ratio > 0.5 else 0.5)  # More high frequency content
        )

        # Ride characteristics:
        # - Medium-long duration
        # - Strong mid-range frequencies
        # - More sustain than hi-hat
        # - Often has distinct "ping" sound
        ride_score = (
                (1.0 if 0.8 < duration < 2.5 else 0.5) +  # Medium duration
                (1.0 if 2500 < spectral_centroid < 5000 else 0.5) +  # Mid-high frequencies
                (1.0 if 2.0 < decay_rate < 6.0 else 0.5) +  # Medium decay
                (1.0 if self._detect_ping(y, sr) > 0.6 else 0.5) +  # Ping sound
                (1.0 if mid_ratio > 0.3 and high_ratio > 0.3 else 0.5)  # Balanced frequency distribution
        )

        # Crash characteristics:
        # - Longer duration
        # - Broad spectral bandwidth
        # - Slower decay rate
        # - Strong initial attack followed by wash
        crash_score = (
                (1.0 if duration > 1.5 else 0.5) +  # Longer duration
                (1.0 if spectral_bandwidth > 2000 else 0.5) +  # Wide bandwidth
                (1.0 if decay_rate < 3.0 else 0.5) +  # Slow decay
                (1.0 if attack_strength > 0.8 else 0.5) +  # Very strong attack
                (1.0 if high_ratio > 0.4 and mid_ratio > 0.3 else 0.5)  # Strong across mid-high frequencies
        )

        # Determine cymbal type based on highest score
        scores = {
            'hihat': hihat_score,
            'ride': ride_score,
            'crash': crash_score
        }

        cymbal_type = max(scores, key=scores.get)

        # Determine articulation based on cymbal type
        articulation = 'normal'  # Default articulation

        if cymbal_type == 'hihat':
            # Determine hi-hat state
            if duration < 0.2 and decay_rate > 8.0:
                articulation = 'closed'
            elif duration > 0.5 and decay_rate < 4.0:
                articulation = 'open'
            elif attack_strength < 0.5:
                articulation = 'pedal'
            else:
                articulation = 'half_open'

        elif cymbal_type == 'ride':
            # Determine if it's a bell hit
            if spectral_centroid > 4500 and mid_ratio < 0.25:
                articulation = 'bell'
            elif self._detect_ping(y, sr) > 0.8:
                articulation = 'ping'
            else:
                articulation = 'normal'

        elif cymbal_type == 'crash':
            # Determine if it's choked
            if duration < 1.0 and self._detect_sudden_decay(y, sr):
                articulation = 'choke'
            elif duration > 2.5:
                articulation = 'wash'
            elif attack_strength > 0.9:
                articulation = 'accent'
            else:
                articulation = 'normal'

        return cymbal_type, articulation

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
        low_idx = int(len(spec_sum) * 0.15)  # Low frequencies
        mid_idx = int(len(spec_sum) * 0.45)  # Mid frequencies

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

    def _calculate_decay_rate(self, signal: np.ndarray) -> float:
        """
        Calculate the decay rate of a signal.

        Args:
            signal: Audio data starting from the peak

        Returns:
            Decay rate (higher value means faster decay)
        """
        if len(signal) < 2:
            return 0.0

        # Smooth the signal to reduce noise
        window_size = min(1024, len(signal) // 10)
        if window_size < 2:
            window_size = 2

        smoothed = np.convolve(signal, np.ones(window_size) / window_size, mode='valid')

        if len(smoothed) < 2:
            return 0.0

        # Estimate decay rate from amplitude envelope
        try:
            # Use logarithmic decay model
            log_envelope = np.log(smoothed + 1e-10)  # Avoid log(0)
            time = np.arange(len(log_envelope))

            # Linear regression to estimate decay rate
            if len(time) > 1:
                polyfit = np.polyfit(time, log_envelope, 1)
                decay_rate = -polyfit[0]  # Negative slope of log envelope
                return float(decay_rate * 10000)  # Scale for readability
            else:
                return 0.0
        except Exception as e:
            logger.warning(f"Error calculating decay rate: {e}")
            return 0.0

    def _calculate_attack_strength(self, y: np.ndarray, sr: int) -> float:
        """
        Calculate the attack strength.

        Args:
            y: Audio data
            sr: Sample rate

        Returns:
            Attack strength (0.0 to 1.0)
        """
        # Get envelope
        env = np.abs(y)

        # Find peak
        peak_idx = np.argmax(env)
        peak_amp = env[peak_idx]

        if peak_idx == 0 or peak_amp == 0:
            return 0.0

        # Calculate the duration of the attack (time to reach 80% of peak)
        attack_threshold = peak_amp * 0.2  # Start measuring from 20% of peak
        attack_start_idx = 0

        for i in range(peak_idx - 1, 0, -1):
            if env[i] < attack_threshold:
                attack_start_idx = i
                break

        attack_duration = (peak_idx - attack_start_idx) / sr

        if attack_duration == 0:
            return 1.0  # Immediate attack (strongest)

        # Calculate the slope of the attack
        attack_slope = (peak_amp - env[attack_start_idx]) / (attack_duration + 1e-10)

        # Normalize to 0-1 range
        normalized_slope = min(1.0, attack_slope / (peak_amp * 5))

        return float(normalized_slope)

    def _detect_ping(self, y: np.ndarray, sr: int) -> float:
        """
        Detect the "ping" sound characteristic of ride cymbals.

        Args:
            y: Audio data
            sr: Sample rate

        Returns:
            Ping score (0.0 to 1.0)
        """
        # A ping is characterized by a strong attack followed by a specific
        # frequency distribution with prominent mid-high frequencies

        # Get spectrogram
        spec = np.abs(librosa.stft(y))

        # Focus on the attack portion
        attack_duration = min(0.05, len(y) / sr)  # 50ms or less
        attack_frames = int(attack_duration * sr / 512) + 1  # Convert to STFT frames

        if attack_frames >= spec.shape[1]:
            attack_frames = spec.shape[1] - 1

        attack_spec = spec[:, :attack_frames]

        if attack_spec.size == 0:
            return 0.0

        # Calculate spectral features of the attack
        try:
            # Look for strong mid-high frequencies (3-8kHz) relative to other frequencies
            mid_high_bins = slice(int(3000 / sr * spec.shape[0]), int(8000 / sr * spec.shape[0]))
            mid_high_energy = np.sum(attack_spec[mid_high_bins, :])
            total_energy = np.sum(attack_spec)

            if total_energy == 0:
                return 0.0

            mid_high_ratio = mid_high_energy / total_energy

            # Check for spectral peakiness (characteristic of the metallic ping)
            spectral_contrast = np.mean(librosa.feature.spectral_contrast(S=attack_spec, sr=sr))

            # Combine factors
            ping_score = (mid_high_ratio * 0.5) + (min(1.0, spectral_contrast / 5) * 0.5)

            return float(ping_score)
        except Exception as e:
            logger.warning(f"Error in ping detection: {e}")
            return 0.0

    def _detect_sudden_decay(self, y: np.ndarray, sr: int) -> bool:
        """
        Detect if there's a sudden decay in the signal (e.g., choked cymbal).

        Args:
            y: Audio data
            sr: Sample rate

        Returns:
            True if a sudden decay is detected
        """
        # Get amplitude envelope
        env = np.abs(y)

        # Find peak
        peak_idx = np.argmax(env)

        if peak_idx >= len(y) - 1:
            return False

        # Look for a sharp drop in amplitude after the peak
        # Calculate the decay rate in small windows
        window_size = int(0.05 * sr)  # 50ms windows

        if window_size < 2 or peak_idx + window_size >= len(y):
            return False

        try:
            decay_rates = []
            for i in range(peak_idx, len(y) - window_size, window_size):
                start_amp = np.mean(env[i:i + 10])
                end_amp = np.mean(env[i + window_size - 10:i + window_size])

                if start_amp > 0:
                    decay = (start_amp - end_amp) / start_amp
                    decay_rates.append(decay)

            if not decay_rates:
                return False

            # Check for a sudden large decay rate
            max_decay = max(decay_rates)

            return max_decay > 0.5  # Arbitrary threshold for "sudden" decay
        except Exception as e:
            logger.warning(f"Error in sudden decay detection: {e}")
            return False

    def _calculate_clarity_score(self, y: np.ndarray, sr: int, spec: np.ndarray) -> float:
        """Calculate clarity score for the cymbal sound."""
        # Higher contrast and lower flatness indicate more clarity
        contrast = np.mean(librosa.feature.spectral_contrast(S=spec, sr=sr))
        flatness = np.mean(librosa.feature.spectral_flatness(y=y))

        clarity_score = (contrast * 5) * (1 - flatness)
        return float(min(10.0, clarity_score))

    def _analyze_consistency(self, y: np.ndarray, sr: int) -> float:
        """Analyze timing consistency for technique training."""
        # Detect onsets
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        onsets = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr, units='time')

        if len(onsets) < 3:
            return 1.0  # Not enough onsets to analyze

        # Calculate inter-onset intervals
        iois = np.diff(onsets)

        # Calculate coefficient of variation (lower is more consistent)
        cv = np.std(iois) / np.mean(iois) if np.mean(iois) > 0 else 0

        # Convert to a consistency score (1-10, higher is better)
        consistency = 10 * (1 - min(cv, 1))
        return float(consistency)

    def _analyze_decay_profile(self, y: np.ndarray, sr: int) -> Dict[str, float]:
        """Analyze the decay profile of the cymbal."""
        # Get envelope
        env = np.abs(y)

        # Find peak
        peak_idx = np.argmax(env)
        peak_amp = env[peak_idx]

        if peak_idx >= len(y) - 1 or peak_amp == 0:
            return {'initial_decay': 0.0, 'sustain': 0.0, 'tail': 0.0}

        # Calculate time to decay to different percentages of peak
        decay_80_idx = len(y)
        decay_50_idx = len(y)
        decay_20_idx = len(y)

        for i in range(peak_idx, len(y)):
            if env[i] < peak_amp * 0.8 and decay_80_idx == len(y):
                decay_80_idx = i
            elif env[i] < peak_amp * 0.5 and decay_50_idx == len(y):
                decay_50_idx = i
            elif env[i] < peak_amp * 0.2 and decay_20_idx == len(y):
                decay_20_idx = i
                break

        # Convert to times
        initial_decay = (decay_80_idx - peak_idx) / sr
        sustain = (decay_50_idx - decay_80_idx) / sr
        tail = (decay_20_idx - decay_50_idx) / sr

        return {
            'initial_decay': float(initial_decay),
            'sustain': float(sustain),
            'tail': float(tail)
        }

    def _analyze_pattern_complexity(self, y: np.ndarray, sr: int) -> float:
        """Analyze the complexity of a rhythmic pattern."""
        # Detect onsets
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        onsets = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr, units='time')

        if len(onsets) < 3:
            return 1.0  # Not enough onsets to analyze

        # Calculate inter-onset intervals
        iois = np.diff(onsets)

        # Calculate variability in IOIs
        ioi_variability = np.std(iois)

        # Calculate dynamic variability
        onset_strengths = onset_env[librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr)]
        dynamic_variability = np.std(onset_strengths) if len(onset_strengths) > 0 else 0

        # Combine factors
        complexity = (ioi_variability * 5) + (dynamic_variability * 3)

        # Normalize to 1-10 scale
        complexity = min(10, max(1, complexity))
        return float(complexity)

    def _is_multi_instrument_track(self, y: np.ndarray, sr: int) -> bool:
        """
        Determine if the track contains multiple instruments.

        Args:
            y: Audio data
            sr: Sample rate

        Returns:
            True if multiple instruments are detected
        """
        # Check for multiple distinct onset patterns
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        onsets = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr, units='time')

        if len(onsets) < 4:
            return False

        # Calculate inter-onset intervals
        iois = np.diff(onsets)

        # Check for multiple groups in the IOIs (suggesting different instruments)
        try:
            from sklearn.cluster import KMeans
            iois_reshaped = iois.reshape(-1, 1)
            kmeans = KMeans(n_clusters=2, random_state=0).fit(iois_reshaped)
            clusters = kmeans.labels_

            # Check if we have significantly different clusters
            cluster_means = [np.mean(iois_reshaped[clusters == i]) for i in range(2)]
            if abs(cluster_means[0] - cluster_means[1]) > 0.1:  # Arbitrary threshold
                return True
        except Exception:
            pass  # Fall back to simpler method if sklearn isn't available

        # Check for significant variation in onset strengths (suggesting different instruments)
        if len(onset_strengths) > 0:
            cv = np.std(onset_strengths) / np.mean(onset_strengths) if np.mean(onset_strengths) > 0 else 0
            if cv > 0.5:  # Arbitrary threshold for significant variation
                return True

        # Analyze spectral differences between onsets
        if len(onsets) > 1:
            onset_specs = []
            window_size = int(0.05 * sr)  # 50ms window

            for onset in onsets:
                onset_idx = int(onset * sr)
                if onset_idx + window_size < len(y):
                    onset_y = y[onset_idx:onset_idx + window_size]
                    onset_spec = np.abs(librosa.stft(onset_y))
                    onset_specs.append(np.mean(onset_spec, axis=1))

            if len(onset_specs) > 1:
                # Calculate pairwise distances between spectral profiles
                spectral_distances = []
                for i in range(len(onset_specs)):
                    for j in range(i + 1, len(onset_specs)):
                        dist = np.mean((onset_specs[i] - onset_specs[j]) ** 2)
                        spectral_distances.append(dist)

                if np.mean(spectral_distances) > 0.2:  # Arbitrary threshold
                    return True

        return False

    def _detect_instruments(self, y: np.ndarray, sr: int) -> List[str]:
        """
        Detect which instruments are present in a multi-instrument track.

        Args:
            y: Audio data
            sr: Sample rate

        Returns:
            List of detected instrument types
        """
        detected_instruments = []

        # Split audio into segments based on onsets
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        onsets = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr, units='samples')

        if len(onsets) < 2:
            # Not enough onsets to segment, analyze the whole audio
            cymbal_type, _ = self._detect_cymbal_type(y, sr)
            return [cymbal_type]

        # Create segments from onsets
        segments = []
        for i in range(len(onsets) - 1):
            start = onsets[i]
            end = onsets[i + 1]
            if end - start > sr // 100:  # At least 10ms segment
                segment = y[start:end]
                segments.append(segment)

        # Add the last segment
        if len(y) - onsets[-1] > sr // 100:
            segments.append(y[onsets[-1]:])

        # Analyze each segment
        for segment in segments:
            if len(segment) < sr // 50:  # Skip very short segments
                continue

            # Detect cymbal type
            cymbal_type, _ = self._detect_cymbal_type(segment, sr)

            if cymbal_type not in detected_instruments:
                detected_instruments.append(cymbal_type)

        # Add non-cymbal instruments if we detect them
        # This is a simplified approach - in reality you would need more sophisticated
        # detection for kick, snare, etc.

        # Check for low frequency content suggesting kick drum
        spec = np.abs(librosa.stft(y))
        band_energies = self._calculate_band_energies(spec)

        if band_energies['low'] / band_energies['total'] > 0.3:
            detected_instruments.append('kick')

        # Check for snare characteristics (mid frequency + noise)
        if band_energies['mid'] / band_energies['total'] > 0.4:
            # Additional check for noise component
            flatness = np.mean(librosa.feature.spectral_flatness(y=y))
            if flatness > 0.2:
                detected_instruments.append('snare')

        return detected_instruments