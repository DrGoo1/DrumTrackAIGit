# drum_analysis/instruments/snare.py

"""
Enhanced snare drum analyzer for the DrumTracKAI framework.

This module provides specialized analysis for snare drum sounds, with the ability to
detect various playing techniques, articulations, and rudiments.
"""

import numpy as np
import librosa
import scipy.signal
import logging
from typing import Dict, Any, Optional, Tuple, List

logger = logging.getLogger(__name__)


class SnareAnalyzer:
    """
    Analyzer for snare drum samples.

    This class provides specialized analysis for snare drum sounds,
    including playing technique detection and rudiment analysis.
    """

    def __init__(self):
        """Initialize the snare analyzer."""
        self.instrument_type = 'snare'

    def analyze(self, y: np.ndarray, sr: int, purpose: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze a snare drum sample.

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

        # Snare-specific features
        features['snare_wire_presence'] = self._detect_snare_wire(y, sr)
        features['brightness'] = float(np.mean(librosa.feature.spectral_rolloff(S=spec, sr=sr)))

        # Detect playing technique
        technique, confidence = self._detect_playing_technique(y, sr, spec)
        features['playing_technique'] = technique
        features['technique_confidence'] = float(confidence)

        # Add technique-specific features
        if technique == 'center_hit':
            features['hit_strength'] = self._calculate_hit_strength(y)
            features['tone_quality'] = self._calculate_tone_quality(y, sr, spec)
        elif technique == 'rimshot':
            features['rimshot_intensity'] = self._calculate_rimshot_intensity(y, sr, spec)
        elif technique == 'cross_stick':
            features['cross_stick_clarity'] = self._calculate_cross_stick_clarity(y, sr, spec)
        elif technique == 'ghost_note':
            features['ghost_note_level'] = self._calculate_ghost_note_level(y)
        elif technique == 'rim_hit':
            features['rim_resonance'] = self._calculate_rim_resonance(y, sr)
        elif technique == 'buzz_roll':
            features['buzz_quality'] = self._calculate_buzz_quality(y, sr)

        # Rudiment detection for technique training purpose
        if purpose == 'technique_training':
            rudiment, confidence = self._detect_rudiment(y, sr)
            features['detected_rudiment'] = rudiment
            features['rudiment_confidence'] = float(confidence)
            features['timing_consistency'] = self._analyze_timing_consistency(y, sr)
            features['dynamic_consistency'] = self._analyze_dynamic_consistency(y, sr)

        # Add purpose-specific features
        if purpose == 'sonic_reference':
            features['crack_factor'] = self._calculate_crack_factor(y, sr)
            features['sustain_quality'] = self._calculate_sustain_quality(y, sr)
        elif purpose == 'technique_training':
            # Already added above
            pass
        elif purpose == 'style_examples':
            features['groove_complexity'] = self._analyze_groove_complexity(y, sr)
            features['ghost_note_pattern'] = self._analyze_ghost_note_pattern(y, sr)

        return features

    def _detect_playing_technique(self, y: np.ndarray, sr: int,
                                  spec: Optional[np.ndarray] = None) -> Tuple[str, float]:
        """
        Detect the playing technique used on the snare drum.

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
        spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(S=spec, sr=sr))

        # Calculate attack and envelope features
        env = np.abs(y)
        peak_amplitude = np.max(env)
        attack_time = self._calculate_attack_time(y, sr)
        decay_rate = self._calculate_decay_rate(env)

        # Transient-to-sustain ratio
        transient_ratio = self._calculate_transient_ratio(y, sr)

        # Noise content
        noise_ratio = self._calculate_noise_ratio(y, sr)

        # Frequency band energy distribution
        band_energies = self._calculate_band_energies(spec)
        high_ratio = band_energies['high'] / band_energies['total']
        mid_ratio = band_energies['mid'] / band_energies['total']
        low_ratio = band_energies['low'] / band_energies['total']

        # Calculate scores for each technique

        # Center hit characteristics:
        # - Balanced frequency distribution
        # - Moderate attack time
        # - Medium decay rate
        center_hit_score = (
                (1.0 if 0.15 < low_ratio < 0.4 else 0.5) +
                (1.0 if 0.3 < mid_ratio < 0.6 else 0.5) +
                (1.0 if 0.2 < high_ratio < 0.5 else 0.5) +
                (1.0 if 0.005 < attack_time < 0.03 else 0.5) +
                (1.0 if decay_rate > 2.0 else 0.5)
        )

        # Rimshot characteristics:
        # - High spectral centroid
        # - Very fast attack
        # - High transient ratio
        # - Bright sound (high spectral rolloff)
        rimshot_score = (
                (1.0 if spectral_centroid > 4000 else 0.5) +
                (1.0 if attack_time < 0.01 else 0.5) +
                (1.0 if transient_ratio > 0.7 else 0.5) +
                (1.0 if spectral_rolloff > 8000 else 0.5) +
                (1.0 if spectral_contrast > 20 else 0.5)
        )

        # Cross stick/rim click characteristics:
        # - Very focused frequency content
        # - Very high spectral contrast
        # - Limited sustain
        # - Lower overall energy
        cross_stick_score = (
                (1.0 if spectral_contrast > 25 else 0.5) +
                (1.0 if peak_amplitude < 0.5 else 0.5) +  # Relative to other techniques
                (1.0 if decay_rate > 5.0 else 0.5) +
                (1.0 if mid_ratio > 0.5 else 0.5) +
                (1.0 if transient_ratio > 0.8 else 0.5)
        )

        # Ghost note characteristics:
        # - Very low amplitude
        # - More mid/low frequencies
        # - Softer attack
        ghost_note_score = (
                (1.0 if peak_amplitude < 0.3 else 0.5) +
                (1.0 if attack_time > 0.01 else 0.5) +
                (1.0 if mid_ratio + low_ratio > 0.7 else 0.5) +
                (1.0 if transient_ratio < 0.6 else 0.5) +
                (1.0 if noise_ratio < 0.4 else 0.5)
        )

        # Rim hit characteristics:
        # - High pitch
        # - Very fast decay
        # - Less snare wire noise
        rim_hit_score = (
                (1.0 if spectral_centroid > 3500 else 0.5) +
                (1.0 if decay_rate > 4.0 else 0.5) +
                (1.0 if noise_ratio < 0.3 else 0.5) +
                (1.0 if high_ratio > 0.4 else 0.5) +
                (1.0 if self._detect_snare_wire(y, sr) < 0.4 else 0.5)
        )

        # Buzz roll characteristics:
        # - Multiple rapid onsets
        # - Sustained energy
        # - Higher noise content
        buzz_roll_score = (
                (1.0 if self._detect_multiple_onsets(y, sr) else 0.0) +
                (1.0 if decay_rate < 2.0 else 0.5) +
                (1.0 if attack_time > 0.02 else 0.5) +
                (1.0 if noise_ratio > 0.5 else 0.5) +
                (1.0 if transient_ratio < 0.5 else 0.5)
        )

        # Determine technique based on highest score
        scores = {
            'center_hit': center_hit_score,
            'rimshot': rimshot_score,
            'cross_stick': cross_stick_score,
            'ghost_note': ghost_note_score,
            'rim_hit': rim_hit_score,
            'buzz_roll': buzz_roll_score
        }

        technique = max(scores, key=scores.get)
        max_score = scores[technique]

        # Convert score to confidence (5 questions, each worth 1 point, max total = 5)
        confidence = max_score / 5.0

        return technique, confidence

    def _detect_snare_wire(self, y: np.ndarray, sr: int) -> float:
        """
        Detect the presence and prominence of snare wire sound.

        Args:
            y: Audio data
            sr: Sample rate

        Returns:
            Snare wire presence score (0.0 to 1.0)
        """
        # Snare wire noise is high frequency, noisy content that persists after attack

        # Get envelope
        env = np.abs(y)

        # Find peak
        peak_idx = np.argmax(env)
        peak_amp = env[peak_idx]

        if peak_idx >= len(y) - 1 or peak_amp == 0:
            return 0.0

        # Analyze the sustain portion after the attack
        sustain_start = min(peak_idx + int(0.01 * sr), len(y) - 1)  # 10ms after peak
        sustain_duration = min(0.1, (len(y) - sustain_start) / sr)  # Up to 100ms of sustain
        sustain_end = min(sustain_start + int(sustain_duration * sr), len(y))

        if sustain_end <= sustain_start:
            return 0.0

        sustain_y = y[sustain_start:sustain_end]

        # Calculate noise content in the sustain
        noise_ratio = self._calculate_noise_ratio(sustain_y, sr)

        # Calculate high-frequency content in the sustain
        if len(sustain_y) >= 512:  # Minimum length for STFT
            sustain_spec = np.abs(librosa.stft(sustain_y))
            band_energies = self._calculate_band_energies(sustain_spec)
            high_ratio = band_energies['high'] / band_energies['total'] if band_energies['total'] > 0 else 0
        else:
            high_ratio = 0

        # Calculate spectral flatness (higher flatness = more noise-like)
        flatness = 0
        try:
            flatness = float(np.mean(librosa.feature.spectral_flatness(y=sustain_y)))
        except Exception as e:
            logger.debug(f"Error calculating spectral flatness: {e}")

        # Combine factors for wire sound score
        wire_score = (noise_ratio * 0.4) + (high_ratio * 0.4) + (flatness * 0.2)

        return float(wire_score)

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
        mid_idx = int(len(spec_sum) * 0.5)  # Mid frequencies

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

    def _calculate_noise_ratio(self, y: np.ndarray, sr: int) -> float:
        """
        Calculate the ratio of noise-like content to tonal content.

        Args:
            y: Audio data
            sr: Sample rate

        Returns:
            Noise ratio (0.0 to 1.0)
        """
        if len(y) < 512:  # Need enough samples for spectral analysis
            return 0.5  # Default value

        try:
            # Calculate spectral flatness (higher = more noise-like)
            flatness = np.mean(librosa.feature.spectral_flatness(y=y))

            # Calculate spectral contrast (higher = more tonal)
            spec = np.abs(librosa.stft(y))
            contrast = np.mean(librosa.feature.spectral_contrast(S=spec, sr=sr))

            # Normalize contrast (higher values indicate less noise)
            norm_contrast = min(1.0, contrast / 30)

            # Combine for noise ratio (flatness contributes positively, contrast negatively)
            noise_ratio = (flatness * 0.7) + (1.0 - norm_contrast) * 0.3

            return float(noise_ratio)
        except Exception as e:
            logger.debug(f"Error calculating noise ratio: {e}")
            return 0.5  # Default value

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

    def _calculate_hit_strength(self, y: np.ndarray) -> float:
        """
        Calculate the strength of a hit based on amplitude.

        Args:
            y: Audio data

        Returns:
            Hit strength score (0.0 to 1.0)
        """
        # Simple calculation based on peak amplitude
        peak_amp = np.max(np.abs(y))

        # Scale to 0-1 range (0.8 is a strong hit)
        strength = min(1.0, peak_amp / 0.8)

        return float(strength)

    def _calculate_tone_quality(self, y: np.ndarray, sr: int, spec: np.ndarray) -> float:
        """
        Calculate the tone quality of a center hit.

        Args:
            y: Audio data
            sr: Sample rate
            spec: Spectrogram

        Returns:
            Tone quality score (0.0 to 1.0)
        """
        # For a center hit, good tone has:
        # - Balanced frequency spectrum
        # - Clear fundamental
        # - Appropriate decay

        # Calculate spectral features
        contrast = np.mean(librosa.feature.spectral_contrast(S=spec, sr=sr))
        flatness = np.mean(librosa.feature.spectral_flatness(y=y))

        # Calculate frequency band balance
        band_energies = self._calculate_band_energies(spec)

        # Ideal distribution for a good snare tone
        low_ratio = band_energies['low'] / band_energies['total'] if band_energies['total'] > 0 else 0
        mid_ratio = band_energies['mid'] / band_energies['total'] if band_energies['total'] > 0 else 0
        high_ratio = band_energies['high'] / band_energies['total'] if band_energies['total'] > 0 else 0

        # Calculate balance factor (ideal: low ~25%, mid ~45%, high ~30%)
        balance_factor = 1.0 - (
                abs(low_ratio - 0.25) +
                abs(mid_ratio - 0.45) +
                abs(high_ratio - 0.30)
        )

        # Calculate decay quality
        env = np.abs(y)
        decay_rate = self._calculate_decay_rate(env)

        # Ideal decay rate for snare (not too fast, not too long)
        decay_factor = 1.0 - min(1.0, abs(decay_rate - 3.0) / 3.0)

        # Combine factors for tone quality
        tone_quality = (
                (contrast / 30) * 0.3 +  # Normalized contrast
                (1.0 - flatness) * 0.2 +  # Inverse flatness
                balance_factor * 0.3 +
                decay_factor * 0.2
        )

        return float(min(1.0, max(0.0, tone_quality)))

    def _calculate_rimshot_intensity(self, y: np.ndarray, sr: int, spec: np.ndarray) -> float:
        """
        Calculate the intensity of a rimshot.

        Args:
            y: Audio data
            sr: Sample rate
            spec: Spectrogram

        Returns:
            Rimshot intensity score (0.0 to 1.0)
        """
        # A strong rimshot has:
        # - High peak amplitude
        # - Strong high-frequency content
        # - Sharp attack

        # Calculate peak amplitude
        peak_amp = np.max(np.abs(y))

        # Calculate high frequency energy
        band_energies = self._calculate_band_energies(spec)
        high_ratio = band_energies['high'] / band_energies['total'] if band_energies['total'] > 0 else 0

        # Calculate attack sharpness
        attack_time = self._calculate_attack_time(y, sr)
        attack_sharpness = 1.0 - min(1.0, attack_time / 0.01)  # Sharper = closer to 0

        # Calculate spectral contrast
        contrast = np.mean(librosa.feature.spectral_contrast(S=spec, sr=sr))
        norm_contrast = min(1.0, contrast / 30)

        # Combine factors for rimshot intensity
        intensity = (
                min(1.0, peak_amp / 0.8) * 0.3 +
                high_ratio * 0.3 +
                attack_sharpness * 0.2 +
                norm_contrast * 0.2
        )

        return float(intensity)

    def _calculate_cross_stick_clarity(self, y: np.ndarray, sr: int, spec: np.ndarray) -> float:
        """
        Calculate the clarity of a cross stick/rim click.

        Args:
            y: Audio data
            sr: Sample rate
            spec: Spectrogram

        Returns:
            Cross stick clarity score (0.0 to 1.0)
        """
        # A clear cross stick has:
        # - Focused frequency content (strong mid frequencies)
        # - Clear attack
        # - Minimal snare wire noise
        # - Good separation from other sounds

        # Calculate mid frequency focus
        band_energies = self._calculate_band_energies(spec)
        mid_ratio = band_energies['mid'] / band_energies['total'] if band_energies['total'] > 0 else 0

        # Calculate attack clarity
        attack_time = self._calculate_attack_time(y, sr)
        attack_clarity = 1.0 - min(1.0, abs(attack_time - 0.005) / 0.01)  # Ideal around 5ms

        # Calculate snare wire noise (should be minimal)
        wire_presence = self._detect_snare_wire(y, sr)
        wire_clarity = 1.0 - wire_presence  # Less wire noise = better clarity

        # Calculate spectral contrast (higher = clearer tone)
        contrast = np.mean(librosa.feature.spectral_contrast(S=spec, sr=sr))
        norm_contrast = min(1.0, contrast / 30)

        # Combine factors
        clarity = (
                (mid_ratio / 0.6) * 0.3 +  # Normalized to ideal ~60% mid energy
                attack_clarity * 0.3 +
                wire_clarity * 0.2 +
                norm_contrast * 0.2
        )

        return float(min(1.0, max(0.0, clarity)))

    def _calculate_ghost_note_level(self, y: np.ndarray) -> float:
        """
        Calculate how well a ghost note is played.

        Args:
            y: Audio data

        Returns:
            Ghost note quality score (0.0 to 1.0)
        """
        # A good ghost note is:
        # - Very quiet but still audible
        # - Has good definition

        # Calculate peak amplitude (should be low)
        peak_amp = np.max(np.abs(y))

        # Ideal range for ghost notes
        if peak_amp < 0.05:  # Too quiet
            amp_factor = peak_amp / 0.05
        elif peak_amp > 0.3:  # Too loud
            amp_factor = 1.0 - ((peak_amp - 0.3) / 0.7)
        else:  # Good range
            amp_factor = 1.0 - abs((peak_amp - 0.15) / 0.15)

        # Calculate envelope smoothness (should be gentle attack)
        env = np.abs(y)
        env_diff = np.diff(env)
        smoothness = 1.0 - min(1.0, np.max(np.abs(env_diff)) / 0.1)

        # Combine factors
        level = amp_factor * 0.7 + smoothness * 0.3

        return float(min(1.0, max(0.0, level)))

    def _calculate_rim_resonance(self, y: np.ndarray, sr: int) -> float:
        """
        Calculate the resonance quality of a rim hit.

        Args:
            y: Audio data
            sr: Sample rate

        Returns:
            Rim resonance quality score (0.0 to 1.0)
        """
        # Rim hits should have:
        # - Clear pitch
        # - Good sustain of that pitch
        # - Less noise content

        # Calculate pitch clarity
        spec = np.abs(librosa.stft(y))
        contrast = np.mean(librosa.feature.spectral_contrast(S=spec, sr=sr))
        norm_contrast = min(1.0, contrast / 30)

        # Calculate pitch stability
        # For pitched sounds, the spectral centroid should be stable
        centroids = librosa.feature.spectral_centroid(S=spec, sr=sr)[0]
        if len(centroids) > 1:
            centroid_stability = 1.0 - min(1.0, np.std(centroids) / 1000)
        else:
            centroid_stability = 0.5  # Default value

        # Calculate sustain
        env = np.abs(y)
        decay_rate = self._calculate_decay_rate(env)
        sustain_quality = 1.0 - min(1.0, abs(decay_rate - 2.0) / 2.0)  # Ideal around 2.0

        # Calculate noise content (should be low)
        noise_ratio = self._calculate_noise_ratio(y, sr)
        noise_factor = 1.0 - noise_ratio

        # Combine factors
        resonance = (
                norm_contrast * 0.3 +
                centroid_stability * 0.2 +
                sustain_quality * 0.3 +
                noise_factor * 0.2
        )

        return float(min(1.0, max(0.0, resonance)))

    def _calculate_buzz_quality(self, y: np.ndarray, sr: int) -> float:
        """
        Calculate the quality of a buzz roll.

        Args:
            y: Audio data
            sr: Sample rate

        Returns:
            Buzz roll quality score (0.0 to 1.0)
        """
        # A good buzz roll has:
        # - Consistent amplitude
        # - Smooth, sustained sound
        # - Appropriate frequency content

        # Calculate amplitude consistency
        env = np.abs(y)
        amp_consistency = 1.0 - min(1.0, np.std(env) / np.mean(env) / 0.5)

        # Calculate smoothness
        env_diff = np.diff(env)
        smoothness = 1.0 - min(1.0, np.std(env_diff) / 0.05)

        # Calculate appropriate frequency content
        spec = np.abs(librosa.stft(y))
        band_energies = self._calculate_band_energies(spec)

        # Ideal distribution for buzz rolls
        low_ratio = band_energies['low'] / band_energies['total'] if band_energies['total'] > 0 else 0
        mid_ratio = band_energies['mid'] / band_energies['total'] if band_energies['total'] > 0 else 0
        high_ratio = band_energies['high'] / band_energies['total'] if band_energies['total'] > 0 else 0

        # Balance factor (ideal: low ~20%, mid ~40%, high ~40%)
        balance_factor = 1.0 - (
                abs(low_ratio - 0.2) +
                abs(mid_ratio - 0.4) +
                abs(high_ratio - 0.4)
        )

        # Onset detection - should be rapid, consistent onsets
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        onsets = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr, units='time')

        # Check onset density and consistency
        if len(onsets) < 3:
            onset_factor = 0.0  # Not a roll
        else:
            # Calculate average onset interval and its consistency
            intervals = np.diff(onsets)
            avg_interval = np.mean(intervals)
            # Ideal interval for buzz roll is around 0.05-0.08s
            interval_quality = 1.0 - min(1.0, abs(avg_interval - 0.065) / 0.065)
            # Consistency of intervals
            interval_consistency = 1.0 - min(1.0, np.std(intervals) / avg_interval)
            onset_factor = (interval_quality + interval_consistency) / 2

        # Combine factors
        quality = (
                amp_consistency * 0.3 +
                smoothness * 0.2 +
                balance_factor * 0.2 +
                onset_factor * 0.3
        )

        return float(min(1.0, max(0.0, quality)))

    def _detect_rudiment(self, y: np.ndarray, sr: int) -> Tuple[str, float]:
        """
        Detect the rudiment being played.

        Args:
            y: Audio data
            sr: Sample rate

        Returns:
            Tuple of (rudiment_name, confidence)
        """
        # Extract onset pattern
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        onsets = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr, units='time')

        if len(onsets) < 2:
            return 'single_stroke', 0.5  # Default with low confidence

        # Calculate inter-onset intervals
        intervals = np.diff(onsets)

        # Extract onset strengths
        onset_strengths = onset_env[librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr)]

        # Normalize strengths
        if len(onset_strengths) > 0 and max(onset_strengths) > 0:
            norm_strengths = onset_strengths / max(onset_strengths)
        else:
            norm_strengths = np.ones_like(onset_strengths)

        # Check for common rudiment patterns

        # Single stroke roll: evenly spaced, consistent dynamics
        if len(intervals) >= 3:
            interval_consistency = 1.0 - min(1.0, np.std(intervals) / np.mean(intervals))
            dynamic_consistency = 1.0 - min(1.0, np.std(norm_strengths))

            if interval_consistency > 0.8 and dynamic_consistency > 0.8:
                return 'single_stroke_roll', interval_consistency * dynamic_consistency

        # Double stroke roll: alternating short-short-long pattern
        if len(intervals) >= 5:
            # Check for groups of 2 (short-short)
            grouped = False
            for i in range(0, len(intervals) - 1, 2):
                if i + 1 < len(intervals):
                    ratio = intervals[i] / intervals[i + 1]
                    if 0.7 < ratio < 1.3:  # Similar intervals within group
                        grouped = True
                    else:
                        grouped = False
                        break

            if grouped:
                return 'double_stroke_roll', 0.8

        # Paradiddle: RLRR-LRLL pattern
        if len(intervals) >= 7:
            # Typical paradiddle has a 1-1-1-2 timing pattern (where 2 is about twice as long as 1)
            pattern_found = False
            for i in range(0, len(intervals) - 3, 4):
                if i + 3 < len(intervals):
                    # Check for 1-1-1-2 pattern
                    if (0.7 < intervals[i] / intervals[i + 1] < 1.3 and
                            0.7 < intervals[i + 1] / intervals[i + 2] < 1.3 and
                            1.5 < intervals[i + 3] / intervals[i] < 2.5):
                        pattern_found = True
                        break

            if pattern_found:
                return 'paradiddle', 0.8

        # Flam: two close onsets with different strengths
        if len(intervals) >= 1 and len(norm_strengths) >= 2:
            for i in range(len(intervals)):
                if intervals[i] < 0.03:  # Very close onsets (< 30ms)
                    if i + 1 < len(norm_strengths):
                        strength_diff = abs(norm_strengths[i] - norm_strengths[i + 1])
                        if strength_diff > 0.3:  # Significant difference in strength
                            return 'flam', 0.7 + (strength_diff * 0.3)

        # Drag/Ruff: three close onsets
        if len(intervals) >= 2:
            for i in range(len(intervals) - 1):
                if intervals[i] < 0.04 and intervals[i + 1] < 0.04:  # Two consecutive short intervals
                    return 'drag', 0.8

        # Buzz: rapid multiple onsets
        onset_density = len(onsets) / (max(onsets) - min(onsets)) if len(onsets) > 1 else 0
        if onset_density > 15:  # More than 15 onsets per second
            return 'buzz', min(1.0, onset_density / 20)

        # If no specific pattern is detected
        return 'unidentified', 0.4

    def _analyze_timing_consistency(self, y: np.ndarray, sr: int) -> float:
        """Analyze timing consistency of the performance."""
        # Extract onset pattern
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        onsets = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr, units='time')

        if len(onsets) < 3:
            return 1.0  # Not enough onsets to analyze

        # Calculate inter-onset intervals
        intervals = np.diff(onsets)

        # Calculate coefficient of variation (lower is more consistent)
        cv = np.std(intervals) / np.mean(intervals) if np.mean(intervals) > 0 else 0

        # Convert to a consistency score (1-10, higher is better)
        consistency = 10 * (1 - min(cv, 1))
        return float(consistency)

    def _analyze_dynamic_consistency(self, y: np.ndarray, sr: int) -> float:
        """Analyze dynamic consistency of the performance."""
        # Extract onset strengths
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        onset_indices = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr)

        if len(onset_indices) < 3:
            return 1.0  # Not enough onsets to analyze

        # Get strengths at onset positions
        onset_strengths = onset_env[onset_indices]

        # Calculate coefficient of variation (lower is more consistent)
        cv = np.std(onset_strengths) / np.mean(onset_strengths) if np.mean(onset_strengths) > 0 else 0

        # Convert to a consistency score (1-10, higher is better)
        consistency = 10 * (1 - min(cv, 1))
        return float(consistency)

    def _calculate_crack_factor(self, y: np.ndarray, sr: int) -> float:
        """Calculate the 'crack' factor of a snare hit."""
        # The 'crack' is characterized by:
        # - Strong attack transient
        # - Prominent high frequencies
        # - Good contrast between attack and sustain

        # Calculate attack strength
        env = np.abs(y)
        attack_idx = np.argmax(env)
        attack_strength = env[attack_idx] if attack_idx < len(env) else 0

        # Calculate high frequency content
        spec = np.abs(librosa.stft(y))
        band_energies = self._calculate_band_energies(spec)
        high_ratio = band_energies['high'] / band_energies['total'] if band_energies['total'] > 0 else 0

        # Calculate attack/sustain contrast
        attack_end = min(attack_idx + int(0.02 * sr), len(y))  # 20ms after peak
        if attack_end >= len(y) or attack_idx >= len(y):
            contrast = 0.5  # Default value
        else:
            attack_energy = np.mean(env[attack_idx:attack_end] ** 2)
            sustain_start = attack_end
            sustain_end = min(sustain_start + int(0.1 * sr), len(y))  # 100ms of sustain
            if sustain_end > sustain_start:
                sustain_energy = np.mean(env[sustain_start:sustain_end] ** 2)
                if sustain_energy > 0:
                    contrast = attack_energy / sustain_energy
                else:
                    contrast = 10.0  # Very high contrast (no sustain)
            else:
                contrast = 0.5  # Default value

        # Normalize contrast
        norm_contrast = min(1.0, contrast / 10)

        # Combine factors for crack factor
        crack_factor = (
                (attack_strength / 0.8) * 0.4 +  # Normalized attack strength
                high_ratio * 0.3 +
                norm_contrast * 0.3
        )

        return float(min(1.0, crack_factor))

    def _calculate_sustain_quality(self, y: np.ndarray, sr: int) -> float:
        """Calculate the quality of the sustain portion."""
        # Good sustain has:
        # - Appropriate length
        # - Good snare wire response
        # - Smooth decay

        # Calculate decay rate
        env = np.abs(y)
        decay_rate = self._calculate_decay_rate(env)

        # Ideal decay rate for snare (not too fast, not too long)
        decay_factor = 1.0 - min(1.0, abs(decay_rate - 3.0) / 3.0)

        # Calculate snare wire response
        wire_presence = self._detect_snare_wire(y, sr)

        # Calculate smoothness of decay
        peak_idx = np.argmax(env)
        if peak_idx >= len(env) - 1:
            smoothness = 0.5  # Default value
        else:
            decay = env[peak_idx:]
            # Smooth the decay curve
            window_size = min(512, len(decay) // 4)
            if window_size > 1:
                smoothed = np.convolve(decay, np.ones(window_size) / window_size, mode='valid')
                # Calculate deviation from ideal exponential decay
                if len(smoothed) > 1:
                    time = np.arange(len(smoothed))
                    log_smoothed = np.log(smoothed + 1e-10)
                    # Fit exponential decay
                    polyfit = np.polyfit(time, log_smoothed, 1)
                    # Generate ideal decay
                    ideal_decay = np.exp(polyfit[1] + polyfit[0] * time)
                    # Calculate mean squared error
                    mse = np.mean((smoothed - ideal_decay) ** 2)
                    # Normalize to 0-1 range (lower = smoother)
                    smoothness = 1.0 - min(1.0, mse / 0.01)
                else:
                    smoothness = 0.5
            else:
                smoothness = 0.5

        # Combine factors for sustain quality
        sustain_quality = (
                decay_factor * 0.4 +
                wire_presence * 0.4 +
                smoothness * 0.2
        )

        return float(min(1.0, max(0.0, sustain_quality)))

    def _analyze_groove_complexity(self, y: np.ndarray, sr: int) -> float:
        """Analyze the complexity of a groove pattern."""
        # Extract onset pattern
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        onsets = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr, units='time')

        if len(onsets) < 3:
            return 1.0  # Not enough onsets to analyze

        # Calculate inter-onset intervals
        intervals = np.diff(onsets)

        # Calculate variability in intervals
        interval_variability = np.std(intervals)

        # Extract onset strengths
        onset_strengths = onset_env[librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr)]

        # Calculate dynamic variability
        dynamic_variability = np.std(onset_strengths) if len(onset_strengths) > 0 else 0

        # Detect tempo and quantize intervals to beats
        if len(intervals) > 0:
            # Estimate tempo
            tempo = 60 / np.median(intervals)
            # Normalize tempo to reasonable range
            tempo = max(min(tempo, 240), 40)

            # Calculate beat subdivision (in seconds)
            beat_duration = 60 / tempo
            sixteenth_duration = beat_duration / 4

            # Quantize intervals to sixteenth notes
            quantized_intervals = np.round(intervals / sixteenth_duration) * sixteenth_duration

            # Count unique rhythmic patterns
            unique_patterns = np.unique(quantized_intervals)
            unique_count = len(unique_patterns)

            # More unique patterns = more complex
            pattern_complexity = min(1.0, unique_count / 8)  # Normalize to max of 8 unique values
        else:
            pattern_complexity = 0.0

        # Combine factors for complexity
        complexity = (
                min(1.0, interval_variability * 5) * 0.3 +
                min(1.0, dynamic_variability * 3) * 0.3 +
                pattern_complexity * 0.4
        )

        # Scale to 1-10 range
        complexity = 1 + (complexity * 9)
        return float(complexity)

    def _analyze_ghost_note_pattern(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """Analyze the pattern of ghost notes in a performance."""
        # Extract onset pattern
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        onsets = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr)

        if len(onsets) < 3:
            return {
                'ghost_note_count': 0,
                'ghost_note_ratio': 0.0,
                'pattern_complexity': 1.0
            }

        # Get onset strengths
        onset_strengths = onset_env[onsets]

        # Normalize strengths
        if max(onset_strengths) > 0:
            norm_strengths = onset_strengths / max(onset_strengths)
        else:
            norm_strengths = np.ones_like(onset_strengths)

        # Identify ghost notes (typically below 0.3 of max volume)
        ghost_mask = norm_strengths < 0.3
        ghost_count = np.sum(ghost_mask)
        ghost_ratio = float(ghost_count / len(norm_strengths))

        # Analyze pattern complexity
        if ghost_count > 0:
            # Convert onsets to beat positions
            onset_times = librosa.frames_to_time(onsets, sr=sr)

            # Estimate tempo
            if len(onset_times) > 1:
                tempo = 60 / np.median(np.diff(onset_times))
                # Normalize tempo to reasonable range
                tempo = max(min(tempo, 240), 40)
            else:
                tempo = 120  # Default tempo

            # Calculate beat positions
            beat_duration = 60 / tempo
            beat_positions = onset_times / beat_duration

            # Quantize to sixteenth notes
            quantized_positions = np.round(beat_positions * 4) / 4

            # Create a binary pattern of accents vs ghosts
            pattern = np.zeros(16)  # Assuming one bar of 4/4

            for i, pos in enumerate(quantized_positions):
                idx = int(pos * 4) % 16
                if idx < 16:
                    if ghost_mask[i]:
                        pattern[idx] = 0.5  # Ghost note
                    else:
                        pattern[idx] = 1.0  # Accent

            # Count transitions between ghost notes and accents
            transitions = 0
            for i in range(1, len(pattern)):
                if (pattern[i - 1] == 0.5 and pattern[i] == 1.0) or (pattern[i - 1] == 1.0 and pattern[i] == 0.5):
                    transitions += 1

            # Calculate pattern complexity based on transitions
            pattern_complexity = min(10.0, 1.0 + transitions)
        else:
            pattern_complexity = 1.0  # No ghost notes = simple pattern

        return {
            'ghost_note_count': int(ghost_count),
            'ghost_note_ratio': float(ghost_ratio),
            'pattern_complexity': float(pattern_complexity)
        }