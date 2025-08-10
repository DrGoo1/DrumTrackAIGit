#!/usr/bin/env python3
"""
Populate Drum Beats Database
============================
Script to populate the drum_beats database with files from D:\DrumBeats directory.
Processes both _drum.wav (drum-only) and _original.wav (full song) files.
"""

import os
import sys
import logging
from pathlib import Path

# Add the admin directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'admin'))

from admin.services.central_database_service import get_database_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def extract_song_info(filename):
    """Extract song name and type from filename"""
    # Remove .wav extension
    name = filename.replace('.wav', '')
    
    # Determine type and clean name
    if name.endswith('_drum'):
        song_name = name.replace('_drum', '')
        file_type = 'drum'
    elif name.endswith('_original'):
        song_name = name.replace('_original', '')
        file_type = 'original'
    elif name.endswith('_orig'):  # Handle "we_will_rock_you_orig.wav"
        song_name = name.replace('_orig', '')
        file_type = 'original'
    elif name.endswith('_origianl'):  # Handle typo in "wipe_out_origianl.wav"
        song_name = name.replace('_origianl', '')
        file_type = 'original'
    else:
        song_name = name
        file_type = 'unknown'
    
    # Clean up song name (replace underscores with spaces, title case)
    clean_name = song_name.replace('_', ' ').replace(' ', ' ').strip()
    clean_name = ' '.join(word.capitalize() for word in clean_name.split())
    
    # Handle special cases
    clean_name = clean_name.replace('Smells-Like', 'Smells Like')
    clean_name = clean_name.replace("We're", "We're")
    
    return clean_name, file_type

def get_song_metadata(song_name):
    """Get metadata for known songs"""
    # Famous drum tracks metadata
    metadata = {
        'Ballroom Blitz': {'artist': 'Sweet', 'bpm': 140, 'complexity': 4.0, 'energy': 4.5},
        'Billion Dollar Baby': {'artist': 'Alice Cooper', 'bpm': 120, 'complexity': 3.5, 'energy': 4.0},
        'Cissy Strut': {'artist': 'The Meters', 'bpm': 90, 'complexity': 3.0, 'energy': 3.5},
        'Come Together': {'artist': 'The Beatles', 'bpm': 85, 'complexity': 3.0, 'energy': 3.0},
        'Crazy Train': {'artist': 'Ozzy Osbourne', 'bpm': 138, 'complexity': 4.0, 'energy': 4.5},
        'Fifty Ways To Leave Your Lover': {'artist': 'Paul Simon', 'bpm': 120, 'complexity': 4.5, 'energy': 4.0},
        'Fool In The Rain': {'artist': 'Led Zeppelin', 'bpm': 85, 'complexity': 4.5, 'energy': 3.5},
        'Funky Drummer': {'artist': 'James Brown', 'bpm': 100, 'complexity': 4.0, 'energy': 4.0},
        'Hot For Teacher': {'artist': 'Van Halen', 'bpm': 130, 'complexity': 4.5, 'energy': 5.0},
        'Rosanna': {'artist': 'Toto', 'bpm': 95, 'complexity': 4.5, 'energy': 3.5},
        'Sing Sing Sing': {'artist': 'Benny Goodman', 'bpm': 180, 'complexity': 4.0, 'energy': 4.5},
        'Smells Like Teen Spirit': {'artist': 'Nirvana', 'bpm': 117, 'complexity': 3.5, 'energy': 4.5},
        'Sunday Bloody Sunday': {'artist': 'U2', 'bpm': 103, 'complexity': 3.0, 'energy': 4.0},
        'Superstitious': {'artist': 'Stevie Wonder', 'bpm': 100, 'complexity': 4.0, 'energy': 4.0},
        'Take Five': {'artist': 'Dave Brubeck Quartet', 'bpm': 170, 'complexity': 4.5, 'energy': 3.0},
        'Tom Sawyer': {'artist': 'Rush', 'bpm': 88, 'complexity': 4.5, 'energy': 4.0},
        'Walk This Way': {'artist': 'Aerosmith', 'bpm': 120, 'complexity': 4.0, 'energy': 4.5},
        'We\'re Not Gonna Take It': {'artist': 'Twisted Sister', 'bpm': 140, 'complexity': 3.5, 'energy': 4.5},
        'We Will Rock You': {'artist': 'Queen', 'bpm': 114, 'complexity': 2.0, 'energy': 4.0},
        'Wipe Out': {'artist': 'The Surfaris', 'bpm': 150, 'complexity': 4.5, 'energy': 5.0},
    }
    
    return metadata.get(song_name, {'artist': 'Unknown', 'bpm': 120, 'complexity': 3.0, 'energy': 3.5})

