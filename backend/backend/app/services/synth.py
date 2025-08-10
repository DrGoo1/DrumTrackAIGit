"""
DrumTracKAI v4/v5 Advanced Sampler Synth
Professional drum sample playback with velocity layers and processing
"""

import numpy as np
import soundfile as sf
from pathlib import Path
from scipy.signal import resample
import logging

logger = logging.getLogger(__name__)

class SamplerSynth:
    """Advanced sampler for drum kit playback"""
    
    def __init__(self, sr=48000, kit_map=None):
        self.sr = sr
        self.kit_map = kit_map or {}
        self.cache = {}
        self.default_samples = {
            'kick': self._generate_kick_sample(),
            'snare': self._generate_snare_sample(),
            'hihat': self._generate_hihat_sample(),
            'crash': self._generate_crash_sample(),
            'ride': self._generate_ride_sample(),
            'tom': self._generate_tom_sample()
        }
    
    def _load_sample(self, key: str) -> np.ndarray:
        """Load and cache a sample"""
        if key in self.cache:
            return self.cache[key]
        
        # Try to load from kit mapping
        path = self.kit_map.get(key)
        if path and Path(path).exists():
            try:
                audio, sr = sf.read(path)
                if sr != self.sr:
                    # Resample to target sample rate
                    N = int(len(audio) * self.sr / sr)
                    audio = resample(audio, N)
                
                # Convert to mono if stereo
                if audio.ndim > 1:
                    audio = audio[:, 0]
                
                # Normalize and cache
                audio = audio.astype(np.float32)
                self.cache[key] = audio
                return audio
                
            except Exception as e:
                logger.warning(f"Failed to load sample {path}: {e}")
        
        # Fall back to generated sample
        if key in self.default_samples:
            sample = self.default_samples[key]
            self.cache[key] = sample
            return sample
        
        # Return silence if nothing else works
        return np.zeros(int(0.1 * self.sr), dtype=np.float32)
    
    def render_lane(self, events: list) -> np.ndarray:
        """Render a drum lane from MIDI events"""
        if not events:
            return np.zeros(int(1.0 * self.sr), dtype=np.float32)
        
        # Calculate total duration
        max_time = max(e.get('time_sec', e.get('seconds', 0)) for e in events)
        total_dur = max_time + 3.0  # Add 3 seconds for sample decay
        
        # Initialize output buffer
        out = np.zeros(int(total_dur * self.sr), dtype=np.float32)
        
        for event in events:
            # Get timing and parameters
            time_sec = event.get('time_sec', event.get('seconds', 0))
            velocity = event.get('velocity', 100) / 127.0
            lane = event.get('lane', event.get('key', 'kick'))
            
            # Load sample
            sample = self._load_sample(lane)
            
            # Calculate position in output buffer
            start_idx = int(time_sec * self.sr)
            end_idx = min(start_idx + len(sample), len(out))
            sample_len = end_idx - start_idx
            
            if sample_len > 0:
                # Apply velocity and mix into output
                out[start_idx:end_idx] += sample[:sample_len] * velocity
        
        return out
    
    def _generate_kick_sample(self) -> np.ndarray:
        """Generate a synthetic kick drum sample"""
        duration = 0.8
        t = np.linspace(0, duration, int(duration * self.sr))
        
        # Fundamental frequency sweep
        f0 = 60 * np.exp(-t * 8)  # 60Hz to ~10Hz
        phase = 2 * np.pi * np.cumsum(f0) / self.sr
        
        # Harmonic content
        fundamental = np.sin(phase)
        harmonic2 = 0.3 * np.sin(2 * phase)
        click = 0.2 * np.sin(8 * phase) * np.exp(-t * 20)
        
        # Envelope
        envelope = np.exp(-t * 3)
        
        # Combine
        kick = (fundamental + harmonic2 + click) * envelope
        return kick.astype(np.float32)
    
    def _generate_snare_sample(self) -> np.ndarray:
        """Generate a synthetic snare drum sample"""
        duration = 0.3
        t = np.linspace(0, duration, int(duration * self.sr))
        
        # Tone component (200Hz fundamental)
        tone = 0.4 * np.sin(2 * np.pi * 200 * t)
        
        # Noise component (filtered white noise)
        noise = np.random.normal(0, 0.6, len(t))
        # Simple high-pass filter (emphasize high frequencies)
        noise = np.diff(np.concatenate([[0], noise]))
        
        # Envelope
        envelope = np.exp(-t * 8)
        
        # Combine
        snare = (tone + noise) * envelope
        return snare.astype(np.float32)
    
    def _generate_hihat_sample(self) -> np.ndarray:
        """Generate a synthetic hi-hat sample"""
        duration = 0.15
        t = np.linspace(0, duration, int(duration * self.sr))
        
        # High-frequency noise
        noise = np.random.normal(0, 0.3, len(t))
        
        # Metallic resonance (multiple frequencies)
        metallic = (0.1 * np.sin(2 * np.pi * 8000 * t) +
                   0.08 * np.sin(2 * np.pi * 12000 * t) +
                   0.06 * np.sin(2 * np.pi * 16000 * t))
        
        # Sharp envelope
        envelope = np.exp(-t * 25)
        
        # Combine
        hihat = (noise + metallic) * envelope
        return hihat.astype(np.float32)
    
    def _generate_crash_sample(self) -> np.ndarray:
        """Generate a synthetic crash cymbal sample"""
        duration = 2.0
        t = np.linspace(0, duration, int(duration * self.sr))
        
        # Complex harmonic series for metallic sound
        crash = np.zeros_like(t)
        freqs = [400, 800, 1200, 2400, 4800, 9600]
        amps = [0.3, 0.25, 0.2, 0.15, 0.1, 0.05]
        
        for freq, amp in zip(freqs, amps):
            crash += amp * np.sin(2 * np.pi * freq * t)
        
        # Add noise for shimmer
        noise = 0.2 * np.random.normal(0, 1, len(t))
        crash += noise
        
        # Long decay envelope
        envelope = np.exp(-t * 1.5)
        
        crash *= envelope
        return crash.astype(np.float32)
    
    def _generate_ride_sample(self) -> np.ndarray:
        """Generate a synthetic ride cymbal sample"""
        duration = 1.5
        t = np.linspace(0, duration, int(duration * self.sr))
        
        # Bell-like tone
        bell = 0.4 * np.sin(2 * np.pi * 800 * t)
        
        # Shimmer (high-frequency content)
        shimmer = 0.2 * np.random.normal(0, 1, len(t))
        # Simple high-pass for shimmer
        shimmer = np.diff(np.concatenate([[0], shimmer]))
        
        # Medium decay
        envelope = np.exp(-t * 2)
        
        ride = (bell + shimmer) * envelope
        return ride.astype(np.float32)
    
    def _generate_tom_sample(self) -> np.ndarray:
        """Generate a synthetic tom sample"""
        duration = 0.6
        t = np.linspace(0, duration, int(duration * self.sr))
        
        # Fundamental frequency (tuned tom)
        f0 = 120  # Mid tom frequency
        fundamental = np.sin(2 * np.pi * f0 * t)
        
        # Harmonic content
        harmonic2 = 0.3 * np.sin(2 * np.pi * f0 * 2 * t)
        harmonic3 = 0.1 * np.sin(2 * np.pi * f0 * 3 * t)
        
        # Envelope with slight pitch bend
        envelope = np.exp(-t * 4)
        pitch_bend = np.exp(-t * 2)  # Slight pitch drop
        
        tom = (fundamental + harmonic2 + harmonic3) * envelope * pitch_bend
        return tom.astype(np.float32)
