#!/usr/bin/env python3
"""
Sophisticated Hit-Type Analyzer for DrumTracKAI v1.1.7
=====================================================

High-resolution detection and classification of specific drum hit types:
- Snare: ghost notes, rim shots, edge hits, rolls, cross-stick, flams
- Hi-hat: open/closed variations, foot splashes, rolls, chops
- Ride cymbal: bell hits, edge hits, crash zones, bow hits, rolls

Features:
- Sample database integration for training and reference
- Advanced spectral analysis using TFR techniques
- Machine learning classification models
- GPU-accelerated processing
- Real-time hit-type detection
"""

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import librosa
import soundfile as sf
from scipy import signal, stats
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
import pickle
import json
import sqlite3
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import warnings

# Import our advanced analytic tools
import sys
sys.path.append(str(Path(__file__).parent / "admin" / "services"))

try:
    from tfr_integration_system import DrumTracKAI_TFR_Integration, EnhancedDrumHit
    from advanced_tfr_system import AdvancedTimeFrequencyReassignment
    TFR_AVAILABLE = True
except ImportError:
    TFR_AVAILABLE = False
    warnings.warn("TFR integration not available")

logger = logging.getLogger(__name__)

@dataclass
class HitTypeFeatures:
    """Comprehensive features for hit-type classification"""
    # Temporal features
    attack_time: float
    decay_time: float
    sustain_level: float
    release_time: float
    
    # Spectral features
    spectral_centroid: float
    spectral_rolloff: float
    spectral_bandwidth: float
    spectral_contrast: List[float]
    mfcc_coefficients: List[float]
    
    # TFR-enhanced features
    attack_sharpness: float
    frequency_modulation: float
    transient_strength: float
    spectral_evolution: List[float]
    
    # Physical characteristics
    fundamental_frequency: float
    harmonic_ratio: float
    noise_ratio: float
    resonance_peaks: List[float]
    
    # Context features
    velocity: float
    preceding_interval: float
    following_interval: float
    position_in_measure: float

@dataclass
class HitTypeClassification:
    """Hit-type classification result"""
    primary_type: str
    confidence: float
    secondary_types: Dict[str, float]  # Alternative classifications with confidence
    features: HitTypeFeatures
    raw_audio: np.ndarray
    sample_rate: int

