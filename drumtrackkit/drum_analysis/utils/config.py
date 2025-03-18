# drum_analysis/utils/config.py

"""
Configuration management for the DrumTracKAI framework.

This module provides centralized configuration handling with support for:
- Default configurations
- Custom configuration overrides
- JSON file-based configuration
- Environment variable integration
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List, Union

logger = logging.getLogger(__name__)


class ConfigManager:
    """
    Configuration manager for the drum analysis framework.

    Handles loading, storing and providing configuration values
    with support for defaults, file-based config, and overrides.
    """

    def __init__(self, config_file: Optional[str] = None,
                 config_dict: Optional[Dict[str, Any]] = None):
        """
        Initialize the configuration manager.

        Args:
            config_file: Optional path to JSON configuration file
            config_dict: Optional dictionary with configuration values
        """
        # Initialize with default values
        self.config = self._get_default_config()

        # Update from environment variables
        self._load_from_environment()

        # Load from file if provided
        if config_file and os.path.exists(config_file):
            self._load_from_file(config_file)

        # Update from provided dictionary if any
        if config_dict:
            self.config.update(config_dict)

        logger.debug(f"Initialized ConfigManager with {len(self.config)} settings")

    def _get_default_config(self) -> Dict[str, Any]:
        """
        Get default configuration values.

        Returns:
            Dictionary with default configuration
        """
        return {
            # General settings
            'sample_rate': 44100,
            'max_workers': 4,
            'temp_dir': './temp',

            # Database settings
            'database_path': './data',
            'sonic_reference_db': 'sonic_reference_db.csv',
            'technique_training_db': 'technique_training_db.csv',
            'style_examples_db': 'style_examples_db.csv',

            # Instrument-specific databases
            'kick_database': 'kick_samples_db.csv',
            'snare_database': 'snare_samples_db.csv',
            'cymbal_database': 'cymbal_samples_db.csv',
            'tom_database': 'tom_samples_db.csv',

            # G Drive paths to check
            'g_drive_paths': [
                '/Volumes/G-Drive',
                '/media/g_drive',
                'G:',
                '/mnt/g_drive'
            ],

            # Feature extraction settings
            'default_n_mfcc': 13,
            'feature_precision': 6,

            # Purpose-based settings
            'purpose_types': ['sonic_reference', 'technique_training', 'style_examples'],

            # Logging
            'log_level': 'INFO',
            'log_file': None
        }

    def _load_from_file(self, config_file: str) -> None:
        """
        Load configuration from a JSON file.

        Args:
            config_file: Path to JSON configuration file
        """
        try:
            with open(config_file, 'r') as f:
                file_config = json.load(f)
                self.config.update(file_config)
                logger.info(f"Loaded configuration from {config_file}")
        except Exception as e:
            logger.error(f"Error loading configuration file {config_file}: {e}")

    def _load_from_environment(self) -> None:
        """Load configuration values from environment variables."""
        env_prefix = "DRUMTRACKAI_"

        for key in self.config.keys():
            env_key = f"{env_prefix}{key.upper()}"
            if env_key in os.environ:
                env_value = os.environ[env_key]

                # Try to convert to appropriate type
                if isinstance(self.config[key], bool):
                    self.config[key] = env_value.lower() in ('true', 'yes', '1')
                elif isinstance(self.config[key], int):
                    try:
                        self.config[key] = int(env_value)
                    except ValueError:
                        logger.warning(f"Could not convert environment variable {env_key}='{env_value}' to int")
                elif isinstance(self.config[key], float):
                    try:
                        self.config[key] = float(env_value)
                    except ValueError:
                        logger.warning(f"Could not convert environment variable {env_key}='{env_value}' to float")
                elif isinstance(self.config[key], list):
                    try:
                        # Assume comma-separated list
                        self.config[key] = env_value.split(',')
                    except Exception:
                        logger.warning(f"Could not parse environment variable {env_key}='{env_value}' as list")
                else:
                    # String or other type
                    self.config[key] = env_value

                logger.debug(f"Loaded config from environment: {key}={self.config[key]}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by key.

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        return self.config.get(key, default)

    def get_path(self, key: str, create: bool = False) -> str:
        """
        Get a file or directory path from configuration.

        Args:
            key: Configuration key for the path
            create: Whether to create the directory if it doesn't exist

        Returns:
            Resolved path
        """
        path = self.get(key, "")

        # Resolve relative paths
        if path and not os.path.isabs(path):
            base_path = self.get('database_path', '.')
            path = os.path.join(base_path, path)

        # Create directory if requested
        if create and path:
            directory = path if os.path.splitext(path)[1] == '' else os.path.dirname(path)
            if directory and not os.path.exists(directory):
                try:
                    os.makedirs(directory, exist_ok=True)
                    logger.debug(f"Created directory: {directory}")
                except Exception as e:
                    logger.error(f"Error creating directory {directory}: {e}")

        return path

    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.

        Args:
            key: Configuration key
            value: Value to set
        """
        self.config[key] = value

    def update(self, config_dict: Dict[str, Any]) -> None:
        """
        Update multiple configuration values.

        Args:
            config_dict: Dictionary with configuration values to update
        """
        self.config.update(config_dict)

    def save(self, config_file: str) -> bool:
        """
        Save current configuration to a JSON file.

        Args:
            config_file: Path to save the configuration

        Returns:
            Boolean indicating success
        """
        try:
            # Create directory if it doesn't exist
            directory = os.path.dirname(config_file)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)

            with open(config_file, 'w') as f:
                json.dump(self.config, f, indent=2, sort_keys=True)

            logger.info(f"Saved configuration to {config_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving configuration to {config_file}: {e}")
            return False

    def get_instrument_db_path(self, instrument: str) -> str:
        """
        Get the database path for a specific instrument.

        Args:
            instrument: Instrument type (kick, snare, cymbal, tom)

        Returns:
            Path to the instrument database
        """
        key = f"{instrument}_database"
        return self.get_path(key)

    def get_purpose_db_path(self, purpose: str) -> str:
        """
        Get the database path for a specific purpose.

        Args:
            purpose: Purpose type (sonic_reference, technique_training, style_examples)

        Returns:
            Path to the purpose database
        """
        key = f"{purpose}_db"
        return self.get_path(key)


# Create a global instance with default settings
config_manager = ConfigManager()


# Simplified access functions
def get_config(key: str, default: Any = None) -> Any:
    """Get a configuration value by key."""
    return config_manager.get(key, default)


def set_config(key: str, value: Any) -> None:
    """Set a configuration value."""
    config_manager.set(key, value)


def load_config(config_file: str) -> None:
    """Load configuration from file."""
    config_manager._load_from_file(config_file)