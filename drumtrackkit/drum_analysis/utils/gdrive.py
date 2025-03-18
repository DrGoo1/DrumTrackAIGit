# drum_analysis/utils/gdrive.py

"""
G Drive utilities for the DrumTracKAI framework.

This module provides functions for:
- Discovering G Drive mounting locations
- Resolving sample paths relative to G Drive
- Handling path mappings between different systems
- Caching location information for performance
"""

import os
import logging
import platform
from typing import Optional, List, Dict, Union, Tuple
from pathlib import Path
import json
import time

# Local imports
from .config import get_config

logger = logging.getLogger(__name__)

# Cache for G Drive discovery - avoid repeated filesystem checks
_GDRIVE_CACHE = {
    'mount_point': None,
    'last_check': 0,
    'cache_duration': 300  # seconds
}


def discover_g_drive() -> Optional[str]:
    """
    Discover the G Drive mounting location on the current system.

    Checks multiple possible locations and caches the result for performance.

    Returns:
        Path to the G Drive root or None if not found
    """
    global _GDRIVE_CACHE

    # Use cached value if available and not expired
    current_time = time.time()
    if (_GDRIVE_CACHE['mount_point'] is not None and
            current_time - _GDRIVE_CACHE['last_check'] < _GDRIVE_CACHE['cache_duration']):
        return _GDRIVE_CACHE['mount_point']

    # Get potential mount points from config
    mount_points = get_config('g_drive_paths', [
        '/Volumes/G-Drive',  # macOS
        '/media/g_drive',  # Linux
        'G:',  # Windows
        '/mnt/g_drive',  # Alternative Linux
    ])

    # Add system-specific locations
    system = platform.system()
    if system == 'Windows':
        # Add all drive letters from D: to Z:
        mount_points.extend([f"{chr(i)}:" for i in range(ord('D'), ord('Z') + 1)])
    elif system == 'Darwin':  # macOS
        # Add volumes directory paths
        volumes_dir = '/Volumes'
        if os.path.exists(volumes_dir):
            for volume in os.listdir(volumes_dir):
                if 'drive' in volume.lower() or 'g' in volume.lower():
                    mount_points.append(os.path.join(volumes_dir, volume))
    elif system == 'Linux':
        # Add media and mnt paths
        for base_dir in ['/media', '/mnt']:
            if os.path.exists(base_dir):
                for username in os.listdir(base_dir):
                    user_dir = os.path.join(base_dir, username)
                    if os.path.isdir(user_dir):
                        for volume in os.listdir(user_dir):
                            if 'drive' in volume.lower() or 'g' in volume.lower():
                                mount_points.append(os.path.join(user_dir, volume))

    # Try to find marker files or directories that would identify this as the G Drive
    gdrive_markers = [
        'DrumSamples',
        'SampleLibrary',
        'Drums',
        'AudioContent',
        'DrumTracKAI'
    ]

    # Check each location
    for mount_point in mount_points:
        if os.path.exists(mount_point) and os.path.isdir(mount_point):
            logger.debug(f"Found potential G Drive mount point: {mount_point}")

            # Look for markers to confirm this is the correct drive
            for marker in gdrive_markers:
                marker_path = os.path.join(mount_point, marker)
                if os.path.exists(marker_path):
                    logger.info(f"Confirmed G Drive mount point: {mount_point} (found marker: {marker})")

                    # Update cache
                    _GDRIVE_CACHE['mount_point'] = mount_point
                    _GDRIVE_CACHE['last_check'] = current_time

                    return mount_point

            # If no markers found, but this is the most likely candidate
            if 'g' in os.path.basename(mount_point).lower() or 'drive' in os.path.basename(mount_point).lower():
                logger.info(f"Probable G Drive mount point: {mount_point} (no markers found)")

                # Update cache
                _GDRIVE_CACHE['mount_point'] = mount_point
                _GDRIVE_CACHE['last_check'] = current_time

                return mount_point

    # If no mount point found, cache the failure and return None
    logger.warning("G Drive mount point not found")
    _GDRIVE_CACHE['mount_point'] = None
    _GDRIVE_CACHE['last_check'] = current_time

    return None


def resolve_g_drive_path(relative_path: str) -> Optional[str]:
    """
    Resolve a path relative to the G Drive to an absolute path.

    Args:
        relative_path: Path relative to G Drive root

    Returns:
        Absolute path or None if G Drive not found
    """
    # Handle empty or None paths
    if not relative_path:
        return None

    # If path is already absolute and exists, return it
    if os.path.isabs(relative_path) and os.path.exists(relative_path):
        return relative_path

    # Clean up the relative path
    clean_path = relative_path.lstrip('/')
    clean_path = clean_path.replace('\\', '/')

    # Find G Drive mount point
    g_drive = discover_g_drive()
    if not g_drive:
        logger.warning(f"Cannot resolve path '{relative_path}' - G Drive not found")
        return None

    # Combine paths
    full_path = os.path.join(g_drive, clean_path)

    # Check if path exists
    if os.path.exists(full_path):
        return full_path
    else:
        logger.debug(f"Resolved path does not exist: {full_path}")
        return full_path  # Return the path even if it doesn't exist


