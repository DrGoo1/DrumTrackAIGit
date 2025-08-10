#!/usr/bin/env python3
"""
ML Drum Articulation Trainer
Uses existing sample/clip database to train machine learning models for drum articulation recognition
"""

import json
import numpy as np
import librosa
import soundfile as sf
from pathlib import Path
import logging
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import StandardScaler
import pickle
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MLDrumArticulationTrainer:
    """Train ML models using sample database for drum articulation recognition"""
    
    def __init__(self, sample_database_path="D:/DrumTracKAI_v1.1.10/sample_database"):
        self.sample_database_path = Path(sample_database_path)
        self.models = {}
        self.scalers = {}
        self.feature_extractors = {}
        self.training_data = {}
        
        # Create necessary directories
        self.models_dir = self.sample_database_path / "trained_models"
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Define articulation types for each drum
        self.articulation_types = {
            'snare': ['ghost_note', 'rim_shot', 'normal_hit', 'cross_stick', 'flam'],
            'hihat': ['open', 'closed', 'foot', 'half_open', 'splash'],
            'ride': ['bell', 'rim', 'bow', 'crash_ride', 'choke'],
            'crash': ['normal', 'choke', 'splash', 'bell', 'edge'],
            'kick': ['normal', 'double_kick', 'heel', 'toe', 'muffled']
        }
        
        logger.info("ML Drum Articulation Trainer initialized")
    
    def scan_sample_database(self):
        """Scan the sample database and organize samples by drum type and articulation"""
        
        logger.info("Scanning sample database...")
        
        sample_data = {}
        
        # Look for common sample database structures
        possible_paths = [
            self.sample_database_path,
            self.sample_database_path / "samples",
            self.sample_database_path / "clips",
            Path("H:/Drum_Analysis/Analytic_Tools/sample_database"),
            Path("D:/DrumTracKAI_v1.1.10/audio_samples")
        ]
        
        for base_path in possible_paths:
            if base_path.exists():
                logger.info(f"Scanning: {base_path}")
                self._scan_directory_structure(base_path, sample_data)
        
        # If no samples found, create synthetic training data structure
        if not sample_data:
            logger.warning("No sample database found, creating example structure")
            sample_data = self._create_example_structure()
        
        self.training_data = sample_data
        
        logger.info(f"Found samples for drums: {list(sample_data.keys())}")
        for drum_type, articulations in sample_data.items():
            logger.info(f"  {drum_type}: {list(articulations.keys())}")
        
        return sample_data
    
    def _scan_directory_structure(self, base_path, sample_data):
        """Scan directory structure for organized samples"""
        
        # Common audio extensions
        audio_extensions = {'.wav', '.mp3', '.flac', '.aiff', '.m4a'}
        
        for drum_type in ['snare', 'hihat', 'ride', 'crash', 'kick', 'toms']:
            drum_path = base_path / drum_type
            if drum_path.exists():
                sample_data[drum_type] = {}
                
                # Look for articulation subdirectories
                for articulation in self.articulation_types.get(drum_type, ['normal']):
                    articulation_path = drum_path / articulation
                    if articulation_path.exists():
                        # Find audio files
                        audio_files = []
                        for ext in audio_extensions:
                            audio_files.extend(articulation_path.glob(f"*{ext}"))
                        
                        if audio_files:
                            sample_data[drum_type][articulation] = [str(f) for f in audio_files]
                
                # Also look for files with articulation in filename
                for file_path in drum_path.iterdir():
                    if file_path.suffix.lower() in audio_extensions:
                        filename = file_path.stem.lower()
                        
                        # Match articulation types in filename
                        for articulation in self.articulation_types.get(drum_type, ['normal']):
                            if articulation.replace('_', '') in filename or articulation in filename:
                                if drum_type not in sample_data:
                                    sample_data[drum_type] = {}
                                if articulation not in sample_data[drum_type]:
                                    sample_data[drum_type][articulation] = []
                                
                                sample_data[drum_type][articulation].append(str(file_path))
    
    def _create_example_structure(self):
        """Create example structure for demonstration"""
        
        logger.info("Creating example training structure...")
        
        # This would be replaced with actual sample database scanning
        return {
            'snare': {
                'ghost_note': [],
                'rim_shot': [],
                'normal_hit': [],
                'cross_stick': []
            },
            'hihat': {
                'open': [],
                'closed': [],
                'foot': [],
                'half_open': []
            },
            'ride': {
                'bell': [],
                'rim': [],
                'bow': []
            },
            'crash': {
                'normal': [],
                'choke': [],
                'splash': []
            }
        }
    
    def extract_features_from_samples(self, drum_type):
        """Extract features from all samples of a specific drum type"""
        
        logger.info(f"Extracting features for {drum_type}...")
        
        features = []
        labels = []
        
        drum_samples = self.training_data.get(drum_type, {})
        
        for articulation, sample_files in drum_samples.items():
            logger.info(f"  Processing {articulation}: {len(sample_files)} samples")
            
            for sample_file in sample_files:
                try:
                    # Load audio sample
                    y, sr = librosa.load(sample_file, sr=44100, duration=2.0)
                    
                    if len(y) < 1000:  # Skip very short samples
                        continue
                    
                    # Extract comprehensive features
                    sample_features = self._extract_comprehensive_features(y, sr, drum_type)
                    
                    features.append(sample_features)
                    labels.append(articulation)
                    
                except Exception as e:
                    logger.warning(f"Error processing {sample_file}: {e}")
                    continue
        
        if not features:
            logger.warning(f"No features extracted for {drum_type}")
            return None, None
        
        # Convert to numpy arrays
        X = np.array(features)
        y = np.array(labels)
        
        logger.info(f"Extracted {len(features)} feature vectors for {drum_type}")
        logger.info(f"Feature dimensions: {X.shape}")
        logger.info(f"Unique labels: {np.unique(y)}")
        
        return X, y
    
    def _extract_comprehensive_features(self, y, sr, drum_type):
        """Extract comprehensive features for ML training"""
        
        features = []
        
        # Basic audio features
        features.extend([
            np.mean(y),                    # Mean amplitude
            np.std(y),                     # Standard deviation
            np.max(np.abs(y)),            # Peak amplitude
            np.sqrt(np.mean(y**2))        # RMS energy
        ])
        
        # Spectral features
        stft = librosa.stft(y)
        magnitude = np.abs(stft)
        
        # Spectral centroid (brightness)
        spectral_centroids = librosa.feature.spectral_centroid(S=magnitude, sr=sr)
        features.extend([
            np.mean(spectral_centroids),
            np.std(spectral_centroids)
        ])
        
        # Spectral rolloff
        spectral_rolloff = librosa.feature.spectral_rolloff(S=magnitude, sr=sr)
        features.extend([
            np.mean(spectral_rolloff),
            np.std(spectral_rolloff)
        ])
        
        # Spectral bandwidth
        spectral_bandwidth = librosa.feature.spectral_bandwidth(S=magnitude, sr=sr)
        features.extend([
            np.mean(spectral_bandwidth),
            np.std(spectral_bandwidth)
        ])
        
        # Zero crossing rate
        zcr = librosa.feature.zero_crossing_rate(y)
        features.extend([
            np.mean(zcr),
            np.std(zcr)
        ])
        
        # MFCC features (first 13 coefficients)
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        for i in range(13):
            features.extend([
                np.mean(mfccs[i]),
                np.std(mfccs[i])
            ])
        
        # Drum-specific features
        if drum_type == 'snare':
            features.extend(self._extract_snare_specific_features(y, sr))
        elif drum_type == 'hihat':
            features.extend(self._extract_hihat_specific_features(y, sr))
        elif drum_type == 'ride':
            features.extend(self._extract_ride_specific_features(y, sr))
        elif drum_type == 'crash':
            features.extend(self._extract_crash_specific_features(y, sr))
        
        return features
    
    def _extract_snare_specific_features(self, y, sr):
        """Extract snare-specific features"""
        
        features = []
        
        # High frequency content (for rim shots)
        stft = librosa.stft(y)
        freqs = librosa.fft_frequencies(sr=sr)
        high_freq_mask = freqs > 5000
        high_freq_energy = np.mean(np.abs(stft[high_freq_mask, :]))
        total_energy = np.mean(np.abs(stft))
        high_freq_ratio = high_freq_energy / (total_energy + 1e-10)
        
        # Attack characteristics
        attack_time = self._calculate_attack_time(y, sr)
        attack_sharpness = self._calculate_attack_sharpness(y)
        
        # Noise characteristics (for ghost notes)
        noise_floor = np.percentile(np.abs(y), 10)
        
        features.extend([
            high_freq_ratio,
            attack_time,
            attack_sharpness,
            noise_floor
        ])
        
        return features
    
    def _extract_hihat_specific_features(self, y, sr):
        """Extract hihat-specific features"""
        
        features = []
        
        # Decay characteristics
        envelope = np.abs(y)
        decay_time = self._calculate_decay_time(envelope, sr)
        
        # High frequency content (brightness)
        stft = librosa.stft(y)
        freqs = librosa.fft_frequencies(sr=sr)
        high_freq_mask = freqs > 8000
        high_freq_energy = np.mean(np.abs(stft[high_freq_mask, :]))
        total_energy = np.mean(np.abs(stft))
        brightness = high_freq_energy / (total_energy + 1e-10)
        
        # Sustain vs transient characteristics
        sustain_ratio = self._calculate_sustain_ratio(envelope)
        
        features.extend([
            decay_time,
            brightness,
            sustain_ratio
        ])
        
        return features
    
    def _extract_ride_specific_features(self, y, sr):
        """Extract ride-specific features"""
        
        features = []
        
        # Fundamental frequency (for bell detection)
        fundamental_freq = self._detect_fundamental_frequency(y, sr)
        
        # Sustain characteristics
        envelope = np.abs(y)
        sustain_time = self._calculate_sustain_time(envelope, sr)
        
        # Harmonic content
        harmonic_ratio = self._calculate_harmonic_ratio(y, sr)
        
        features.extend([
            fundamental_freq,
            sustain_time,
            harmonic_ratio
        ])
        
        return features
    
    def _extract_crash_specific_features(self, y, sr):
        """Extract crash-specific features"""
        
        features = []
        
        # Spectral spread
        stft = librosa.stft(y)
        spectral_bandwidth = librosa.feature.spectral_bandwidth(S=np.abs(stft))
        spectral_spread = np.mean(spectral_bandwidth)
        
        # Shimmer (spectral variation)
        spectral_centroids = librosa.feature.spectral_centroid(S=np.abs(stft))
        shimmer = np.std(spectral_centroids)
        
        # Crash duration
        envelope = np.abs(y)
        crash_duration = self._calculate_crash_duration(envelope, sr)
        
        features.extend([
            spectral_spread,
            shimmer,
            crash_duration
        ])
        
        return features
    
    def train_articulation_model(self, drum_type):
        """Train ML model for specific drum articulation detection"""
        
        logger.info(f"Training articulation model for {drum_type}...")
        
        # Extract features
        X, y = self.extract_features_from_samples(drum_type)
        
        if X is None or len(X) < 10:
            logger.warning(f"Insufficient training data for {drum_type}")
            return None
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Try multiple models
        models = {
            'RandomForest': RandomForestClassifier(n_estimators=100, random_state=42),
            'GradientBoosting': GradientBoostingClassifier(n_estimators=100, random_state=42)
        }
        
        best_model = None
        best_score = 0
        best_model_name = None
        
        for model_name, model in models.items():
            # Train model
            model.fit(X_train_scaled, y_train)
            
            # Evaluate
            train_score = model.score(X_train_scaled, y_train)
            test_score = model.score(X_test_scaled, y_test)
            
            # Cross-validation
            cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5)
            cv_mean = np.mean(cv_scores)
            
            logger.info(f"  {model_name}:")
            logger.info(f"    Train Score: {train_score:.3f}")
            logger.info(f"    Test Score: {test_score:.3f}")
            logger.info(f"    CV Score: {cv_mean:.3f} (+/- {np.std(cv_scores)*2:.3f})")
            
            if cv_mean > best_score:
                best_score = cv_mean
                best_model = model
                best_model_name = model_name
        
        if best_model is None:
            logger.error(f"Failed to train model for {drum_type}")
            return None
        
        logger.info(f"Best model for {drum_type}: {best_model_name} (CV: {best_score:.3f})")
        
        # Final evaluation
        y_pred = best_model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        
        logger.info(f"Final test accuracy: {accuracy:.3f}")
        logger.info("Classification Report:")
        logger.info(f"\n{classification_report(y_test, y_pred)}")
        
        # Save model and scaler
        model_data = {
            'model': best_model,
            'scaler': scaler,
            'model_name': best_model_name,
            'accuracy': accuracy,
            'feature_names': self._get_feature_names(drum_type),
            'articulation_types': list(np.unique(y)),
            'training_date': datetime.now().isoformat()
        }
        
        model_file = self.models_dir / f"{drum_type}_articulation_model.pkl"
        with open(model_file, 'wb') as f:
            pickle.dump(model_data, f)
        
        logger.info(f"Model saved: {model_file}")
        
        # Store in memory
        self.models[drum_type] = best_model
        self.scalers[drum_type] = scaler
        
        return model_data
    
    def train_all_models(self):
        """Train models for all available drum types"""
        
        logger.info("Training models for all drum types...")
        
        # Scan database first
        self.scan_sample_database()
        
        trained_models = {}
        
        for drum_type in self.training_data.keys():
            logger.info(f"\n{'='*50}")
            logger.info(f"Training {drum_type} model...")
            logger.info(f"{'='*50}")
            
            model_data = self.train_articulation_model(drum_type)
            if model_data:
                trained_models[drum_type] = model_data
        
        # Save training summary
        summary = {
            'training_date': datetime.now().isoformat(),
            'trained_models': list(trained_models.keys()),
            'model_accuracies': {k: v['accuracy'] for k, v in trained_models.items()},
            'total_models': len(trained_models)
        }
        
        summary_file = self.models_dir / "training_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"\nTraining complete! Summary saved: {summary_file}")
        logger.info(f"Trained {len(trained_models)} models")
        
        return trained_models
    
    def load_trained_models(self):
        """Load all trained models"""
        
        logger.info("Loading trained models...")
        
        loaded_models = {}
        
        for model_file in self.models_dir.glob("*_articulation_model.pkl"):
            drum_type = model_file.stem.replace('_articulation_model', '')
            
            try:
                with open(model_file, 'rb') as f:
                    model_data = pickle.load(f)
                
                self.models[drum_type] = model_data['model']
                self.scalers[drum_type] = model_data['scaler']
                loaded_models[drum_type] = model_data
                
                logger.info(f"Loaded {drum_type} model (accuracy: {model_data['accuracy']:.3f})")
                
            except Exception as e:
                logger.error(f"Error loading {model_file}: {e}")
        
        logger.info(f"Loaded {len(loaded_models)} models")
        return loaded_models
    
    def predict_articulation(self, audio_file, drum_type):
        """Predict articulation type for audio file"""
        
        if drum_type not in self.models:
            logger.error(f"No trained model for {drum_type}")
            return None
        
        try:
            # Load audio
            y, sr = librosa.load(audio_file, sr=44100)
            
            # Extract features
            features = self._extract_comprehensive_features(y, sr, drum_type)
            features = np.array(features).reshape(1, -1)
            
            # Scale features
            features_scaled = self.scalers[drum_type].transform(features)
            
            # Predict
            prediction = self.models[drum_type].predict(features_scaled)[0]
            probabilities = self.models[drum_type].predict_proba(features_scaled)[0]
            
            # Get class names
            classes = self.models[drum_type].classes_
            
            # Create result
            result = {
                'predicted_articulation': prediction,
                'confidence': np.max(probabilities),
                'all_probabilities': dict(zip(classes, probabilities))
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error predicting articulation: {e}")
            return None
    
    # Helper methods for feature calculation
    def _calculate_attack_time(self, y, sr):
        """Calculate attack time"""
        peak_idx = np.argmax(np.abs(y))
        attack_time = peak_idx / sr
        return min(0.1, attack_time)  # Cap at 100ms
    
    def _calculate_attack_sharpness(self, y):
        """Calculate attack sharpness"""
        if len(y) < 10:
            return 0
        
        peak_idx = np.argmax(np.abs(y))
        if peak_idx < 5:
            return 1.0
        
        rise_segment = y[:peak_idx]
        rise_time = len(rise_segment) / 44100.0
        return max(0, min(1, 1.0 - rise_time * 10))
    
    def _calculate_decay_time(self, envelope, sr):
        """Calculate decay time"""
        if len(envelope) < 10:
            return 0
        
        peak_idx = np.argmax(envelope)
        if peak_idx >= len(envelope) - 5:
            return 0
        
        peak_value = envelope[peak_idx]
        threshold = peak_value * 0.1
        
        decay_segment = envelope[peak_idx:]
        decay_idx = np.where(decay_segment < threshold)[0]
        
        if len(decay_idx) > 0:
            return min(2.0, decay_idx[0] / sr)
        
        return 2.0
    
    def _calculate_sustain_time(self, envelope, sr):
        """Calculate sustain time"""
        return self._calculate_decay_time(envelope, sr)
    
    def _calculate_sustain_ratio(self, envelope):
        """Calculate sustain vs attack ratio"""
        if len(envelope) < 10:
            return 0
        
        peak_idx = np.argmax(envelope)
        attack_energy = np.sum(envelope[:peak_idx]) if peak_idx > 0 else 0
        sustain_energy = np.sum(envelope[peak_idx:])
        
        total_energy = attack_energy + sustain_energy
        return sustain_energy / (total_energy + 1e-10)
    
    def _detect_fundamental_frequency(self, y, sr):
        """Detect fundamental frequency"""
        try:
            # Use autocorrelation
            correlation = np.correlate(y, y, mode='full')
            correlation = correlation[len(correlation)//2:]
            
            # Find first peak
            peaks = []
            for i in range(1, len(correlation)-1):
                if correlation[i] > correlation[i-1] and correlation[i] > correlation[i+1]:
                    if correlation[i] > np.max(correlation) * 0.3:
                        peaks.append(i)
            
            if peaks:
                period = peaks[0]
                fundamental_freq = sr / period if period > 0 else 0
                return min(8000, fundamental_freq)
            
            return 0
            
        except:
            return 0
    
    def _calculate_harmonic_ratio(self, y, sr):
        """Calculate harmonic to noise ratio"""
        try:
            # Simple harmonic analysis
            stft = librosa.stft(y)
            magnitude = np.abs(stft)
            
            # Find peaks in spectrum
            spectrum = np.mean(magnitude, axis=1)
            peaks = []
            for i in range(1, len(spectrum)-1):
                if spectrum[i] > spectrum[i-1] and spectrum[i] > spectrum[i+1]:
                    if spectrum[i] > np.max(spectrum) * 0.1:
                        peaks.append(spectrum[i])
            
            harmonic_energy = sum(peaks) if peaks else 0
            total_energy = np.sum(spectrum)
            
            return harmonic_energy / (total_energy + 1e-10)
            
        except:
            return 0
    
    def _calculate_crash_duration(self, envelope, sr):
        """Calculate crash duration"""
        # Find where envelope drops to 5% of peak
        peak_value = np.max(envelope)
        threshold = peak_value * 0.05
        
        duration_samples = len(envelope)
        for i in range(len(envelope)-1, 0, -1):
            if envelope[i] > threshold:
                duration_samples = i
                break
        
        return duration_samples / sr
    
    def _get_feature_names(self, drum_type):
        """Get feature names for documentation"""
        
        base_features = [
            'mean_amplitude', 'std_amplitude', 'peak_amplitude', 'rms_energy',
            'spectral_centroid_mean', 'spectral_centroid_std',
            'spectral_rolloff_mean', 'spectral_rolloff_std',
            'spectral_bandwidth_mean', 'spectral_bandwidth_std',
            'zcr_mean', 'zcr_std'
        ]
        
        # MFCC features
        for i in range(13):
            base_features.extend([f'mfcc_{i}_mean', f'mfcc_{i}_std'])
        
        # Drum-specific features
        if drum_type == 'snare':
            base_features.extend(['high_freq_ratio', 'attack_time', 'attack_sharpness', 'noise_floor'])
        elif drum_type == 'hihat':
            base_features.extend(['decay_time', 'brightness', 'sustain_ratio'])
        elif drum_type == 'ride':
            base_features.extend(['fundamental_freq', 'sustain_time', 'harmonic_ratio'])
        elif drum_type == 'crash':
            base_features.extend(['spectral_spread', 'shimmer', 'crash_duration'])
        
        return base_features

def main():
    """Main training function"""
    
    print("ML Drum Articulation Trainer")
    print("=" * 40)
    
    # Initialize trainer
    trainer = MLDrumArticulationTrainer()
    
    # Scan database
    print("\nScanning sample database...")
    sample_data = trainer.scan_sample_database()
    
    if not any(sample_data.values()):
        print("No samples found in database.")
        print("Please organize samples in the following structure:")
        print("sample_database/")
        print("  snare/")
        print("    ghost_note/")
        print("    rim_shot/")
        print("    normal_hit/")
        print("  hihat/")
        print("    open/")
        print("    closed/")
        print("    foot/")
        print("  etc...")
        return
    
    # Train all models
    print("\nTraining ML models...")
    trained_models = trainer.train_all_models()
    
    print(f"\nTraining complete!")
    print(f"Trained {len(trained_models)} models")
    print(f"Models saved in: {trainer.models_dir}")

if __name__ == "__main__":
    main()
