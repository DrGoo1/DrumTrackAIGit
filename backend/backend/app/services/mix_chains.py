"""
DrumTracKAI v4/v5 Advanced Mix Chains
Professional audio processing chains with DSP effects
"""

import numpy as np
from scipy import signal
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class DSPProcessor:
    """Base class for DSP processors"""
    
    def __init__(self, sr: int = 48000):
        self.sr = sr
    
    def process(self, audio: np.ndarray) -> np.ndarray:
        """Process audio - override in subclasses"""
        return audio

class BiquadFilter(DSPProcessor):
    """Biquad filter implementation"""
    
    def __init__(self, sr: int, filter_type: str, freq: float, q: float = 0.707, gain: float = 0):
        super().__init__(sr)
        self.filter_type = filter_type
        self.freq = freq
        self.q = q
        self.gain = gain
        self.b, self.a = self._design_filter()
        self.zi = None
    
    def _design_filter(self):
        """Design the biquad filter"""
        nyquist = self.sr / 2
        norm_freq = self.freq / nyquist
        
        if self.filter_type == 'lowpass':
            return signal.butter(2, norm_freq, btype='low')
        elif self.filter_type == 'highpass':
            return signal.butter(2, norm_freq, btype='high')
        elif self.filter_type == 'bandpass':
            return signal.butter(2, norm_freq, btype='band')
        elif self.filter_type == 'peaking':
            # Peaking EQ
            w = 2 * np.pi * norm_freq
            A = 10**(self.gain / 40)
            alpha = np.sin(w) / (2 * self.q)
            
            b0 = 1 + alpha * A
            b1 = -2 * np.cos(w)
            b2 = 1 - alpha * A
            a0 = 1 + alpha / A
            a1 = -2 * np.cos(w)
            a2 = 1 - alpha / A
            
            return [b0/a0, b1/a0, b2/a0], [1, a1/a0, a2/a0]
        else:
            # Default to no filtering
            return [1], [1]
    
    def process(self, audio: np.ndarray) -> np.ndarray:
        """Apply biquad filter"""
        if self.zi is None:
            self.zi = signal.lfilter_zi(self.b, self.a) * audio[0]
        
        filtered, self.zi = signal.lfilter(self.b, self.a, audio, zi=self.zi)
        return filtered

class TransientProcessor(DSPProcessor):
    """Transient shaper for drums"""
    
    def __init__(self, sr: int, attack: float = 0, sustain: float = 0):
        super().__init__(sr)
        self.attack = attack  # -1 to 1
        self.sustain = sustain  # -1 to 1
    
    def process(self, audio: np.ndarray) -> np.ndarray:
        """Shape transients"""
        # Simple envelope follower
        envelope = np.abs(audio)
        
        # Smooth the envelope
        alpha = 0.01
        smoothed = np.zeros_like(envelope)
        smoothed[0] = envelope[0]
        
        for i in range(1, len(envelope)):
            if envelope[i] > smoothed[i-1]:
                # Attack
                smoothed[i] = alpha * envelope[i] + (1 - alpha) * smoothed[i-1]
            else:
                # Release
                smoothed[i] = 0.001 * envelope[i] + 0.999 * smoothed[i-1]
        
        # Detect transients (rapid changes in envelope)
        transient_strength = np.diff(smoothed, prepend=smoothed[0])
        transient_strength = np.maximum(transient_strength, 0)  # Only positive changes
        
        # Apply transient shaping
        if self.attack != 0:
            # Enhance or reduce attack
            attack_gain = 1 + self.attack * transient_strength * 2
            audio = audio * attack_gain
        
        if self.sustain != 0:
            # Enhance or reduce sustain
            sustain_gain = 1 + self.sustain * (1 - transient_strength)
            audio = audio * sustain_gain
        
        return audio

class Saturator(DSPProcessor):
    """Analog-style saturation"""
    
    def __init__(self, sr: int, drive: float = 0, mix: float = 1):
        super().__init__(sr)
        self.drive = drive  # 0 to 1
        self.mix = mix  # 0 to 1
    
    def process(self, audio: np.ndarray) -> np.ndarray:
        """Apply saturation"""
        if self.drive == 0:
            return audio
        
        # Pre-gain
        driven = audio * (1 + self.drive * 4)
        
        # Soft clipping (tanh saturation)
        saturated = np.tanh(driven)
        
        # Post-gain compensation
        saturated = saturated * (1 / (1 + self.drive * 0.5))
        
        # Mix with dry signal
        return self.mix * saturated + (1 - self.mix) * audio

