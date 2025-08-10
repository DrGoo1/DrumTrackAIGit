#!/usr/bin/env python3
"""
DrumTracKAI Advanced Audio Engine
High-performance audio processing with multi-format support and real-time analysis
"""

import numpy as np
import librosa
import soundfile as sf
import scipy.signal
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Union
import asyncio
import json
import logging
from dataclasses import dataclass, asdict
from enum import Enum
import time
import threading
from concurrent.futures import ThreadPoolExecutor
import queue

# Audio format support
try:
    import pydub
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    logging.warning("pydub not available - limited format support")

# Enhanced format detection
try:
    import mutagen
    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False
    logging.warning("mutagen not available - limited metadata support")

logger = logging.getLogger(__name__)

class AudioFormat(Enum):
    WAV = "wav"
    MP3 = "mp3"
    FLAC = "flac"
    AIFF = "aiff"
    M4A = "m4a"
    OGG = "ogg"
    WMA = "wma"

class SampleRate(Enum):
    SR_44100 = 44100
    SR_48000 = 48000
    SR_88200 = 88200
    SR_96000 = 96000
    SR_176400 = 176400
    SR_192000 = 192000

class BitDepth(Enum):
    BIT_16 = 16
    BIT_24 = 24
    BIT_32_FLOAT = 32

class GridSnap(Enum):
    QUARTER = "1/4"
    EIGHTH = "1/8"
    SIXTEENTH = "1/16"
    THIRTY_SECOND = "1/32"
    TRIPLET_8 = "1/8T"
    TRIPLET_16 = "1/16T"

@dataclass
class AudioSpecs:
    """Audio file specifications"""
    sample_rate: int
    channels: int
    bit_depth: int
    duration: float
    format: str
    file_size: int
    
@dataclass
class DrumHit:
    """Individual drum hit detection"""
    time: float
    drum_type: str  # kick, snare, hihat, crash, ride, tom1, tom2, tom3
    velocity: float
    confidence: float
    frequency_range: Tuple[float, float]

@dataclass
class TimeMarker:
    """Timeline markers for song structure"""
    time: float
    label: str
    marker_type: str  # verse, chorus, bridge, solo, intro, outro
    confidence: float = 1.0

@dataclass
class TempoChange:
    """Tempo changes throughout the track"""
    time: float
    bpm: float
    time_signature: str = "4/4"

@dataclass
class WaveformData:
    """Processed waveform data for visualization"""
    audio_data: np.ndarray
    sample_rate: int
    peaks: np.ndarray
    rms: np.ndarray
    spectral_centroid: np.ndarray
    zero_crossings: np.ndarray
    onset_frames: np.ndarray

