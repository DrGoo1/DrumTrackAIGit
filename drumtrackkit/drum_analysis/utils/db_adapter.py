# drum_analysis/utils/db_adapter.py

"""
Database adapter for the DrumTracKAI framework.

This module provides a database adapter to integrate with the existing
DrumTracKAI database system, as well as standalone database functionality
for when the framework is used independently.
"""

import os
import sqlite3
import pandas as pd
import csv
import json
import logging
import traceback
from typing import Dict, Any, List, Optional, Tuple, Union
from pathlib import Path

# Local imports
try:
    from .config import get_config
except ImportError:
    # Simple fallback if config module is not available
    def get_config(key, default=None):
        """Simple fallback for config when module not available."""
        return default

# Just use standard logging instead of get_logger
logger = logging.getLogger(__name__)


class DatabaseAdapter:
    """
    Database adapter for the DrumTracKAI framework.

    Provides an interface to interact with either:
    1. The existing DrumTracKAI database system
    2. A standalone database for independent use
    """

    def __init__(self, db_manager=None, db_path: Optional[str] = None):
        """
        Initialize the database adapter.

        Args:
            db_manager: Optional existing DrumTracKAI database manager
            db_path: Optional path to SQLite database for standalone mode
        """
        self.db_manager = db_manager
        self.db_path = db_path or get_config('database_path', './data/drumtrackai.db')
        self.standalone_mode = db_manager is None

        # Convert to absolute path for clarity in error messages
        self.db_path = os.path.abspath(self.db_path)
        logger.info(f"Database path set to: {self.db_path}")

        # Initialize standalone database if needed
        if self.standalone_mode:
            try:
                self._init_standalone_db()
            except Exception as e:
                logger.error(f"Error initializing standalone database: {e}")
                logger.error(traceback.format_exc())
                raise

    def _init_standalone_db(self) -> None:
        """Initialize the standalone database."""
        # Create directory if it doesn't exist
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            try:
                os.makedirs(db_dir, exist_ok=True)
                logger.info(f"Created database directory: {db_dir}")
            except Exception as e:
                logger.error(f"Failed to create database directory {db_dir}: {e}")
                raise

        # Test if we can write to the directory
        if not os.access(db_dir, os.W_OK):
            logger.error(f"No write permission to database directory: {db_dir}")
            raise PermissionError(f"No write permission to database directory: {db_dir}")

        # Create tables if they don't exist
        try:
            conn = self._get_connection()
            logger.info("Successfully connected to database")

            cursor = conn.cursor()

            # Create tables for different instrument types
            for instrument in ['kick', 'snare', 'cymbal', 'tom']:
                cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {instrument}_samples (
                    id INTEGER PRIMARY KEY,
                    file_name TEXT,
                    file_path TEXT,
                    purpose TEXT,
                    features TEXT,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """)

            # Create table for analysis results
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_results (
                id INTEGER PRIMARY KEY,
                file_path TEXT,
                purpose TEXT,
                instrument_type TEXT,
                results TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            conn.commit()
            logger.info("Initialized standalone database tables")
        except Exception as e:
            logger.error(f"Error creating database tables: {e}")
            logger.error(traceback.format_exc())
            raise
        finally:
            if 'conn' in locals() and conn:
                conn.close()

    def _get_connection(self) -> sqlite3.Connection:
        """
        Get a database connection.

        Returns:
            sqlite3.Connection: Connection to the database
        """
        if self.standalone_mode:
            try:
                # Make sure the directory exists before trying to connect
                db_dir = os.path.dirname(self.db_path)
                if db_dir and not os.path.exists(db_dir):
                    os.makedirs(db_dir, exist_ok=True)
                    logger.info(f"Created database directory: {db_dir}")

                # Try to connect to the database
                logger.debug(f"Connecting to database at: {self.db_path}")
                conn = sqlite3.connect(self.db_path)
                return conn
            except Exception as e:
                logger.error(f"Failed to connect to database at {self.db_path}: {e}")
                logger.error(traceback.format_exc())
                raise
        else:
            # In integrated mode, get the connection from the db_manager
            return self.db_manager.get_connection()

    def get_samples(self, instrument_type: str = None, purpose: str = None,
                    limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get samples from the database with optional filtering.

        Args:
            instrument_type: Optional instrument type filter (kick, snare, cymbal, tom)
            purpose: Optional purpose filter (sonic_reference, technique_training, etc.)
            limit: Maximum number of samples to return

        Returns:
            List of sample dictionaries
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            if self.standalone_mode:
                if instrument_type:
                    table_name = f"{instrument_type}_samples"
                    query = f"SELECT * FROM {table_name}"
                    params = []

                    if purpose:
                        query += " WHERE purpose = ?"
                        params.append(purpose)

                    query += f" LIMIT {limit}"
                    cursor.execute(query, params)

                    columns = [desc[0] for desc in cursor.description]
                    results = []

                    for row in cursor.fetchall():
                        sample = dict(zip(columns, row))
                        # Convert JSON strings back to dictionaries
                        if 'features' in sample and sample['features']:
                            sample['features'] = json.loads(sample['features'])
                        if 'metadata' in sample and sample['metadata']:
                            sample['metadata'] = json.loads(sample['metadata'])
                        results.append(sample)

                    return results
                else:
                    # If no instrument type specified, query all instrument tables
                    results = []
                    for inst in ['kick', 'snare', 'cymbal', 'tom']:
                        query = f"SELECT * FROM {inst}_samples"
                        params = []

                        if purpose:
                            query += " WHERE purpose = ?"
                            params.append(purpose)

                        query += f" LIMIT {limit // 4}"  # Divide limit among tables
                        cursor.execute(query, params)

                        columns = [desc[0] for desc in cursor.description]
                        for row in cursor.fetchall():
                            sample = dict(zip(columns, row))
                            # Add instrument type since it's not in the table
                            sample['instrument_type'] = inst
                            # Convert JSON strings back to dictionaries
                            if 'features' in sample and sample['features']:
                                sample['features'] = json.loads(sample['features'])
                            if 'metadata' in sample and sample['metadata']:
                                sample['metadata'] = json.loads(sample['metadata'])
                            results.append(sample)

                    return results
            else:
                # In integrated mode, use the db_manager's methods
                return self.db_manager.get_samples(
                    instrument_type=instrument_type,
                    purpose=purpose,
                    limit=limit
                )
        except Exception as e:
            logger.error(f"Error retrieving samples: {e}")
            logger.error(traceback.format_exc())
            return []
        finally:
            if self.standalone_mode and conn:
                conn.close()

    def save_sample(self, instrument_type: str, file_path: str, file_name: str = None,
                    purpose: str = None, features: Dict[str, Any] = None,
                    metadata: Dict[str, Any] = None) -> int:
        """
        Save a sample to the database.

        Args:
            instrument_type: Instrument type (kick, snare, cymbal, tom)
            file_path: Path to the sample file
            file_name: Optional file name (extracted from path if not provided)
            purpose: Optional purpose classification
            features: Optional features dictionary
            metadata: Optional metadata dictionary

        Returns:
            int: ID of the saved sample
        """
        if not file_name:
            file_name = os.path.basename(file_path)

        # Convert dictionaries to JSON strings
        features_json = json.dumps(features) if features else None
        metadata_json = json.dumps(metadata) if metadata else None

        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            if self.standalone_mode:
                table_name = f"{instrument_type}_samples"
                cursor.execute(f"""
                INSERT INTO {table_name} (file_name, file_path, purpose, features, metadata)
                VALUES (?, ?, ?, ?, ?)
                """, (file_name, file_path, purpose, features_json, metadata_json))

                conn.commit()
                return cursor.lastrowid
            else:
                # In integrated mode, use the db_manager's methods
                return self.db_manager.save_sample(
                    instrument_type=instrument_type,
                    file_path=file_path,
                    file_name=file_name,
                    purpose=purpose,
                    features=features,
                    metadata=metadata
                )
        except Exception as e:
            logger.error(f"Error saving sample: {e}")
            logger.error(traceback.format_exc())
            return -1
        finally:
            if self.standalone_mode and conn:
                conn.close()

    def save_analysis_result(self, file_path: str, instrument_type: str,
                             purpose: str, results: Dict[str, Any]) -> int:
        """
        Save analysis results to the database.

        Args:
            file_path: Path to the analyzed file
            instrument_type: Instrument type
            purpose: Purpose classification
            results: Analysis results dictionary

        Returns:
            int: ID of the saved result
        """
        # Convert results dict to JSON string
        results_json = json.dumps(results)

        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            if self.standalone_mode:
                cursor.execute("""
                INSERT INTO analysis_results (file_path, instrument_type, purpose, results)
                VALUES (?, ?, ?, ?)
                """, (file_path, instrument_type, purpose, results_json))

                conn.commit()
                return cursor.lastrowid
            else:
                # In integrated mode, use the db_manager's methods
                return self.db_manager.save_analysis_result(
                    file_path=file_path,
                    instrument_type=instrument_type,
                    purpose=purpose,
                    results=results
                )
        except Exception as e:
            logger.error(f"Error saving analysis result: {e}")
            logger.error(traceback.format_exc())
            return -1
        finally:
            if self.standalone_mode and conn:
                conn.close()

    def get_analysis_results(self, instrument_type: str = None,
                             purpose: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get analysis results from the database.

        Args:
            instrument_type: Optional instrument type filter
            purpose: Optional purpose filter
            limit: Maximum number of results to return

        Returns:
            List of result dictionaries
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            if self.standalone_mode:
                query = "SELECT * FROM analysis_results"
                params = []

                # Build WHERE clause
                where_clauses = []
                if instrument_type:
                    where_clauses.append("instrument_type = ?")
                    params.append(instrument_type)
                if purpose:
                    where_clauses.append("purpose = ?")
                    params.append(purpose)

                if where_clauses:
                    query += " WHERE " + " AND ".join(where_clauses)

                query += f" LIMIT {limit}"
                cursor.execute(query, params)

                columns = [desc[0] for desc in cursor.description]
                results = []

                for row in cursor.fetchall():
                    result = dict(zip(columns, row))
                    # Convert JSON string back to dictionary
                    if 'results' in result and result['results']:
                        result['results'] = json.loads(result['results'])
                    results.append(result)

                return results
            else:
                # In integrated mode, use the db_manager's methods
                return self.db_manager.get_analysis_results(
                    instrument_type=instrument_type,
                    purpose=purpose,
                    limit=limit
                )
        except Exception as e:
            logger.error(f"Error retrieving analysis results: {e}")
            logger.error(traceback.format_exc())
            return []
        finally:
            if self.standalone_mode and conn:
                conn.close()

    def export_to_csv(self, table_name: str, output_path: str) -> None:
        """
        Export a table to CSV.

        Args:
            table_name: Name of the table to export
            output_path: Path to save the CSV file
        """
        conn = None
        try:
            conn = self._get_connection()
            # Create a DataFrame from the table
            df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)

            # Save to CSV
            df.to_csv(output_path, index=False)
            logger.info(f"Exported {table_name} to {output_path}")
        except Exception as e:
            logger.error(f"Error exporting table to CSV: {e}")
            logger.error(traceback.format_exc())
        finally:
            if self.standalone_mode and conn:
                conn.close()

    def import_from_csv(self, table_name: str, input_path: str) -> int:
        """
        Import data from CSV to a table.

        Args:
            table_name: Name of the table to import into
            input_path: Path to the CSV file

        Returns:
            int: Number of rows imported
        """
        try:
            # Read CSV file
            df = pd.read_csv(input_path)

            conn = self._get_connection()
            try:
                # Insert DataFrame into the table
                df.to_sql(table_name, conn, if_exists='append', index=False)
                return len(df)
            finally:
                if self.standalone_mode:
                    conn.close()
        except Exception as e:
            logger.error(f"Error importing data from CSV: {e}")
            logger.error(traceback.format_exc())
            return 0

    def get_db_info(self) -> Dict[str, Any]:
        """
        Get information about the database.

        This is useful for debugging database connection issues.

        Returns:
            Dictionary with database information
        """
        info = {
            'db_path': self.db_path,
            'db_exists': os.path.exists(self.db_path),
            'db_size_bytes': os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0,
            'db_directory': os.path.dirname(self.db_path),
            'dir_exists': os.path.exists(os.path.dirname(self.db_path)),
            'dir_writable': os.access(os.path.dirname(self.db_path), os.W_OK)
            if os.path.exists(os.path.dirname(self.db_path)) else False,
            'tables': []
        }

        # Try to get list of tables
        if self.standalone_mode and os.path.exists(self.db_path):
            try:
                conn = self._get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                info['tables'] = [row[0] for row in cursor.fetchall()]
                conn.close()
            except Exception as e:
                info['connection_error'] = str(e)

        return info


# Replace the singleton creation at the end of db_adapter.py with this code:

# Create a singleton instance for easy import - with better default path handling
_singleton_instance = None


def get_db_adapter():
    """
    Get the singleton instance of DatabaseAdapter.

    This function lazily initializes the adapter on first call
    and handles initialization failures gracefully.

    Returns:
        DatabaseAdapter: The singleton instance
    """
    global _singleton_instance
    if _singleton_instance is None:
        try:
            # Try to use a reliable path in user's home directory
            home_dir = os.path.expanduser("~")
            drumtrackai_dir = os.path.join(home_dir, ".drumtrackai")
            if not os.path.exists(drumtrackai_dir):
                os.makedirs(drumtrackai_dir, exist_ok=True)

            db_path = os.path.join(drumtrackai_dir, "drumtrackai.db")
            _singleton_instance = DatabaseAdapter(db_path=db_path)
            logger.info(f"Database adapter singleton initialized at {db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize database adapter in home directory: {e}")
            try:
                # Fall back to current directory
                db_path = os.path.join(os.getcwd(), "drumtrackai.db")
                _singleton_instance = DatabaseAdapter(db_path=db_path)
                logger.info(f"Database adapter singleton initialized at {db_path}")
            except Exception as e:
                logger.error(f"Failed to initialize database adapter in current directory: {e}")
                # Create a non-functional stub as last resort
                logger.warning("Using in-memory database as fallback")
                _singleton_instance = DatabaseAdapter(db_path=":memory:")

    return _singleton_instance


# For backward compatibility, create a db_adapter variable
# that points to the function
db_adapter = get_db_adapter()