class Compressor(DSPProcessor):
    """Dynamic range compressor"""
    
    def __init__(self, sr: int, threshold: float = -12, ratio: float = 4, 
                 attack: float = 0.003, release: float = 0.1):
        super().__init__(sr)
        self.threshold = threshold  # dB
        self.ratio = ratio
        self.attack_coeff = np.exp(-1 / (attack * sr))
        self.release_coeff = np.exp(-1 / (release * sr))
        self.envelope = 0
    
    def process(self, audio: np.ndarray) -> np.ndarray:
        """Apply compression"""
        output = np.zeros_like(audio)
        
        for i, sample in enumerate(audio):
            # Convert to dB
            level_db = 20 * np.log10(max(abs(sample), 1e-6))
            
            # Calculate gain reduction
            if level_db > self.threshold:
                excess = level_db - self.threshold
                gain_reduction = excess * (1 - 1/self.ratio)
            else:
                gain_reduction = 0
            
            # Smooth gain reduction with attack/release
            if gain_reduction > self.envelope:
                # Attack
                self.envelope = gain_reduction + (self.envelope - gain_reduction) * self.attack_coeff
            else:
                # Release
                self.envelope = gain_reduction + (self.envelope - gain_reduction) * self.release_coeff
            
            # Apply gain reduction
            gain_linear = 10 ** (-self.envelope / 20)
            output[i] = sample * gain_linear
        
        return output

class ConvolutionReverb(DSPProcessor):
    """Convolution reverb using impulse responses"""
    
    def __init__(self, sr: int, ir_path: Optional[str] = None, mix: float = 0.2):
        super().__init__(sr)
        self.mix = mix
        self.ir = self._load_ir(ir_path) if ir_path else self._generate_default_ir()
    
    def _load_ir(self, ir_path: str) -> np.ndarray:
        """Load impulse response from file"""
        try:
            import soundfile as sf
            ir, sr = sf.read(ir_path)
            if sr != self.sr:
                from scipy.signal import resample
                N = int(len(ir) * self.sr / sr)
                ir = resample(ir, N)
            return ir.astype(np.float32)
        except Exception as e:
            logger.warning(f"Failed to load IR {ir_path}: {e}")
            return self._generate_default_ir()
    
    def _generate_default_ir(self) -> np.ndarray:
        """Generate a simple algorithmic reverb IR"""
        duration = 2.0  # 2 second reverb
        samples = int(duration * self.sr)
        
        # Exponential decay
        t = np.linspace(0, duration, samples)
        decay = np.exp(-t * 2)
        
        # Add some early reflections
        ir = decay * np.random.normal(0, 0.1, samples)
        
        # Add a few discrete early reflections
        early_times = [0.01, 0.023, 0.041, 0.067]
        early_gains = [0.3, 0.2, 0.15, 0.1]
        
        for time, gain in zip(early_times, early_gains):
            idx = int(time * self.sr)
            if idx < len(ir):
                ir[idx] += gain
        
        return ir
    
    def process(self, audio: np.ndarray) -> np.ndarray:
        """Apply convolution reverb"""
        # Convolve with impulse response
        wet = np.convolve(audio, self.ir, mode='same')
        
        # Mix wet and dry
        return (1 - self.mix) * audio + self.mix * wet

class ChannelStrip:
    """Complete channel processing chain"""
    
    def __init__(self, sr: int, config: Dict[str, Any]):
        self.sr = sr
        self.processors = []
        self._build_chain(config)
    
    def _build_chain(self, config: Dict[str, Any]):
        """Build processing chain from configuration"""
        # High-pass filter
        if config.get('highpass', {}).get('enabled', False):
            hpf_config = config['highpass']
            self.processors.append(
                BiquadFilter(self.sr, 'highpass', hpf_config.get('freq', 80))
            )
        
        # EQ
        if config.get('eq', {}).get('enabled', False):
            eq_config = config['eq']
            for band in eq_config.get('bands', []):
                if band.get('gain', 0) != 0:
                    self.processors.append(
                        BiquadFilter(
                            self.sr, 'peaking', 
                            band['freq'], 
                            band.get('q', 1.0), 
                            band['gain']
                        )
                    )
        
        # Compressor
        if config.get('compressor', {}).get('enabled', False):
            comp_config = config['compressor']
            self.processors.append(
                Compressor(
                    self.sr,
                    comp_config.get('threshold', -12),
                    comp_config.get('ratio', 4),
                    comp_config.get('attack', 0.003),
                    comp_config.get('release', 0.1)
                )
            )
        
        # Transient shaper
        if config.get('transients', {}).get('enabled', False):
            trans_config = config['transients']
            self.processors.append(
                TransientProcessor(
                    self.sr,
                    trans_config.get('attack', 0),
                    trans_config.get('sustain', 0)
                )
            )
        
        # Saturator
        if config.get('saturator', {}).get('enabled', False):
            sat_config = config['saturator']
            self.processors.append(
                Saturator(
                    self.sr,
                    sat_config.get('drive', 0),
                    sat_config.get('mix', 1)
                )
            )
    
    def process(self, audio: np.ndarray) -> np.ndarray:
        """Process audio through the channel strip"""
        for processor in self.processors:
            audio = processor.process(audio)
        return audio

