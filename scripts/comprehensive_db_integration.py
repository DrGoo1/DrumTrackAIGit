#!/usr/bin/env python
"""
Comprehensive Drum Database Integration Script for DrumTracKAI

This script integrates all drum-related databases from the G: drive into the DrumTracKAI project, including:
- Cymbal databases (hi-hat, ride, crash, splash, china)
- Kick databases
- Snare databases (including rudiments)
- Tom databases
- E-GMD dataset
- SoundTracksLoops Dataset

Usage:
    python drum_db_integration.py [--gdrive GDRIVE_PATH]

Options:
    --gdrive GDRIVE_PATH  Path to G Drive (default: auto-detect)
"""

import os
import sys
import argparse
import json
import sqlite3
import csv
import logging
import re
import shutil
import platform
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("drum_database_integration.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DrumDatabaseIntegrator:
    """Handles integration of all drum-related databases from G: drive"""

    def __init__(self, gdrive_path=None):
        self.gdrive_path = self.find_gdrive_path(gdrive_path)
        if not self.gdrive_path:
            raise ValueError("G Drive path not found. Specify with --gdrive")

        # Define database file types
        self.db_types = {
            '.db': 'sqlite',
            '.sqlite': 'sqlite',
            '.sqlite3': 'sqlite',
            '.csv': 'csv',
            '.json': 'json',
            '.mid': 'midi',
            '.midi': 'midi',
            '.wav': 'audio',
            '.mp3': 'audio',
            '.flac': 'audio',
            '.ogg': 'audio'
        }

        # Instrument types to detect
        self.instrument_types = {
            'cymbal': ['hi-hat', 'hihat', 'ride', 'crash', 'splash', 'china'],
            'kick': ['kick', 'bass drum', 'bassdrum'],
            'snare': ['snare', 'rudiment'],
            'tom': ['tom', 'floor tom', 'rack tom']
        }

        # Special datasets to detect
        self.special_datasets = {
            'egmd': ['e-gmd', 'egmd', 'groove midi dataset'],
            'soundtracksloops': ['soundtracksloops', 'soundtracks loops'],
            'snare_rudiments': ['rudiment', 'rudiments']
        }

        # Store found databases
        self.databases = {
            'sqlite': [],
            'csv': [],
            'json': [],
            'midi': [],
            'audio': []
        }

        # Store database statistics by instrument/dataset type
        self.db_stats = {
            'cymbal': {},
            'kick': {},
            'snare': {},
            'tom': {},
            'egmd': {},
            'soundtracksloops': {},
            'snare_rudiments': {},
            'unknown': {}
        }

        # Store special dataset locations
        self.dataset_locations = {
            'egmd': None,
            'soundtracksloops': None,
            'snare_rudiments': None
        }

    def find_gdrive_path(self, specified_path=None):
        """Find G Drive path"""
        if specified_path and os.path.exists(specified_path):
            return specified_path

        # Common G Drive paths
        potential_paths = [
            r"G:\\",
            r"G:",
            r"/Volumes/G",
            os.path.expanduser("~/G"),
        ]

        # Try to find the path
        for path in potential_paths:
            if os.path.exists(path):
                logger.info(f"Found G Drive at: {path}")
                return path

        logger.warning("G Drive path not found")
        return None

    def determine_instrument_type(self, path):
        """Determine which instrument or dataset a file is related to"""
        path_str = str(path).lower()

        # Check for special datasets first (more specific matches)
        for dataset_key, keywords in self.special_datasets.items():
            if any(keyword in path_str for keyword in keywords):
                return dataset_key

        # Check for instrument types
        for instrument_key, subtypes in self.instrument_types.items():
            if any(subtype in path_str for subtype in subtypes):
                return instrument_key

        return 'unknown'

    def scan_for_databases(self):
        """Scan G Drive for all drum-related databases"""
        logger.info(f"Scanning {self.gdrive_path} for drum databases...")
        gdrive_path = Path(self.gdrive_path)

        # Look for special dataset directories first
        self._find_special_datasets(gdrive_path)

        # Track progress
        files_scanned = 0
        potential_db_files = []
        start_time = datetime.now()

        # Collect potential database files
        for ext in self.db_types.keys():
            for db_file in gdrive_path.glob(f"**/*{ext}"):
                files_scanned += 1
                if files_scanned % 1000 == 0:
                    logger.info(f"Scanned {files_scanned} files...")

                # Determine instrument/dataset type
                instrument_type = self.determine_instrument_type(db_file)

                # Only include drums-related files
                if instrument_type != 'unknown' or 'drum' in str(db_file).lower():
                    potential_db_files.append((db_file, instrument_type))

        # Process the potential database files
        logger.info(f"Found {len(potential_db_files)} potential drum database files. Analyzing...")

        for db_file, instrument_type in potential_db_files:
            ext = db_file.suffix.lower()
            db_type = self.db_types.get(ext)

            if not db_type:
                continue

            try:
                # Verify the file is a valid database of its type
                if db_type == 'sqlite':
                    self._verify_sqlite(db_file, instrument_type)
                elif db_type == 'csv':
                    self._verify_csv(db_file, instrument_type)
                elif db_type == 'json':
                    self._verify_json(db_file, instrument_type)
                elif db_type == 'midi':
                    self._verify_midi(db_file, instrument_type)
                elif db_type == 'audio':
                    self._verify_audio(db_file, instrument_type)
            except Exception as e:
                logger.warning(f"Error processing {db_file}: {e}")
                continue

        elapsed_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"Scan completed in {elapsed_time:.2f} seconds")

        # Log counts by type
        total_dbs = sum(len(dbs) for dbs in self.databases.values())
        logger.info(f"Found {total_dbs} valid drum databases:")

        for db_type, db_list in self.databases.items():
            if db_list:
                logger.info(f"  {db_type}: {len(db_list)} databases")

        # Log counts by instrument
        for instrument, stats in self.db_stats.items():
            if stats:
                logger.info(f"  {instrument}: {len(stats)} databases")

        return self.databases

    def _find_special_datasets(self, gdrive_path):
        """Find special dataset directories"""
        logger.info("Looking for special datasets...")

        # Common locations
        egmd_paths = ["E-GMD", "EGMD", "groove midi dataset"]
        stl_paths = ["SoundTracksLoops Dataset", "SoundTracksLoops"]
        rudiments_paths = ["Snare Rudiments", "Rudiments"]

        # Search for E-GMD dataset
        for path in egmd_paths:
            potential_path = gdrive_path / path
            if potential_path.exists() and potential_path.is_dir():
                self.dataset_locations['egmd'] = str(potential_path)
                logger.info(f"Found E-GMD dataset at: {potential_path}")
                break

        # Search for SoundTracksLoops dataset
        for path in stl_paths:
            potential_path = gdrive_path / path
            if potential_path.exists() and potential_path.is_dir():
                self.dataset_locations['soundtracksloops'] = str(potential_path)
                logger.info(f"Found SoundTracksLoops dataset at: {potential_path}")
                break

        # Search for Snare Rudiments dataset
        for path in rudiments_paths:
            potential_path = gdrive_path / path
            if potential_path.exists() and potential_path.is_dir():
                self.dataset_locations['snare_rudiments'] = str(potential_path)
                logger.info(f"Found Snare Rudiments dataset at: {potential_path}")
                break

        # Specific path for SoundTracksLoops
        specific_stl = gdrive_path / "SoundTracksLoops Dataset"
        if specific_stl.exists() and specific_stl.is_dir():
            self.dataset_locations['soundtracksloops'] = str(specific_stl)
            logger.info(f"Found SoundTracksLoops dataset at: {specific_stl}")

    def _verify_sqlite(self, db_file, instrument_type):
        """Verify SQLite database and extract metadata"""
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()

            # Get list of tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]

            if not tables:
                return False

            # Count rows in each table
            table_stats = {}
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM '{table}';")
                row_count = cursor.fetchone()[0]
                table_stats[table] = row_count

            # Get column info from first table
            cursor.execute(f"PRAGMA table_info('{tables[0]}');")
            columns = [row[1] for row in cursor.fetchall()]

            conn.close()

            # Store database info
            db_info = {
                'path': str(db_file),
                'tables': tables,
                'row_counts': table_stats,
                'columns': columns,
                'size': db_file.stat().st_size,
                'instrument_type': instrument_type
            }

            self.databases['sqlite'].append(db_info)
            self.db_stats[instrument_type][str(db_file)] = db_info
            logger.info(f"Added SQLite database: {db_file} ({instrument_type})")
            return True

        except sqlite3.Error as e:
            logger.debug(f"Not a valid SQLite database: {db_file} - {e}")
            return False

    def _verify_csv(self, csv_file, instrument_type):
        """Verify CSV file and extract metadata"""
        try:
            with open(csv_file, 'r', newline='', encoding='utf-8') as f:
                csv_reader = csv.reader(f)
                header = next(csv_reader, None)

                if not header:
                    return False

                # Count rows
                row_count = sum(1 for _ in csv_reader)

            # Store database info
            db_info = {
                'path': str(csv_file),
                'columns': header,
                'row_count': row_count,
                'size': csv_file.stat().st_size,
                'instrument_type': instrument_type
            }

            self.databases['csv'].append(db_info)
            self.db_stats[instrument_type][str(csv_file)] = db_info
            logger.info(f"Added CSV database: {csv_file} ({instrument_type})")
            return True

        except Exception as e:
            logger.debug(f"Not a valid CSV file: {csv_file} - {e}")
            return False

    def _verify_json(self, json_file, instrument_type):
        """Verify JSON file and extract metadata"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                json_data = json.load(f)

            # Check if it's a list or dict
            if isinstance(json_data, list):
                row_count = len(json_data)
                columns = list(json_data[0].keys()) if row_count > 0 else []
            elif isinstance(json_data, dict):
                row_count = len(json_data)
                columns = list(json_data.keys())
            else:
                return False

            # Store database info
            db_info = {
                'path': str(json_file),
                'columns': columns,
                'row_count': row_count,
                'size': json_file.stat().st_size,
                'instrument_type': instrument_type
            }

            self.databases['json'].append(db_info)
            self.db_stats[instrument_type][str(json_file)] = db_info
            logger.info(f"Added JSON database: {json_file} ({instrument_type})")
            return True

        except Exception as e:
            logger.debug(f"Not a valid JSON file: {json_file} - {e}")
            return False

    def _verify_midi(self, midi_file, instrument_type):
        """Verify MIDI file and extract basic metadata"""
        try:
            # Just check file size for now
            file_size = midi_file.stat().st_size

            if file_size == 0:
                return False

            # Store database info
            db_info = {
                'path': str(midi_file),
                'size': file_size,
                'instrument_type': instrument_type
            }

            self.databases['midi'].append(db_info)
            self.db_stats[instrument_type][str(midi_file)] = db_info

            # Don't log every MIDI file to avoid log spam
            if len(self.databases['midi']) % 100 == 1:
                logger.info(f"Added {len(self.databases['midi'])} MIDI files so far...")

            return True

        except Exception as e:
            logger.debug(f"Error processing MIDI file: {midi_file} - {e}")
            return False

    def _verify_audio(self, audio_file, instrument_type):
        """Verify audio file and extract basic metadata"""
        try:
            # Just check file size for now
            file_size = audio_file.stat().st_size

            if file_size == 0:
                return False

            # Store database info
            db_info = {
                'path': str(audio_file),
                'size': file_size,
                'instrument_type': instrument_type
            }

            self.databases['audio'].append(db_info)
            self.db_stats[instrument_type][str(audio_file)] = db_info

            # Don't log every audio file to avoid log spam
            if len(self.databases['audio']) % 100 == 1:
                logger.info(f"Added {len(self.databases['audio'])} audio files so far...")

            return True

        except Exception as e:
            logger.debug(f"Error processing audio file: {audio_file} - {e}")
            return False

    def analyze_dataset_structure(self):
        """Analyze the structure of special datasets"""
        for dataset_name, dataset_path in self.dataset_locations.items():
            if not dataset_path:
                continue

            logger.info(f"Analyzing {dataset_name} dataset structure at {dataset_path}...")

            try:
                path = Path(dataset_path)
                if not path.exists():
                    continue

                # Get directory structure
                structure = {
                    'directories': [],
                    'file_counts': {},
                    'file_types': {},
                    'total_size': 0
                }

                # Track first-level directories
                for item in path.iterdir():
                    if item.is_dir():
                        structure['directories'].append(item.name)

                        # Count files by type in each subdirectory
                        file_counts = {}
                        file_types = {}
                        dir_size = 0

                        for subitem in item.glob('**/*'):
                            if subitem.is_file():
                                ext = subitem.suffix.lower()
                                if ext not in file_types:
                                    file_types[ext] = 0
                                file_types[ext] += 1

                                dir_size += subitem.stat().st_size

                        structure['file_counts'][item.name] = sum(file_types.values())
                        structure['file_types'][item.name] = file_types
                        structure['total_size'] += dir_size

                # Store dataset structure
                self.db_stats[dataset_name]['structure'] = structure
                logger.info(
                    f"Analyzed {dataset_name} dataset: {len(structure['directories'])} directories, {structure['total_size'] / (1024 * 1024 * 1024):.2f} GB")

            except Exception as e:
                logger.warning(f"Error analyzing {dataset_name} dataset: {e}")

    def generate_config_file(self):
        """Generate configuration file for all drum databases"""
        logger.info("Generating configuration file...")

        # Organize databases by instrument type
        db_mapping = {}

        for instrument_type, stats in self.db_stats.items():
            if not stats:
                continue

            db_mapping[instrument_type] = {
                'databases': [],
                'count': len(stats),
                'special_dataset': instrument_type in self.dataset_locations and self.dataset_locations[
                    instrument_type] is not None
            }

            # Add regular database files
            for db_path, db_info in stats.items():
                if 'path' in db_info:
                    db_type = None
                    for t, db_list in self.databases.items():
                        for db in db_list:
                            if db.get('path') == db_path:
                                db_type = t
                                break
                        if db_type:
                            break

                    if db_type:
                        db_mapping[instrument_type]['databases'].append({
                            'path': db_path,
                            'type': db_type,
                            'size': db_info.get('size', 0)
                        })

            # Add special dataset path if it exists
            if instrument_type in self.dataset_locations and self.dataset_locations[instrument_type]:
                db_mapping[instrument_type]['dataset_path'] = self.dataset_locations[instrument_type]

        # Create configuration
        config = {
            'gdrive_path': self.gdrive_path,
            'last_updated': datetime.now().isoformat(),
            'database_mapping': db_mapping
        }

        # Write configuration file
        config_dir = Path("config")
        config_dir.mkdir(exist_ok=True)

        config_file = config_dir / "drum_database_config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)

        logger.info(f"Configuration written to {config_file}")
        return config_file

    def generate_dataset_symlinks(self):
        """Generate symbolic links to special datasets in the project"""
        logger.info("Creating symbolic links to special datasets...")

        datasets_dir = Path("datasets")
        datasets_dir.mkdir(exist_ok=True)

        created_links = []

        for dataset_name, dataset_path in self.dataset_locations.items():
            if not dataset_path:
                continue

            link_path = datasets_dir / dataset_name

            # Remove existing link if it's a symlink
            if link_path.is_symlink():
                os.remove(link_path)

            # Create the symbolic link
            try:
                # For Windows
                if platform.system() == 'Windows':
                    subprocess.run(
                        ["mklink", "/D", str(link_path), dataset_path],
                        shell=True,
                        check=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
                # For Unix
                else:
                    os.symlink(dataset_path, link_path, target_is_directory=True)

                logger.info(f"Created symbolic link: {link_path} -> {dataset_path}")
                created_links.append((str(link_path), dataset_path))

            except Exception as e:
                logger.warning(f"Could not create symbolic link for {dataset_name}: {e}")

                # If symlinking fails, create a text file with the path instead
                with open(f"{link_path}_path.txt", "w") as f:
                    f.write(f"Dataset path: {dataset_path}\n")

                logger.info(f"Created path reference file: {link_path}_path.txt")

        return created_links

    def generate_report(self):
        """Generate a comprehensive report on all drum databases"""
        logger.info("Generating drum database report...")

        # Calculate total counts and sizes
        total_counts = {
            'databases': sum(len(dbs) for dbs in self.databases.values() if dbs),
            'by_type': {db_type: len(db_list) for db_type, db_list in self.databases.items() if db_list},
            'by_instrument': {instr: len(stats) for instr, stats in self.db_stats.items() if
                              stats and instr != 'structure'},
            'total_size_bytes': sum(
                db_info.get('size', 0)
                for db_list in self.databases.values()
                for db in db_list
                for db_info in [db] if 'size' in db_info
            ),
            'special_datasets': {
                name: path for name, path in self.dataset_locations.items() if path
            }
        }

        # Create report dictionary
        report = {
            'summary': total_counts,
            'databases': self.db_stats
        }

        # Write report file
        report_dir = Path("docs")
        report_dir.mkdir(exist_ok=True)

        report_file = report_dir / "drum_database_migration_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)

        # Create a human-readable report
        readable_report = f"""