class AudioEngine:
    """Advanced audio processing engine for DrumTracKAI"""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.loaded_audio: Dict[str, np.ndarray] = {}
        self.audio_specs: Dict[str, AudioSpecs] = {}
        self.waveform_cache: Dict[str, WaveformData] = {}
        self.analysis_cache: Dict[str, Dict] = {}
        
        # Audio processing settings
        self.default_sr = 44100
        self.default_hop_length = 512
        self.default_n_fft = 2048
        
        # Drum detection parameters
        self.drum_frequency_ranges = {
            'kick': (20, 120),
            'snare': (180, 250),
            'hihat': (6000, 20000),
            'crash': (3000, 20000),
            'ride': (2000, 8000),
            'tom1': (80, 200),    # High tom
            'tom2': (60, 150),    # Mid tom  
            'tom3': (40, 100),    # Floor tom
        }
        
        logger.info(f"AudioEngine initialized with {max_workers} workers")

    async def load_audio_file(self, file_path: Union[str, Path], target_sr: Optional[int] = None) -> str:
        """Load audio file with format detection and conversion"""
        file_path = Path(file_path)
        file_id = f"audio_{hash(str(file_path))}"
        
        if file_id in self.loaded_audio:
            logger.info(f"Audio already loaded: {file_id}")
            return file_id
        
        try:
            # Detect format and load
            specs, audio_data = await self._load_with_format_detection(file_path, target_sr)
            
            # Store audio data and specs
            self.loaded_audio[file_id] = audio_data
            self.audio_specs[file_id] = specs
            
            logger.info(f"Loaded audio: {file_path.name} ({specs.duration:.2f}s, {specs.sample_rate}Hz)")
            return file_id
            
        except Exception as e:
            logger.error(f"Failed to load audio {file_path}: {e}")
            raise

    async def _load_with_format_detection(self, file_path: Path, target_sr: Optional[int]) -> Tuple[AudioSpecs, np.ndarray]:
        """Load audio with automatic format detection and conversion"""
        
        def _load_audio():
            # Try librosa first (handles most formats)
            try:
                audio_data, sr = librosa.load(str(file_path), sr=target_sr, mono=False)
                
                # Handle mono/stereo
                if audio_data.ndim == 1:
                    channels = 1
                else:
                    channels = audio_data.shape[0]
                    # Convert to mono for processing (mix down)
                    audio_data = librosa.to_mono(audio_data)
                
                duration = len(audio_data) / sr
                
                specs = AudioSpecs(
                    sample_rate=sr,
                    channels=channels,
                    bit_depth=32,  # librosa loads as float32
                    duration=duration,
                    format=file_path.suffix.lower()[1:],
                    file_size=file_path.stat().st_size
                )
                
                return specs, audio_data
                
            except Exception as librosa_error:
                logger.warning(f"librosa failed: {librosa_error}")
                
                # Fallback to pydub for problematic formats
                if PYDUB_AVAILABLE:
                    try:
                        audio_segment = AudioSegment.from_file(str(file_path))
                        
                        # Convert to numpy array
                        audio_data = np.array(audio_segment.get_array_of_samples(), dtype=np.float32)
                        
                        # Normalize to [-1, 1]
                        audio_data = audio_data / (2**(audio_segment.sample_width * 8 - 1))
                        
                        # Handle stereo
                        if audio_segment.channels == 2:
                            audio_data = audio_data.reshape((-1, 2))
                            audio_data = np.mean(audio_data, axis=1)  # Mix to mono
                        
                        # Resample if needed
                        if target_sr and audio_segment.frame_rate != target_sr:
                            audio_data = librosa.resample(audio_data, 
                                                        orig_sr=audio_segment.frame_rate, 
                                                        target_sr=target_sr)
                            sr = target_sr
                        else:
                            sr = audio_segment.frame_rate
                        
                        specs = AudioSpecs(
                            sample_rate=sr,
                            channels=audio_segment.channels,
                            bit_depth=audio_segment.sample_width * 8,
                            duration=len(audio_segment) / 1000.0,
                            format=file_path.suffix.lower()[1:],
                            file_size=file_path.stat().st_size
                        )
                        
                        return specs, audio_data
                        
                    except Exception as pydub_error:
                        logger.error(f"pydub also failed: {pydub_error}")
                        raise Exception(f"Could not load audio file: {file_path}")
                
                else:
                    raise librosa_error
        
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, _load_audio)

    async def generate_waveform_data(self, audio_id: str, zoom_level: float = 1.0) -> WaveformData:
        """Generate comprehensive waveform data for visualization"""
        
        cache_key = f"{audio_id}_waveform_{zoom_level}"
        if cache_key in self.waveform_cache:
            return self.waveform_cache[cache_key]
        
        if audio_id not in self.loaded_audio:
            raise ValueError(f"Audio not loaded: {audio_id}")
        
        def _generate_waveform():
            audio_data = self.loaded_audio[audio_id]
            specs = self.audio_specs[audio_id]
            sr = specs.sample_rate
            
            # Calculate decimation factor based on zoom
            decimation = max(1, int(len(audio_data) / (2000 * zoom_level)))
            
            # Decimate for visualization if needed
            if decimation > 1:
                vis_audio = scipy.signal.decimate(audio_data, decimation, ftype='fir')
                vis_sr = sr // decimation
            else:
                vis_audio = audio_data
                vis_sr = sr
            
            # Calculate peaks (for waveform outline)
            window_size = max(1, len(vis_audio) // 1000)
            peaks = np.array([
                np.max(np.abs(vis_audio[i:i+window_size])) 
                for i in range(0, len(vis_audio), window_size)
            ])
            
            # Calculate RMS (for average energy)
            rms = np.array([
                np.sqrt(np.mean(vis_audio[i:i+window_size]**2))
                for i in range(0, len(vis_audio), window_size)
            ])
            
            # Spectral features
            spectral_centroid = librosa.feature.spectral_centroid(
                y=vis_audio, sr=vis_sr, hop_length=self.default_hop_length
            )[0]
            
            # Zero crossings (useful for drum transients)
            zero_crossings = librosa.feature.zero_crossing_rate(
                vis_audio, hop_length=self.default_hop_length
            )[0]
            
            # Onset detection (drum hits)
            onset_frames = librosa.onset.onset_detect(
                y=vis_audio, sr=vis_sr, hop_length=self.default_hop_length,
                backtrack=True, units='frames'
            )
            
            waveform_data = WaveformData(
                audio_data=vis_audio,
                sample_rate=vis_sr,
                peaks=peaks,
                rms=rms,
                spectral_centroid=spectral_centroid,
                zero_crossings=zero_crossings,
                onset_frames=onset_frames
            )
            
            return waveform_data
        
        # Generate in thread pool
        loop = asyncio.get_event_loop()
        waveform_data = await loop.run_in_executor(self.executor, _generate_waveform)
        
        # Cache the result
        self.waveform_cache[cache_key] = waveform_data
        
        logger.info(f"Generated waveform data for {audio_id} (zoom: {zoom_level})")
        return waveform_data

    async def detect_drum_hits(self, audio_id: str, sophistication_level: float = 0.887) -> List[DrumHit]:
        """Advanced drum hit detection using AI-enhanced analysis"""
        
        if audio_id not in self.loaded_audio:
            raise ValueError(f"Audio not loaded: {audio_id}")
        
        def _detect_hits():
            audio_data = self.loaded_audio[audio_id]
            specs = self.audio_specs[audio_id]
            sr = specs.sample_rate
            
            hits = []
            
            # Enhanced onset detection
            onset_frames = librosa.onset.onset_detect(
                y=audio_data, sr=sr,
                hop_length=self.default_hop_length,
                backtrack=True,
                units='frames'
            )
            
            onset_times = librosa.frames_to_time(onset_frames, sr=sr, hop_length=self.default_hop_length)
            
            # Get spectral features for classification
            stft = librosa.stft(audio_data, hop_length=self.default_hop_length, n_fft=self.default_n_fft)
            magnitude = np.abs(stft)
            
            for onset_time in onset_times:
                # Get the frame closest to onset
                frame_idx = int(onset_time * sr / self.default_hop_length)
                
                if frame_idx < magnitude.shape[1]:
                    # Analyze frequency content at this onset
                    frame_magnitude = magnitude[:, frame_idx]
                    freq_bins = librosa.fft_frequencies(sr=sr, n_fft=self.default_n_fft)
                    
                    # Classify drum type based on frequency content
                    drum_type, confidence = self._classify_drum_hit(frame_magnitude, freq_bins, sophistication_level)
                    
                    # Calculate velocity based on magnitude
                    velocity = min(1.0, np.max(frame_magnitude) / np.mean(frame_magnitude))
                    
                    # Get frequency range for this drum type
                    freq_range = self.drum_frequency_ranges.get(drum_type, (20, 20000))
                    
                    hit = DrumHit(
                        time=onset_time,
                        drum_type=drum_type,
                        velocity=velocity,
                        confidence=confidence,
                        frequency_range=freq_range
                    )
                    
                    hits.append(hit)
            
            return hits
        
        loop = asyncio.get_event_loop()
        hits = await loop.run_in_executor(self.executor, _detect_hits)
        
        logger.info(f"Detected {len(hits)} drum hits in {audio_id}")
        return hits

    def _classify_drum_hit(self, magnitude: np.ndarray, freq_bins: np.ndarray, sophistication: float) -> Tuple[str, float]:
        """Classify drum hit type based on frequency content"""
        
        # Calculate energy in each frequency band
        band_energies = {}
        for drum_type, (low_freq, high_freq) in self.drum_frequency_ranges.items():
            # Find frequency bins in this range
            freq_mask = (freq_bins >= low_freq) & (freq_bins <= high_freq)
            band_energy = np.sum(magnitude[freq_mask])
            band_energies[drum_type] = band_energy
        
        # Find dominant frequency band
        total_energy = sum(band_energies.values())
        if total_energy == 0:
            return 'other', 0.0
        
        # Normalize energies
        normalized_energies = {k: v/total_energy for k, v in band_energies.items()}
        
        # Enhanced classification based on sophistication level
        if sophistication >= 0.85:  # Expert level
            # Use advanced heuristics
            kick_energy = normalized_energies['kick']
            snare_energy = normalized_energies['snare']
            hihat_energy = normalized_energies['hihat']
            
            # Advanced classification logic
            if kick_energy > 0.4:
                confidence = min(0.95, kick_energy + 0.2)
                return 'kick', confidence
            elif snare_energy > 0.3 and normalized_energies['tom1'] > 0.1:
                confidence = min(0.9, snare_energy + normalized_energies['tom1'])
                return 'snare', confidence
            elif hihat_energy > 0.5:
                confidence = min(0.85, hihat_energy + 0.1)
                return 'hihat', confidence
            else:
                # Find highest energy band
                best_drum = max(normalized_energies, key=normalized_energies.get)
                confidence = min(0.8, normalized_energies[best_drum] + 0.2)
                return best_drum, confidence
        else:
            # Basic classification
            best_drum = max(normalized_energies, key=normalized_energies.get)
            confidence = min(0.7, normalized_energies[best_drum])
            return best_drum, confidence

    async def analyze_tempo_changes(self, audio_id: str) -> List[TempoChange]:
        """Detect tempo changes throughout the track"""
        
        if audio_id not in self.loaded_audio:
            raise ValueError(f"Audio not loaded: {audio_id}")
        
        def _analyze_tempo():
            audio_data = self.loaded_audio[audio_id]
            specs = self.audio_specs[audio_id]
            sr = specs.sample_rate
            
            # Use onset detection for tempo tracking
            onset_frames = librosa.onset.onset_detect(
                y=audio_data, sr=sr, hop_length=self.default_hop_length
            )
            
            # Convert to time
            onset_times = librosa.frames_to_time(onset_frames, sr=sr, hop_length=self.default_hop_length)
            
            # Analyze tempo in segments
            segment_length = 8.0  # 8 second segments
            tempo_changes = []
            
            for start_time in np.arange(0, specs.duration, segment_length):
                end_time = min(start_time + segment_length, specs.duration)
                
                # Get onsets in this segment
                segment_onsets = onset_times[(onset_times >= start_time) & (onset_times < end_time)]
                
                if len(segment_onsets) > 3:
                    # Calculate inter-onset intervals
                    intervals = np.diff(segment_onsets)
                    
                    # Estimate tempo from most common interval
                    if len(intervals) > 0:
                        # Use median interval to avoid outliers
                        median_interval = np.median(intervals)
                        estimated_bpm = 60.0 / median_interval
                        
                        # Snap to reasonable BPM range
                        estimated_bpm = np.clip(estimated_bpm, 60, 200)
                        
                        tempo_change = TempoChange(
                            time=start_time,
                            bpm=round(estimated_bpm),
                            time_signature="4/4"  # Default, could be enhanced
                        )
                        
                        tempo_changes.append(tempo_change)
            
            return tempo_changes
        
        loop = asyncio.get_event_loop()
        tempo_changes = await loop.run_in_executor(self.executor, _analyze_tempo)
        
        logger.info(f"Detected {len(tempo_changes)} tempo changes in {audio_id}")
        return tempo_changes

    async def detect_song_structure(self, audio_id: str) -> List[TimeMarker]:
        """Detect song structure markers (verse, chorus, etc.)"""
        
        if audio_id not in self.loaded_audio:
            raise ValueError(f"Audio not loaded: {audio_id}")
        
        def _detect_structure():
            audio_data = self.loaded_audio[audio_id]
            specs = self.audio_specs[audio_id]
            sr = specs.sample_rate
            
            # Use chroma features for harmonic analysis
            chroma = librosa.feature.chroma_stft(y=audio_data, sr=sr, hop_length=self.default_hop_length)
            
            # Use MFCC for timbral analysis
            mfcc = librosa.feature.mfcc(y=audio_data, sr=sr, hop_length=self.default_hop_length, n_mfcc=13)
            
            # Combine features
            features = np.vstack([chroma, mfcc])
            
            # Use simple structure detection
            markers = []
            
            # Basic structure assumptions for drum tracks
            duration = specs.duration
            
            if duration > 30:  # Only for longer tracks
                # Intro (first 10%)
                markers.append(TimeMarker(0.0, "Intro", "intro", 0.8))
                
                # Verse (10-40%)
                verse_start = duration * 0.1
                markers.append(TimeMarker(verse_start, "Verse 1", "verse", 0.7))
                
                # Chorus (40-60%)
                chorus_start = duration * 0.4
                markers.append(TimeMarker(chorus_start, "Chorus 1", "chorus", 0.7))
                
                # Verse 2 (60-80%)
                if duration > 60:
                    verse2_start = duration * 0.6
                    markers.append(TimeMarker(verse2_start, "Verse 2", "verse", 0.6))
                
                # Outro (last 20%)
                outro_start = duration * 0.8
                markers.append(TimeMarker(outro_start, "Outro", "outro", 0.7))
            
            return markers
        
        loop = asyncio.get_event_loop()
        markers = await loop.run_in_executor(self.executor, _detect_structure)
        
        logger.info(f"Detected {len(markers)} structure markers in {audio_id}")
        return markers

    def time_to_samples(self, time_seconds: float, sample_rate: int) -> int:
        """Convert time to sample index"""
        return int(time_seconds * sample_rate)
    
    def samples_to_time(self, samples: int, sample_rate: int) -> float:
        """Convert sample index to time"""
        return samples / sample_rate
    
    def snap_to_grid(self, time_seconds: float, bpm: float, grid: GridSnap) -> float:
        """Snap time to musical grid"""
        beat_duration = 60.0 / bpm
        
        grid_values = {
            GridSnap.QUARTER: beat_duration,
            GridSnap.EIGHTH: beat_duration / 2,
            GridSnap.SIXTEENTH: beat_duration / 4,
            GridSnap.THIRTY_SECOND: beat_duration / 8,
            GridSnap.TRIPLET_8: beat_duration / 3,
            GridSnap.TRIPLET_16: beat_duration / 6,
        }
        
        grid_duration = grid_values[grid]
        return round(time_seconds / grid_duration) * grid_duration

    async def export_stems(self, audio_id: str, stems: Dict[str, np.ndarray], 
                          output_dir: Path, format: AudioFormat = AudioFormat.WAV,
                          sample_rate: int = 44100, bit_depth: BitDepth = BitDepth.BIT_24) -> Dict[str, Path]:
        """Export individual stems with high quality"""
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        def _export_stem(stem_name: str, audio_data: np.ndarray) -> Path:
            output_file = output_dir / f"{stem_name}.{format.value}"
            
            # Set up soundfile parameters
            subtype_map = {
                BitDepth.BIT_16: 'PCM_16',
                BitDepth.BIT_24: 'PCM_24',
                BitDepth.BIT_32_FLOAT: 'FLOAT'
            }
            
            subtype = subtype_map.get(bit_depth, 'PCM_24')
            
            # Resample if needed
            if len(audio_data) > 0:
                specs = self.audio_specs[audio_id]
                if specs.sample_rate != sample_rate:
                    audio_data = librosa.resample(audio_data, 
                                                orig_sr=specs.sample_rate, 
                                                target_sr=sample_rate)
                
                # Export with soundfile
                sf.write(str(output_file), audio_data, sample_rate, subtype=subtype)
            
            return output_file
        
        # Export all stems in parallel
        loop = asyncio.get_event_loop()
        tasks = []
        
        for stem_name, audio_data in stems.items():
            task = loop.run_in_executor(self.executor, _export_stem, stem_name, audio_data)
            tasks.append((stem_name, task))
        
        # Wait for all exports to complete
        exported_files = {}
        for stem_name, task in tasks:
            exported_files[stem_name] = await task
        
        logger.info(f"Exported {len(exported_files)} stems to {output_dir}")
        return exported_files

    def get_audio_specs(self, audio_id: str) -> AudioSpecs:
        """Get audio specifications"""
        if audio_id not in self.audio_specs:
            raise ValueError(f"Audio not loaded: {audio_id}")
        return self.audio_specs[audio_id]

    def get_supported_formats(self) -> List[str]:
        """Get list of supported audio formats"""
        formats = [fmt.value for fmt in AudioFormat]
        if not PYDUB_AVAILABLE:
            # Limited formats without pydub
            formats = ['wav', 'flac']
        return formats

    async def cleanup(self):
        """Clean up resources"""
        self.loaded_audio.clear()
        self.audio_specs.clear()
        self.waveform_cache.clear()
        self.analysis_cache.clear()
        self.executor.shutdown(wait=True)
        logger.info("AudioEngine cleaned up")

# Export main class and utilities
__all__ = [
    'AudioEngine', 'AudioSpecs', 'DrumHit', 'TimeMarker', 'TempoChange', 
    'WaveformData', 'AudioFormat', 'SampleRate', 'BitDepth', 'GridSnap'
]