def populate_drum_beats_database():
    """Populate the drum beats database with files from D:\DrumBeats"""
    
    drumbeats_dir = Path("D:/DrumBeats")
    
    if not drumbeats_dir.exists():
        logger.error(f"DrumBeats directory not found: {drumbeats_dir}")
        return False
    
    # Initialize database service
    logger.info("Initializing database service...")
    db_service = get_database_service()
    success = db_service.initialize()
    
    if not success:
        logger.error("Failed to initialize database service")
        return False
    
    # Get all WAV files
    wav_files = list(drumbeats_dir.glob("*.wav"))
    logger.info(f"Found {len(wav_files)} WAV files in {drumbeats_dir}")
    
    # Group files by song
    songs = {}
    for wav_file in wav_files:
        song_name, file_type = extract_song_info(wav_file.name)
        
        if song_name not in songs:
            songs[song_name] = {}
        
        songs[song_name][file_type] = wav_file
    
    logger.info(f"Identified {len(songs)} unique songs")
    
    # Process each song
    added_count = 0
    for song_name, files in songs.items():
        try:
            metadata = get_song_metadata(song_name)
            
            # Add drum version if available
            if 'drum' in files:
                drum_file = files['drum']
                beat_name = f"{song_name} (Drum Only)"
                description = f"Drum-only version of {song_name} by {metadata['artist']}"
                
                beat_metadata = {
                    'description': description,
                    'bpm': metadata['bpm'],
                    'complexity': metadata['complexity'],
                    'energy': metadata['energy'],
                    'time_signature': '4/4'
                }
                
                beat_id = db_service.add_drum_beat(
                    name=beat_name,
                    file_path=str(drum_file),
                    metadata=beat_metadata
                )
                
                if beat_id:
                    logger.info(f"Added drum beat: {beat_name}")
                    added_count += 1
                else:
                    logger.error(f"Failed to add drum beat: {beat_name}")
            
            # Add original version if available
            if 'original' in files:
                original_file = files['original']
                beat_name = f"{song_name} (Original)"
                description = f"Original full song version of {song_name} by {metadata['artist']}"
                
                beat_metadata = {
                    'description': description,
                    'bpm': metadata['bpm'],
                    'complexity': metadata['complexity'] * 0.8,  # Slightly lower complexity for full song
                    'energy': metadata['energy'],
                    'time_signature': '4/4'
                }
                
                beat_id = db_service.add_drum_beat(
                    name=beat_name,
                    file_path=str(original_file),
                    metadata=beat_metadata
                )
                
                if beat_id:
                    logger.info(f"Added drum beat: {beat_name}")
                    added_count += 1
                else:
                    logger.error(f"Failed to add drum beat: {beat_name}")
                    
        except Exception as e:
            logger.error(f"Error processing song {song_name}: {e}")
    
    logger.info(f"Successfully added {added_count} drum beats to the database")
    
    # Verify the data
    all_beats = db_service.get_drum_beats()
    logger.info(f"Database now contains {len(all_beats)} drum beats total")
    
    return True

if __name__ == "__main__":
    logger.info("Starting DrumBeats database population...")
    success = populate_drum_beats_database()
    
    if success:
        logger.info("DrumBeats database population completed successfully!")
    else:
        logger.error("DrumBeats database population failed!")
        sys.exit(1)