def get_all_audio_files(directory: str, recursive: bool = True) -> List[str]:
    """
    Get all audio files in a directory.

    Args:
        directory: Directory to search
        recursive: Whether to search recursively

    Returns:
        List of audio file paths
    """
    if not os.path.exists(directory) or not os.path.isdir(directory):
        logger.warning(f"Directory does not exist or is not a directory: {directory}")
        return []

    audio_extensions = ['.wav', '.mp3', '.aiff', '.flac', '.ogg']
    audio_files = []

    if recursive:
        for root, _, files in os.walk(directory):
            for file in files:
                if any(file.lower().endswith(ext) for ext in audio_extensions):
                    audio_files.append(os.path.join(root, file))
    else:
        for file in os.listdir(directory):
            if any(file.lower().endswith(ext) for ext in audio_extensions):
                audio_files.append(os.path.join(directory, file))

    logger.debug(f"Found {len(audio_files)} audio files in {directory}")
    return audio_files


def get_relative_path(absolute_path: str) -> str:
    """
    Get path relative to G Drive.

    Args:
        absolute_path: Absolute path

    Returns:
        Path relative to G Drive root or original path if not under G Drive
    """
    g_drive = discover_g_drive()
    if not g_drive or not absolute_path.startswith(g_drive):
        return absolute_path

    # Get relative path
    rel_path = os.path.relpath(absolute_path, g_drive)
    return rel_path


def get_sample_category(file_path: str) -> str:
    """
    Determine the sample category based on file path.

    Categories include:
    - sonic_reference: Individual drum hits
    - technique_training: Technique exercises
    - style_examples: Full performances

    Args:
        file_path: Path to the audio file

    Returns:
        Sample category
    """
    # Path components to help categorize
    path_lower = file_path.lower()
    filename = os.path.basename(path_lower)

    # Keywords that suggest different categories
    sonic_keywords = ['hit', 'one-shot', 'oneshot', 'sample', 'individual', 'single']
    technique_keywords = ['exercise', 'pattern', 'rudiment', 'technique', 'practice']
    style_keywords = ['performance', 'groove', 'beat', 'full', 'track', 'song']

    # Check filename and path for category hints
    if any(keyword in path_lower or keyword in filename for keyword in sonic_keywords):
        return 'sonic_reference'
    elif any(keyword in path_lower or keyword in filename for keyword in technique_keywords):
        return 'technique_training'
    elif any(keyword in path_lower or keyword in filename for keyword in style_keywords):
        return 'style_examples'

    # If no keywords match, try to guess based on audio properties
    # This is just a placeholder - real implementation would analyze the audio
    # For now, default to sonic_reference as the most common case
    return 'sonic_reference'


class PathCache:
    """
    Cache for frequently accessed paths to improve performance.
    """

    def __init__(self, cache_file: Optional[str] = None):
        """
        Initialize the path cache.

        Args:
            cache_file: Optional path to cache file
        """
        self.cache = {}
        self.cache_file = cache_file
        self.modified = False

        # Load cache from file if available
        if cache_file and os.path.exists(cache_file):
            self._load_cache()

    def _load_cache(self):
        """Load cache from file."""
        try:
            with open(self.cache_file, 'r') as f:
                self.cache = json.load(f)
                logger.debug(f"Loaded {len(self.cache)} entries from path cache")
        except Exception as e:
            logger.warning(f"Error loading path cache: {e}")
            self.cache = {}

    def save_cache(self):
        """Save cache to file if modified."""
        if not self.modified or not self.cache_file:
            return

        try:
            directory = os.path.dirname(self.cache_file)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)

            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)

            self.modified = False
            logger.debug(f"Saved {len(self.cache)} entries to path cache")
        except Exception as e:
            logger.warning(f"Error saving path cache: {e}")

    def add(self, relative_path: str, absolute_path: str):
        """
        Add a path mapping to the cache.

        Args:
            relative_path: Path relative to G Drive
            absolute_path: Absolute path
        """
        self.cache[relative_path] = absolute_path
        self.modified = True

    def get(self, relative_path: str) -> Optional[str]:
        """
        Get an absolute path from cache.

        Args:
            relative_path: Path relative to G Drive

        Returns:
            Absolute path or None if not in cache
        """
        return self.cache.get(relative_path)

    def clear(self):
        """Clear the cache."""
        self.cache = {}
        self.modified = True


# Initialize a global path cache
path_cache = PathCache(os.path.join(get_config('temp_dir', './temp'), 'path_cache.json'))