class MixBus:
    """Mix bus with sends and processing"""
    
    def __init__(self, sr: int, config: Dict[str, Any]):
        self.sr = sr
        self.channel_strip = ChannelStrip(sr, config.get('processing', {}))
        self.reverb = None
        
        # Initialize reverb if configured
        if config.get('reverb', {}).get('enabled', False):
            reverb_config = config['reverb']
            self.reverb = ConvolutionReverb(
                sr, 
                reverb_config.get('ir_path'),
                reverb_config.get('mix', 0.2)
            )
    
    def mixdown(self, lane_audio: Dict[str, np.ndarray], params: Dict[str, Any]) -> np.ndarray:
        """Mix down all lanes to stereo"""
        if not lane_audio:
            return np.zeros(int(1.0 * self.sr), dtype=np.float32)
        
        # Find the longest audio
        max_len = max(len(audio) for audio in lane_audio.values())
        
        # Mix all lanes
        mix = np.zeros(max_len, dtype=np.float32)
        
        for lane, audio in lane_audio.items():
            # Get lane volume from params
            volume = params.get('volumes', {}).get(lane, 0.8)
            
            # Pad audio to match max length
            if len(audio) < max_len:
                audio = np.pad(audio, (0, max_len - len(audio)))
            
            # Add to mix
            mix += audio * volume
        
        # Apply bus processing
        mix = self.channel_strip.process(mix)
        
        # Apply reverb if enabled
        if self.reverb:
            mix = self.reverb.process(mix)
        
        # Final limiting to prevent clipping
        peak = np.max(np.abs(mix))
        if peak > 0.95:
            mix = mix * (0.95 / peak)
        
        return mix

def build_channel_chain(lane: str, sr: int, params: Dict[str, Any]) -> ChannelStrip:
    """Build a processing chain for a specific drum lane"""
    # Default configurations for different drum types
    default_configs = {
        'kick': {
            'highpass': {'enabled': True, 'freq': 40},
            'eq': {
                'enabled': True,
                'bands': [
                    {'freq': 60, 'gain': 2, 'q': 1.0},    # Sub thump
                    {'freq': 2500, 'gain': 1, 'q': 0.7}   # Click
                ]
            },
            'compressor': {'enabled': True, 'threshold': -8, 'ratio': 3},
            'saturator': {'enabled': True, 'drive': 0.1}
        },
        'snare': {
            'highpass': {'enabled': True, 'freq': 80},
            'eq': {
                'enabled': True,
                'bands': [
                    {'freq': 200, 'gain': 1, 'q': 1.0},   # Body
                    {'freq': 5000, 'gain': 2, 'q': 0.7}   # Crack
                ]
            },
            'compressor': {'enabled': True, 'threshold': -6, 'ratio': 4},
            'transients': {'enabled': True, 'attack': 0.3}
        },
        'hihat': {
            'highpass': {'enabled': True, 'freq': 200},
            'eq': {
                'enabled': True,
                'bands': [
                    {'freq': 8000, 'gain': 1, 'q': 0.5}   # Brightness
                ]
            },
            'compressor': {'enabled': True, 'threshold': -10, 'ratio': 2}
        }
    }
    
    # Get configuration for this lane
    config = default_configs.get(lane, {})
    
    # Override with user parameters
    user_config = params.get('processing', {}).get(lane, {})
    for key, value in user_config.items():
        if key in config:
            config[key].update(value)
        else:
            config[key] = value
    
    return ChannelStrip(sr, config)

def build_buses(sr: int, params: Dict[str, Any]) -> MixBus:
    """Build the main mix bus"""
    bus_config = params.get('mix_bus', {
        'processing': {
            'compressor': {'enabled': True, 'threshold': -3, 'ratio': 2},
            'eq': {
                'enabled': True,
                'bands': [
                    {'freq': 100, 'gain': 0.5, 'q': 0.7}  # Low end control
                ]
            }
        },
        'reverb': {'enabled': True, 'mix': 0.15}
    })
    
    return MixBus(sr, bus_config)
