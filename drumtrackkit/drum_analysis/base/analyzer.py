# drum_analysis/base/analyzer.py

import os
import numpy as np
import pandas as pd
import librosa
import librosa.display
import matplotlib.pyplot as plt
from scipy.stats import skew, kurtosis
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
import pickle
import logging
from typing import Dict, Tuple, List, Any, Optional, Union
from concurrent.futures import ThreadPoolExecutor, as_completed


class DrumSampleAnalyzer:
    """
    Base analyzer class implementing common functionality for all drum types.
    Part of the Drum Pattern Analysis System.
    """

    def __init__(self, drum_type: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the drum sample analyzer.

        Args:
            drum_type: Type of drum ("kick", "snare", "cymbal", "tom")
            config: Optional configuration parameters
        """
        self.drum_type = drum_type
        self.config = self._initialize_config(config)
        self.logger = self._setup_logging()

    def _initialize_config(self, config):
        """Set up configuration with defaults and custom overrides"""
        # Common configuration across all analyzers
        default_config = {
            'sample_rate': 44100,
            'n_mfcc': 13,
            'database_filename': f"{self.drum_type}_samples_db.csv",
            'model_filename': f"{self.drum_type}_classifier_model.pkl",
            'temp_dir': "./temp",
            'batch_size': 20,
            'feature_precision': 6,
        }

        if config:
            default_config.update(config)
        return default_config

    def _setup_logging(self):
        """Set up logging for this analyzer"""
        logger = logging.getLogger(f"{self.drum_type}_analyzer")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def load_database(self) -> pd.DataFrame:
        """
        Load the drum samples database or create a new one if it doesn't exist

        Returns:
            pd.DataFrame: Database of drum samples and features
        """
        if os.path.exists(self.config['database_filename']):
            return pd.read_csv(self.config['database_filename'])
        else:
            # Create a minimal DataFrame - subclasses will extend with specific columns
            columns = [
                "file_name", "brand",
                "mfcc_mean", "mfcc_skew", "mfcc_kurtosis",
                "mfcc_delta_mean", "mfcc_delta2_mean",
                "spectral_centroid_mean", "spectral_bandwidth_mean", "spectral_rolloff_mean",
                "spectral_contrast_mean", "attack_time", "decay_time",
                "harmonic_energy", "percussive_energy", "harmonic_percussive_ratio",
                "zero_crossing_rate"
            ]
            return pd.DataFrame(columns=columns)

    def save_to_database(self, record: Dict[str, Any]) -> pd.DataFrame:
        """
        Save a record to the database

        Args:
            record: Dictionary containing sample data and features

        Returns:
            pd.DataFrame: Updated database
        """
        df = self.load_database()
        df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)
        df.to_csv(self.config['database_filename'], index=False)
        return df

    def extract_features(self, audio_data: np.ndarray, sr: int, metadata: Optional[Dict[str, Any]] = None) -> Tuple[
        Dict[str, Any], np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Extract common audio features from the provided audio data.

        Args:
            audio_data: Audio time series
            sr: Sample rate
            metadata: Optional metadata about the sample

        Returns:
            Tuple containing features dictionary and analysis components
        """
        # Compute MFCCs
        mfccs = librosa.feature.mfcc(y=audio_data, sr=sr, n_mfcc=self.config['n_mfcc'])
        mfcc_mean = np.mean(mfccs, axis=1)
        # Higher-order statistics on MFCCs
        mfcc_skew = [skew(mfccs[i, :]) for i in range(mfccs.shape[0])]
        mfcc_kurt = [kurtosis(mfccs[i, :]) for i in range(mfccs.shape[0])]

        # Compute MFCC deltas and delta-deltas
        mfcc_delta = librosa.feature.delta(mfccs)
        mfcc_delta2 = librosa.feature.delta(mfccs, order=2)
        mfcc_delta_mean = np.mean(mfcc_delta, axis=1)
        mfcc_delta2_mean = np.mean(mfcc_delta2, axis=1)

        # Compute spectral centroid, bandwidth, rolloff, and contrast
        centroid = librosa.feature.spectral_centroid(y=audio_data, sr=sr)
        bandwidth = librosa.feature.spectral_bandwidth(y=audio_data, sr=sr)
        rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=sr)
        contrast = librosa.feature.spectral_contrast(y=audio_data, sr=sr)

        # Zero crossing rate
        zcr = librosa.feature.zero_crossing_rate(audio_data)

        # Compute a simple RMS envelope for temporal analysis
        rms = librosa.feature.rms(y=audio_data)[0]
        times = librosa.times_like(rms, sr=sr)

        # Attack time calculation
        if np.any(times <= 0.2):
            attack_time = times[times <= 0.2][np.argmax(rms[times <= 0.2])]
        else:
            attack_time = 0.0

        # Decay time calculation
        decay_time = None
        if len(rms) > 0 and np.max(rms) > 0:
            peak_idx = np.argmax(rms)
            decay_threshold = np.max(rms) * 0.1  # 10% of peak amplitude
            decay_indices = np.where(rms[peak_idx:] <= decay_threshold)[0]
            if len(decay_indices) > 0:
                decay_time = times[decay_indices[0] + peak_idx] - times[peak_idx]
            else:
                decay_time = times[-1] - times[peak_idx]  # Use full remaining time if no decay to threshold

        # Harmonic-percussive source separation
        harmonic, percussive = librosa.effects.hpss(audio_data)
        harmonic_energy = np.mean(harmonic ** 2)
        percussive_energy = np.mean(percussive ** 2)
        harmonic_percussive_ratio = harmonic_energy / percussive_energy if percussive_energy > 0 else 0

        # Base features dictionary
        features = {
            "mfcc_mean": mfcc_mean.tolist(),
            "mfcc_skew": mfcc_skew,
            "mfcc_kurtosis": mfcc_kurt,
            "mfcc_delta_mean": mfcc_delta_mean.tolist(),
            "mfcc_delta2_mean": mfcc_delta2_mean.tolist(),
            "spectral_centroid_mean": float(np.mean(centroid)),
            "spectral_bandwidth_mean": float(np.mean(bandwidth)),
            "spectral_rolloff_mean": float(np.mean(rolloff)),
            "spectral_contrast_mean": float(np.mean(contrast)),
            "attack_time": attack_time,
            "decay_time": decay_time,
            "harmonic_energy": harmonic_energy,
            "percussive_energy": percussive_energy,
            "harmonic_percussive_ratio": harmonic_percussive_ratio,
            "zero_crossing_rate": float(np.mean(zcr)),
        }

        return features, mfccs, mfcc_delta, mfcc_delta2, rms, times, harmonic, percussive

    def analyze_audio_file(self, file_path: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze a single audio file and return features

        Args:
            file_path: Path to the audio file
            metadata: Optional metadata to guide analysis

        Returns:
            Dictionary of extracted features
        """
        try:
            y, sr = librosa.load(file_path, sr=self.config['sample_rate'])
            features, *_ = self.extract_features(y, sr, metadata)
            return features
        except Exception as e:
            self.logger.error(f"Error analyzing {file_path}: {e}")
            return {}

    def prepare_features_for_ml(self, df: pd.DataFrame) -> np.ndarray:
        """
        Prepare features from database for machine learning

        Args:
            df: DataFrame containing drum samples and features

        Returns:
            Array of feature vectors
        """
        X = []
        for _, row in df.iterrows():
            features = []
            # Convert semicolon-separated strings back to lists and flatten
            for feature_name in ['mfcc_mean', 'mfcc_skew', 'mfcc_kurtosis',
                                 'mfcc_delta_mean', 'mfcc_delta2_mean']:
                if feature_name in row and pd.notna(row[feature_name]):
                    try:
                        feature_values = [float(x) for x in row[feature_name].split(';')]
                        features.extend(feature_values)
                    except:
                        # Handle missing or malformed data
                        pass

            # Add scalar features
            for feature_name in ['spectral_centroid_mean', 'spectral_bandwidth_mean',
                                 'spectral_rolloff_mean', 'spectral_contrast_mean',
                                 'attack_time', 'decay_time', 'harmonic_energy',
                                 'percussive_energy', 'harmonic_percussive_ratio',
                                 'zero_crossing_rate']:
                if feature_name in row and pd.notna(row[feature_name]):
                    try:
                        features.append(float(row[feature_name]))
                    except:
                        features.append(0.0)  # Default value for missing features

            if len(features) > 0:
                X.append(features)

        return np.array(X)

    def train_classifier(self, target_variable: str) -> Optional[Dict[str, Any]]:
        """
        Train a random forest classifier on the drum database

        Args:
            target_variable: Column name to use as the target for classification

        Returns:
            Dictionary containing model and evaluation results, or None if training failed
        """
        # Load the database
        df = self.load_database()
        if df.empty:
            self.logger.error("Database is empty. Please add samples first.")
            return None

        # Check if target variable exists
        if target_variable not in df.columns:
            self.logger.error(f"Target variable '{target_variable}' not found in database.")
            return None

        # Prepare feature vectors
        X = self.prepare_features_for_ml(df)

        # Filter out rows with missing features
        valid_indices = np.where(~np.isnan(X).any(axis=1))[0]
        X = X[valid_indices]

        # Target variables
        y = df[target_variable].values[valid_indices]

        # Check if we have enough data
        if len(X) < 10:
            self.logger.error(f"Not enough valid data points for training (found {len(X)}).")
            return None

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

        # Standardize features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        # Train model
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train_scaled, y_train)

        # Evaluate - import as needed
        from sklearn.metrics import classification_report, confusion_matrix
        y_pred = model.predict(X_test_scaled)
        report = classification_report(y_test, y_pred)
        cm = confusion_matrix(y_test, y_pred)

        # Feature importance
        feature_importance = model.feature_importances_

        # Save model
        model_data = {
            'model': model,
            'scaler': scaler,
            'classes': model.classes_,
            'target_variable': target_variable
        }

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.config['model_filename']) or '.', exist_ok=True)

        with open(self.config['model_filename'], 'wb') as f:
            pickle.dump(model_data, f)

        return {
            'model': model,
            'scaler': scaler,
            'report': report,
            'confusion_matrix': cm,
            'feature_importance': feature_importance,
            'X_test': X_test_scaled,
            'y_test': y_test,
            'y_pred': y_pred,
            'classes': model.classes_
        }

    def predict_sample_type(self, features: Dict[str, Any], target_variable: str = None) -> Union[Dict[str, Any], str]:
        """
        Predict drum attributes from extracted features using the trained model

        Args:
            features: Dictionary of extracted features
            target_variable: Optional override for which target to predict

        Returns:
            Dictionary containing prediction results, or error message string
        """
        if not os.path.exists(self.config['model_filename']):
            return "No model found. Please train the model first."

        try:
            with open(self.config['model_filename'], 'rb') as f:
                model_data = pickle.load(f)

            model = model_data['model']
            scaler = model_data['scaler']
            classes = model_data['classes']

            # Use provided target_variable or the one from the model
            target_var = target_variable if target_variable else model_data['target_variable']

            # Prepare features in the same format as training
            feature_vector = []

            # Flatten the lists
            feature_vector.extend(features['mfcc_mean'])
            feature_vector.extend(features['mfcc_skew'])
            feature_vector.extend(features['mfcc_kurtosis'])
            feature_vector.extend(features['mfcc_delta_mean'])
            feature_vector.extend(features['mfcc_delta2_mean'])

            # Add scalar features
            scalar_features = [
                'spectral_centroid_mean', 'spectral_bandwidth_mean',
                'spectral_rolloff_mean', 'spectral_contrast_mean',
                'attack_time', 'decay_time', 'harmonic_energy',
                'percussive_energy', 'harmonic_percussive_ratio',
                'zero_crossing_rate'
            ]

            for feature in scalar_features:
                feature_vector.append(features.get(feature, 0.0))

            # Scale features
            X = np.array([feature_vector])
            X_scaled = scaler.transform(X)

            # Predict
            prediction = model.predict(X_scaled)[0]
            probabilities = model.predict_proba(X_scaled)[0]

            # Get the probability for each class
            class_probs = {cls: prob for cls, prob in zip(classes, probabilities)}

            return {
                'prediction': prediction,
                'target_variable': target_var,
                'probabilities': class_probs
            }

        except Exception as e:
            self.logger.error(f"Error making prediction: {e}")
            return f"Error making prediction: {e}"

    def batch_process_audio(self, audio_dir: str, metadata_file=None, progress_callback=None,
                            use_threading: bool = True, max_workers: int = 4) -> List[Dict[str, Any]]:
        """
        Process multiple audio files in a directory and add them to the database.

        Args:
            audio_dir: Directory containing audio files
            metadata_file: Excel file with metadata (optional)
            progress_callback: Function to call with progress updates (optional)
            use_threading: Whether to use parallel processing
            max_workers: Maximum number of worker threads

        Returns:
            List of dictionaries with processing results for each file
        """
        import glob

        # Check if directory exists
        if not os.path.exists(audio_dir):
            self.logger.error(f"Directory not found: {audio_dir}")
            return []

        # Load metadata if provided
        metadata_df = None
        if metadata_file:
            try:
                metadata_df = pd.read_excel(metadata_file)
                self.logger.info(f"Loaded metadata for {len(metadata_df)} samples")
            except Exception as e:
                self.logger.error(f"Error loading metadata file: {e}")
                return []

        # Find all audio files
        audio_files = glob.glob(os.path.join(audio_dir, "*.wav")) + glob.glob(os.path.join(audio_dir, "*.mp3"))

        if not audio_files:
            self.logger.error(f"No audio files found in {audio_dir}")
            return []

        self.logger.info(f"Found {len(audio_files)} audio files to process")

        # Implementation continues with file processing logic
        # This is a simplified version - implement full functionality as needed

        return []

    def export_database(self, output_path: Optional[str] = None) -> bool:
        """
        Export the database and trained models to a file

        Args:
            output_path: Path to save the export file

        Returns:
            bool: True if export was successful, False otherwise
        """
        if output_path is None:
            output_path = f"{self.drum_type}_database_export.pkl"

        try:
            db = self.load_database()

            # Check if model exists
            model_data = None
            if os.path.exists(self.config['model_filename']):
                with open(self.config['model_filename'], 'rb') as f:
                    model_data = pickle.load(f)

            # Create export data
            import time
            export_data = {
                'database': db,
                'model_data': model_data,
                'config': self.config,
                'export_date': time.strftime("%Y-%m-%d %H:%M:%S"),
                'version': '1.0.0'
            }

            # Save to file
            with open(output_path, 'wb') as f:
                pickle.dump(export_data, f)

            self.logger.info(f"Database exported to {output_path}")
            return True

        except Exception as e:
            self.logger.error(f"Error exporting database: {e}")
            return False

    def import_database(self, import_path: str) -> bool:
        """
        Import database and models from a file

        Args:
            import_path: Path to the import file

        Returns:
            bool: True if import was successful, False otherwise
        """
        try:
            # Load import file
            with open(import_path, 'rb') as f:
                import_data = pickle.load(f)

            # Check version compatibility
            if 'version' not in import_data:
                self.logger.warning("Import file has no version information")

            # Import database
            if 'database' in import_data and isinstance(import_data['database'], pd.DataFrame):
                import_data['database'].to_csv(self.config['database_filename'], index=False)
                self.logger.info(f"Imported {len(import_data['database'])} samples to database")
            else:
                self.logger.error("No valid database found in import file")
                return False

            # Import model if available
            if 'model_data' in import_data and import_data['model_data'] is not None:
                with open(self.config['model_filename'], 'wb') as f:
                    pickle.dump(import_data['model_data'], f)
                self.logger.info(f"Imported model for {import_data['model_data']['target_variable']}")

            # Import configuration if available
            if 'config' in import_data and isinstance(import_data['config'], dict):
                # Only import safe config values
                safe_keys = ['n_mfcc', 'feature_precision', 'batch_size']
                for key in safe_keys:
                    if key in import_data['config']:
                        self.config[key] = import_data['config'][key]
                self.logger.info("Imported configuration settings")

            return True

        except Exception as e:
            self.logger.error(f"Error importing database: {e}")
            return False

    def create_diagnostic_report(self):
        """Generate a diagnostic report for the analyzer"""
        report = {
            "analyzer_type": self.drum_type,
            "config": self.config,
            "database_status": self._get_database_status(),
            "model_status": self._get_model_status(),
        }
        return report

    def _get_database_status(self):
        """Get status information about the database"""
        try:
            df = self.load_database()
            return {
                "exists": True,
                "record_count": len(df),
                "columns": list(df.columns),
                "file_path": self.config['database_filename']
            }
        except Exception:
            return {
                "exists": False,
                "error": "Could not load database"
            }

    def _get_model_status(self):
        """Get status information about the trained model"""
        if os.path.exists(self.config['model_filename']):
            try:
                with open(self.config['model_filename'], 'rb') as f:
                    model_data = pickle.load(f)

                return {
                    "exists": True,
                    "target_variable": model_data.get('target_variable', 'unknown'),
                    "classes": list(model_data.get('classes', [])),
                    "file_path": self.config['model_filename']
                }
            except Exception:
                return {
                    "exists": True,
                    "error": "Could not load model"
                }
        else:
            return {
                "exists": False
            }