# Drum Database Migration Report

## Summary

- **Total Databases:** {total_counts['databases']}
- **Total Size:** {total_counts['total_size_bytes'] / (1024 * 1024 * 1024):.2f} GB

## Database Types

{self._format_dict(total_counts['by_type'])}

## Instrument Types

{self._format_dict(total_counts['by_instrument'])}

## Special Datasets

{self._format_special_datasets()}

## Integration Status

The drum databases have been successfully integrated into the DrumTracKAI project.
Configuration has been written to `config/drum_database_config.json`.

## Dataset Access

Special datasets are accessible via symbolic links in the `datasets` directory:

{self._format_dataset_links()}

## Next Steps

1. Use the `get_db_adapter()` function to access the databases
2. Reference instrument types in your code
3. Update paths if G Drive location changes
"""

        readable_report_file = report_dir / "drum_database_report.md"
        with open(readable_report_file, 'w', encoding='utf-8') as f:
            f.write(readable_report.strip())

        logger.info(f"Report written to {report_file}")
        logger.info(f"Human-readable report written to {readable_report_file}")

        return report_file, readable_report_file

    def _format_dict(self, data_dict):
        """Format dictionary as markdown list"""
        return "\n".join([f"- **{key.capitalize()}:** {value}" for key, value in data_dict.items()])

    def _format_special_datasets(self):
        """Format special datasets as markdown list"""
        if not any(self.dataset_locations.values()):
            return "No special datasets found."

        result = ""
        for name, path in self.dataset_locations.items():
            if path:
                # Get size if structure information exists
                size_info = ""
                if name in self.db_stats and 'structure' in self.db_stats[name]:
                    size_gb = self.db_stats[name]['structure']['total_size'] / (1024 * 1024 * 1024)
                    size_info = f" ({size_gb:.2f} GB)"

                result += f"- **{name.capitalize()}**: {path}{size_info}\n"

        return result

    def _format_dataset_links(self):
        """Format dataset links as markdown list"""
        if not any(self.dataset_locations.values()):
            return "No dataset links created."

        result = ""
        for name, path in self.dataset_locations.items():
            if path:
                result += f"- `datasets/{name}` -> `{path}`\n"

        return result

    def update_env_file(self):
        """Update .env file with G Drive path"""
        env_file = Path(".env")

        if env_file.exists():
            with open(env_file, 'r', encoding='utf-8') as f:
                env_content = f.read()

            # Check if GDRIVE_PATH is already set
            if "GDRIVE_PATH" not in env_content:
                with open(env_file, 'a', encoding='utf-8') as f:
                    f.write(f"\nGDRIVE_PATH={self.gdrive_path}\n")
                logger.info("Updated .env file with G Drive path")
        else:
            # Create new .env file
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write(f"GDRIVE_PATH={self.gdrive_path}\n")
            logger.info("Created .env file with G Drive path")

    def create_db_adapter_config(self):
        """Create a configuration file specifically for the database adapter"""
        logger.info("Creating database adapter configuration...")

        # Build adapter config by instrument type
        adapter_config = {}

        for instrument_type, stats in self.db_stats.items():
            if not stats or instrument_type == 'unknown':
                continue

            # Initialize instrument entry
            adapter_config[instrument_type] = {
                'databases': [],
                'dataset_path': self.dataset_locations.get(instrument_type),
                'fallback_paths': [
                    os.path.join('datasets', instrument_type),
                    os.path.join(self.gdrive_path, instrument_type)
                ]
            }

            # Add database files
            for db_path, db_info in stats.items():
                if isinstance(db_info, dict) and 'path' in db_info:
                    adapter_config[instrument_type]['databases'].append({
                        'path': db_info['path'],
                        'type': db_info.get('instrument_type', instrument_type),
                        'format': next((fmt for fmt, dbs in self.databases.items()
                                        for db in dbs if db.get('path') == db_info['path']), 'unknown')
                    })

        # Add specialized adapter configuration for certain instruments
        if 'cymbal' in adapter_config:
            adapter_config['cymbal']['subtypes'] = self.instrument_types['cymbal']

        # Write database adapter configuration
        config_dir = Path("config")
        config_dir.mkdir(exist_ok=True)

        adapter_config_file = config_dir / "db_adapter_config.json"
        with open(adapter_config_file, 'w', encoding='utf-8') as f:
            json.dump(adapter_config, f, indent=2)

        logger.info(f"Database adapter configuration written to {adapter_config_file}")
        return adapter_config_file

    def run(self):
        """Run the full database integration process"""
        try:
            logger.info("Starting drum database integration...")
            logger.info(f"Using G Drive path: {self.gdrive_path}")

            # Scan for databases
            self.scan_for_databases()

            if not any(self.databases.values()):
                logger.error("No valid drum databases found")
                return False

            # Analyze special dataset structures
            self.analyze_dataset_structure()

            # Generate config file for all databases
            self.generate_config_file()

            # Create database adapter configuration
            self.create_db_adapter_config()

            # Create symbolic links to special datasets
            self.generate_dataset_symlinks()

            # Generate report
            self.generate_report()

            # Update .env file
            self.update_env_file()

            logger.info("Drum database integration completed successfully!")
            return True

        except Exception as e:
            logger.error(f"Integration failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False


def main():
    parser = argparse.ArgumentParser(description="Drum Database Integration for DrumTracKAI")
    parser.add_argument("--gdrive", help="Path to G Drive")
    args = parser.parse_args()

    try:
        integrator = DrumDatabaseIntegrator(args.gdrive)
        success = integrator.run()
        return 0 if success else 1
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())