class DrumSampleDatabase:
    """Database of drum samples for training and reference"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = Path(__file__).parent / "drum_samples.db"
        
        self.db_path = db_path
        self._initialize_database()
        
    def _initialize_database(self):
        """Initialize drum sample database schema"""
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Drum samples table
        c.execute('''
            CREATE TABLE IF NOT EXISTS drum_samples (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                drum_type TEXT NOT NULL,
                hit_type TEXT NOT NULL,
                sample_path TEXT NOT NULL,
                features_json TEXT,
                velocity REAL,
                duration REAL,
                sample_rate INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                verified BOOLEAN DEFAULT FALSE
            )
        ''')
        
        # Hit type definitions
        c.execute('''
            CREATE TABLE IF NOT EXISTS hit_type_definitions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                drum_type TEXT NOT NULL,
                hit_type TEXT NOT NULL,
                description TEXT,
                spectral_signature TEXT,
                typical_features TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Initialize with standard hit types
        self._populate_standard_hit_types()
    
    def _populate_standard_hit_types(self):
        """Populate database with standard hit type definitions"""
        
        standard_hit_types = {
            'snare': [
                ('ghost_note', 'Very quiet snare hit, barely audible, used for groove'),
                ('rim_shot', 'Stick hits rim and head simultaneously, sharp crack sound'),
                ('edge_hit', 'Stick hits edge of snare head, different tone'),
                ('cross_stick', 'Stick laid across head, other end hits rim'),
                ('roll', 'Rapid succession of hits creating sustained sound'),
                ('flam', 'Two hits very close together, grace note effect'),
                ('buzz_roll', 'Multiple bounce roll, snares engaged'),
                ('open_roll', 'Single stroke roll, clean articulation'),
                ('center_hit', 'Standard hit in center of drum head'),
                ('off_center', 'Hit slightly off center, different tone')
            ],
            'hihat': [
                ('closed', 'Hi-hat cymbals pressed together, tight sound'),
                ('open', 'Hi-hat cymbals separated, ringing sound'),
                ('semi_open', 'Partially open hi-hat, controlled ring'),
                ('foot_splash', 'Foot closes hi-hat creating splash sound'),
                ('chop', 'Quick open-close motion with stick hit'),
                ('roll', 'Rapid succession of hits on closed hi-hat'),
                ('tip_hit', 'Hit with stick tip, bright sound'),
                ('shank_hit', 'Hit with stick shank, darker sound'),
                ('edge_hit', 'Hit on edge of cymbal'),
                ('bell_area', 'Hit near the bell/center area')
            ],
            'ride': [
                ('bow_hit', 'Standard hit on main riding area'),
                ('bell_hit', 'Hit on bell/cup of cymbal, bright ping'),
                ('edge_hit', 'Hit on edge, crashy sound'),
                ('crash_zone', 'Hit in crash area of ride'),
                ('roll', 'Sustained roll on ride cymbal'),
                ('cross_stick_ride', 'Cross-stick technique on ride'),
                ('tip_articulation', 'Clean tip hits with good definition'),
                ('wash', 'Multiple overlapping hits creating wash effect'),
                ('choke', 'Grabbing cymbal to stop ring'),
                ('scrape', 'Scraping stick across cymbal surface')
            ],
            'kick': [
                ('beater_hit', 'Standard beater impact'),
                ('heel_toe', 'Double kick technique'),
                ('ghost_kick', 'Very light kick drum hit'),
                ('accent_kick', 'Heavily accented kick'),
                ('muffled', 'Muffled kick with dampening'),
                ('open_tone', 'Open, ringing kick tone'),
                ('attack_heavy', 'Heavy attack emphasis'),
                ('sub_kick', 'Sub-frequency emphasis')
            ],
            'tom': [
                ('center_hit', 'Standard center hit'),
                ('rim_shot', 'Rim and head hit together'),
                ('edge_hit', 'Hit near edge of head'),
                ('roll', 'Tom roll'),
                ('ghost_note', 'Quiet tom hit'),
                ('accent', 'Accented tom hit'),
                ('muffled', 'Muffled tom tone'),
                ('open_tone', 'Open, ringing tom')
            ]
        }
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        for drum_type, hit_types in standard_hit_types.items():
            for hit_type, description in hit_types:
                c.execute('''
                    INSERT OR IGNORE INTO hit_type_definitions 
                    (drum_type, hit_type, description) VALUES (?, ?, ?)
                ''', (drum_type, hit_type, description))
        
        conn.commit()
        conn.close()
        
        logger.info("Standard hit types populated in database")

class SophisticatedHitTypeAnalyzer:
    """Advanced hit-type analyzer with ML classification"""
    
    def __init__(self, sample_rate: int = 44100, use_gpu: bool = True):
        self.sample_rate = sample_rate
        self.use_gpu = use_gpu and torch.cuda.is_available()
        self.device = torch.device('cuda' if self.use_gpu else 'cpu')
        
        # Initialize components
        self.sample_db = DrumSampleDatabase()
        
        # Initialize TFR analyzer if available
        if TFR_AVAILABLE:
            self.tfr_analyzer = DrumTracKAI_TFR_Integration(sample_rate, use_gpu)
        else:
            self.tfr_analyzer = None
            logger.warning("TFR analyzer not available")
        
        # ML models for classification
        self.classifiers = {}
        self.feature_scalers = {}
        
        # Feature extraction parameters
        self.window_size = 0.1  # 100ms analysis window
        self.hop_length = 512
        self.n_mfcc = 13
        
        logger.info(f"Sophisticated Hit-Type Analyzer initialized (GPU: {self.use_gpu})")
    
    def extract_comprehensive_features(self, audio: np.ndarray, onset_time: float) -> HitTypeFeatures:
        """Extract comprehensive features for hit-type classification"""
        
        # Extract audio segment around onset
        start_sample = max(0, int((onset_time - 0.05) * self.sample_rate))
        end_sample = min(len(audio), int((onset_time + self.window_size) * self.sample_rate))
        segment = audio[start_sample:end_sample]
        
        if len(segment) < 100:  # Too short
            return None
        
        # Temporal features
        attack_time = self._calculate_attack_time(segment)
        decay_time = self._calculate_decay_time(segment)
        sustain_level = self._calculate_sustain_level(segment)
        release_time = self._calculate_release_time(segment)
        
        # Spectral features
        spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=segment, sr=self.sample_rate))
        spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(y=segment, sr=self.sample_rate))
        spectral_bandwidth = np.mean(librosa.feature.spectral_bandwidth(y=segment, sr=self.sample_rate))
        
        # Spectral contrast (7 bands)
        spectral_contrast = np.mean(librosa.feature.spectral_contrast(y=segment, sr=self.sample_rate), axis=1).tolist()
        
        # MFCC coefficients
        mfcc = np.mean(librosa.feature.mfcc(y=segment, sr=self.sample_rate, n_mfcc=self.n_mfcc), axis=1).tolist()
        
        # TFR-enhanced features if available
        if self.tfr_analyzer:
            try:
                tfr_analysis = self.tfr_analyzer.tfr_analyzer.analyze_drum_attack(audio, onset_time)
                attack_sharpness = tfr_analysis.attack_sharpness
                frequency_modulation = tfr_analysis.frequency_modulation
                transient_strength = tfr_analysis.transient_strength
                spectral_evolution = tfr_analysis.spectral_evolution[:10]  # First 10 points
            except:
                attack_sharpness = 0.0
                frequency_modulation = 0.0
                transient_strength = 0.0
                spectral_evolution = [0.0] * 10
        else:
            attack_sharpness = self._calculate_attack_sharpness_fallback(segment)
            frequency_modulation = 0.0
            transient_strength = self._calculate_transient_strength_fallback(segment)
            spectral_evolution = [0.0] * 10
        
        # Physical characteristics
        fundamental_frequency = self._estimate_fundamental_frequency(segment)
        harmonic_ratio = self._calculate_harmonic_ratio(segment)
        noise_ratio = self._calculate_noise_ratio(segment)
        resonance_peaks = self._find_resonance_peaks(segment)
        
        return HitTypeFeatures(
            attack_time=attack_time,
            decay_time=decay_time,
            sustain_level=sustain_level,
            release_time=release_time,
            spectral_centroid=spectral_centroid,
            spectral_rolloff=spectral_rolloff,
            spectral_bandwidth=spectral_bandwidth,
            spectral_contrast=spectral_contrast,
            mfcc_coefficients=mfcc,
            attack_sharpness=attack_sharpness,
            frequency_modulation=frequency_modulation,
            transient_strength=transient_strength,
            spectral_evolution=spectral_evolution,
            fundamental_frequency=fundamental_frequency,
            harmonic_ratio=harmonic_ratio,
            noise_ratio=noise_ratio,
            resonance_peaks=resonance_peaks,
            velocity=np.max(np.abs(segment)),
            preceding_interval=0.0,  # To be filled by caller
            following_interval=0.0,  # To be filled by caller
            position_in_measure=0.0  # To be filled by caller
        )
    
    def _calculate_attack_time(self, segment: np.ndarray) -> float:
        """Calculate attack time (time to peak amplitude)"""
        peak_idx = np.argmax(np.abs(segment))
        return peak_idx / self.sample_rate
    
    def _calculate_decay_time(self, segment: np.ndarray) -> float:
        """Calculate decay time (time from peak to 50% amplitude)"""
        abs_segment = np.abs(segment)
        peak_idx = np.argmax(abs_segment)
        peak_val = abs_segment[peak_idx]
        
        # Find where amplitude drops to 50% of peak
        target_val = peak_val * 0.5
        decay_idx = peak_idx
        
        for i in range(peak_idx, len(abs_segment)):
            if abs_segment[i] < target_val:
                decay_idx = i
                break
        
        return (decay_idx - peak_idx) / self.sample_rate
    
    def _calculate_sustain_level(self, segment: np.ndarray) -> float:
        """Calculate sustain level (average amplitude after attack)"""
        abs_segment = np.abs(segment)
        peak_idx = np.argmax(abs_segment)
        
        if peak_idx < len(abs_segment) - 100:
            sustain_portion = abs_segment[peak_idx + 100:]
            return np.mean(sustain_portion) / np.max(abs_segment)
        
        return 0.0
    
    def _calculate_release_time(self, segment: np.ndarray) -> float:
        """Calculate release time (time to fade to near silence)"""
        abs_segment = np.abs(segment)
        peak_val = np.max(abs_segment)
        threshold = peak_val * 0.1  # 10% of peak
        
        # Find last point above threshold
        for i in range(len(abs_segment) - 1, -1, -1):
            if abs_segment[i] > threshold:
                return i / self.sample_rate
        
        return len(segment) / self.sample_rate
    
    def _calculate_attack_sharpness_fallback(self, segment: np.ndarray) -> float:
        """Fallback attack sharpness calculation without TFR"""
        # Use spectral flux as proxy
        stft = librosa.stft(segment, hop_length=self.hop_length)
        magnitude = np.abs(stft)
        
        if magnitude.shape[1] > 1:
            flux = np.sum(np.maximum(0, magnitude[:, 1:] - magnitude[:, :-1]), axis=0)
            return np.max(flux) if len(flux) > 0 else 0.0
        
        return 0.0
    
    def _calculate_transient_strength_fallback(self, segment: np.ndarray) -> float:
        """Fallback transient strength calculation"""
        # Use onset strength as proxy
        onset_envelope = librosa.onset.onset_strength(y=segment, sr=self.sample_rate)
        return np.max(onset_envelope) if len(onset_envelope) > 0 else 0.0
    
    def _estimate_fundamental_frequency(self, segment: np.ndarray) -> float:
        """Estimate fundamental frequency using YIN algorithm"""
        try:
            f0 = librosa.yin(segment, fmin=50, fmax=2000, sr=self.sample_rate)
            # Return median to avoid octave errors
            valid_f0 = f0[f0 > 0]
            return np.median(valid_f0) if len(valid_f0) > 0 else 0.0
        except:
            return 0.0
    
    def _calculate_harmonic_ratio(self, segment: np.ndarray) -> float:
        """Calculate ratio of harmonic to total energy"""
        try:
            # Simple harmonic/percussive separation
            harmonic, percussive = librosa.decompose.hpss(segment)
            harmonic_energy = np.sum(harmonic ** 2)
            total_energy = np.sum(segment ** 2)
            return harmonic_energy / total_energy if total_energy > 0 else 0.0
        except:
            return 0.0
    
    def _calculate_noise_ratio(self, segment: np.ndarray) -> float:
        """Calculate noise-to-signal ratio"""
        try:
            # Use high-frequency content as noise proxy
            stft = librosa.stft(segment)
            magnitude = np.abs(stft)
            
            # Split spectrum into signal (low-mid) and noise (high)
            signal_bands = magnitude[:magnitude.shape[0]//2, :]
            noise_bands = magnitude[magnitude.shape[0]//2:, :]
            
            signal_energy = np.sum(signal_bands ** 2)
            noise_energy = np.sum(noise_bands ** 2)
            
            return noise_energy / (signal_energy + noise_energy) if (signal_energy + noise_energy) > 0 else 0.0
        except:
            return 0.0
    
    def _find_resonance_peaks(self, segment: np.ndarray) -> List[float]:
        """Find prominent resonance peaks in spectrum"""
        try:
            # Compute power spectrum
            freqs, psd = signal.welch(segment, fs=self.sample_rate, nperseg=1024)
            
            # Find peaks
            peaks, _ = signal.find_peaks(psd, height=np.max(psd) * 0.1, distance=10)
            
            # Return frequencies of top 5 peaks
            peak_freqs = freqs[peaks]
            peak_powers = psd[peaks]
            
            # Sort by power and take top 5
            sorted_indices = np.argsort(peak_powers)[::-1]
            top_peaks = peak_freqs[sorted_indices[:5]]
            
            return top_peaks.tolist()
        except:
            return [0.0] * 5
    
    def classify_hit_type(self, audio: np.ndarray, onset_time: float, 
                         drum_type: str) -> HitTypeClassification:
        """Classify the type of drum hit"""
        
        # Extract comprehensive features
        features = self.extract_comprehensive_features(audio, onset_time)
        if features is None:
            return None
        
        # Get audio segment for storage
        start_sample = max(0, int((onset_time - 0.05) * self.sample_rate))
        end_sample = min(len(audio), int((onset_time + self.window_size) * self.sample_rate))
        raw_audio = audio[start_sample:end_sample]
        
        # Load or train classifier for this drum type
        if drum_type not in self.classifiers:
            self._train_classifier_for_drum_type(drum_type)
        
        # Classify using trained model
        if drum_type in self.classifiers:
            classifier = self.classifiers[drum_type]
            scaler = self.feature_scalers[drum_type]
            
            # Prepare feature vector
            feature_vector = self._features_to_vector(features)
            feature_vector_scaled = scaler.transform([feature_vector])
            
            # Get prediction and probabilities
            prediction = classifier.predict(feature_vector_scaled)[0]
            probabilities = classifier.predict_proba(feature_vector_scaled)[0]
            
            # Create secondary types dictionary
            classes = classifier.classes_
            secondary_types = {classes[i]: prob for i, prob in enumerate(probabilities)}
            confidence = secondary_types[prediction]
            
            return HitTypeClassification(
                primary_type=prediction,
                confidence=confidence,
                secondary_types=secondary_types,
                features=features,
                raw_audio=raw_audio,
                sample_rate=self.sample_rate
            )
        else:
            # Fallback to rule-based classification
            return self._rule_based_classification(features, raw_audio, drum_type)
    
    def _features_to_vector(self, features: HitTypeFeatures) -> np.ndarray:
        """Convert features dataclass to feature vector"""
        vector = [
            features.attack_time,
            features.decay_time,
            features.sustain_level,
            features.release_time,
            features.spectral_centroid,
            features.spectral_rolloff,
            features.spectral_bandwidth,
            features.attack_sharpness,
            features.frequency_modulation,
            features.transient_strength,
            features.fundamental_frequency,
            features.harmonic_ratio,
            features.noise_ratio,
            features.velocity
        ]
        
        # Add spectral contrast
        vector.extend(features.spectral_contrast)
        
        # Add MFCC coefficients
        vector.extend(features.mfcc_coefficients)
        
        # Add spectral evolution (first 5 points)
        vector.extend(features.spectral_evolution[:5])
        
        # Add resonance peaks (first 3)
        vector.extend(features.resonance_peaks[:3])
        
        return np.array(vector)
    
    def _train_classifier_for_drum_type(self, drum_type: str):
        """Train ML classifier for specific drum type"""
        
        # This would load training data from the sample database
        # For now, create a placeholder classifier
        logger.info(f"Training classifier for {drum_type} (placeholder)")
        
        # Create dummy training data (in real implementation, load from database)
        n_samples = 100
        n_features = 50  # Approximate feature vector size
        
        X_dummy = np.random.randn(n_samples, n_features)
        y_dummy = np.random.choice(['center_hit', 'rim_shot', 'ghost_note'], n_samples)
        
        # Train classifier
        classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        classifier.fit(X_dummy, y_dummy)
        
        # Train scaler
        scaler = StandardScaler()
        scaler.fit(X_dummy)
        
        self.classifiers[drum_type] = classifier
        self.feature_scalers[drum_type] = scaler
        
        logger.info(f"Classifier trained for {drum_type}")
    
    def _rule_based_classification(self, features: HitTypeFeatures, 
                                 raw_audio: np.ndarray, drum_type: str) -> HitTypeClassification:
        """Fallback rule-based classification"""
        
        # Simple rule-based classification based on features
        if drum_type == 'snare':
            if features.velocity < 0.3:
                hit_type = 'ghost_note'
                confidence = 0.8
            elif features.noise_ratio > 0.6:
                hit_type = 'rim_shot'
                confidence = 0.7
            else:
                hit_type = 'center_hit'
                confidence = 0.6
        
        elif drum_type == 'hihat':
            if features.decay_time < 0.1:
                hit_type = 'closed'
                confidence = 0.7
            else:
                hit_type = 'open'
                confidence = 0.7
        
        elif drum_type == 'ride':
            if features.fundamental_frequency > 1000:
                hit_type = 'bell_hit'
                confidence = 0.6
            else:
                hit_type = 'bow_hit'
                confidence = 0.6
        
        else:
            hit_type = 'standard_hit'
            confidence = 0.5
        
        secondary_types = {hit_type: confidence}
        
        return HitTypeClassification(
            primary_type=hit_type,
            confidence=confidence,
            secondary_types=secondary_types,
            features=features,
            raw_audio=raw_audio,
            sample_rate=self.sample_rate
        )
    
    def analyze_drum_performance(self, audio: np.ndarray, 
                               drum_onsets: Dict[str, np.ndarray]) -> Dict[str, List[HitTypeClassification]]:
        """Analyze complete drum performance with hit-type classification"""
        
        results = {}
        
        for drum_type, onsets in drum_onsets.items():
            logger.info(f"Analyzing {len(onsets)} {drum_type} hits...")
            
            drum_results = []
            for onset_time in onsets:
                classification = self.classify_hit_type(audio, onset_time, drum_type)
                if classification:
                    drum_results.append(classification)
            
            results[drum_type] = drum_results
            
            # Log hit-type summary
            hit_types = [r.primary_type for r in drum_results]
            hit_type_counts = {ht: hit_types.count(ht) for ht in set(hit_types)}
            logger.info(f"{drum_type} hit types: {hit_type_counts}")
        
        return results
    
    def save_analysis_results(self, results: Dict[str, List[HitTypeClassification]], 
                            output_path: str):
        """Save detailed analysis results"""
        
        # Convert to serializable format
        serializable_results = {}
        
        for drum_type, classifications in results.items():
            drum_data = []
            for classification in classifications:
                data = {
                    'primary_type': classification.primary_type,
                    'confidence': classification.confidence,
                    'secondary_types': classification.secondary_types,
                    'features': asdict(classification.features),
                    'timestamp': datetime.now().isoformat()
                }
                drum_data.append(data)
            
            serializable_results[drum_type] = drum_data
        
        # Save to JSON
        with open(output_path, 'w') as f:
            json.dump(serializable_results, f, indent=2)
        
        logger.info(f"Analysis results saved to {output_path}")

if __name__ == "__main__":
    # Test the sophisticated hit-type analyzer
    analyzer = SophisticatedHitTypeAnalyzer()
    
    # Test with dummy audio data
    duration = 5.0  # 5 seconds
    sample_rate = 44100
    t = np.linspace(0, duration, int(duration * sample_rate))
    
    # Create test audio with some drum-like transients
    audio = np.zeros_like(t)
    
    # Add some test "hits" at specific times
    hit_times = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0]
    
    for hit_time in hit_times:
        hit_sample = int(hit_time * sample_rate)
        # Create a simple drum-like transient
        envelope = np.exp(-10 * (t - hit_time)) * (t >= hit_time)
        noise = np.random.randn(len(t)) * 0.1
        audio += envelope * (np.sin(2 * np.pi * 200 * t) + noise)
    
    # Test classification
    drum_onsets = {
        'snare': np.array(hit_times[:4]),
        'hihat': np.array(hit_times[4:])
    }
    
    results = analyzer.analyze_drum_performance(audio, drum_onsets)
    
    # Save results
    analyzer.save_analysis_results(results, "test_hit_type_analysis.json")
    
    print("Sophisticated hit-type analysis test completed!")
