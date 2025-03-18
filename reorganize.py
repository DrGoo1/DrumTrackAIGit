#!/usr/bin/env python
"""
DrumTrackKit Project Reorganization Script

This script reorganizes the current project structure to a cleaner, more consistent layout.
It preserves important files while fixing the naming and organization.

Usage:
    python reorganize.py
"""

import os
import shutil
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Project paths
PROJECT_ROOT = Path.cwd()  # Current directory should be the project root
ORIGINAL_V2_PROJECT = Path(r"C:\Users\goldw\PycharmProjects\DrumTracKAI_V2")

# New structure directories
NEW_DIRS = [
    "drumtrackkit",
    "drumtrackkit/api",
    "drumtrackkit/models",
    "drumtrackkit/services",
    "drumtrackkit/utils",
    "drumtrackkit/drum_analysis",
    "app",
    "docker",
    "instance",
    "logs",
    "results",
    "tests",
    "uploads",
]

# Files to exclude from copying
EXCLUDE_FILES = [
    "__pycache__",
    "*.pyc",
    "*.pyo",
    ".git",
    ".idea",
    ".vscode",
    "venv",
]


def create_new_structure():
    """Create the new directory structure"""
    logger.info("Creating new directory structure...")

    for dir_path in NEW_DIRS:
        new_dir = PROJECT_ROOT / dir_path
        new_dir.mkdir(exist_ok=True)
        logger.info(f"Created directory: {new_dir}")

    logger.info("Directory structure created.")


def should_copy_file(path):
    """Check if a file should be copied or excluded"""
    path_str = str(path).lower()
    return not any(exclude in path_str for exclude in EXCLUDE_FILES)


def copy_files_from_backend():
    """Copy files from the backend directory to the new structure"""
    logger.info("Copying files from backend directory...")

    backend_dir = PROJECT_ROOT / "backend"
    if not backend_dir.exists():
        logger.warning(f"Backend directory not found at {backend_dir}")
        return

    # Copy app directory content
    app_dir = backend_dir / "app"
    if app_dir.exists():
        dest_app_dir = PROJECT_ROOT / "app"
        copy_directory_contents(app_dir, dest_app_dir)

    # Copy Docker directory content
    docker_dir = backend_dir / "docker"
    if docker_dir.exists():
        dest_docker_dir = PROJECT_ROOT / "docker"
        copy_directory_contents(docker_dir, dest_docker_dir)

    # Copy drumtrackkai directory content to new main package
    drumtrackkai_dir = backend_dir / "drumtrackkai"
    if drumtrackkai_dir.exists():
        dest_package_dir = PROJECT_ROOT / "drumtrackkit"
        copy_directory_contents(drumtrackkai_dir, dest_package_dir)

    # Copy other directories
    for dirname in ["instance", "logs", "results", "tests", "uploads"]:
        src_dir = backend_dir / dirname
        if src_dir.exists():
            dest_dir = PROJECT_ROOT / dirname
            copy_directory_contents(src_dir, dest_dir)

    # Copy Python files from backend root to project root
    for py_file in backend_dir.glob("*.py"):
        if should_copy_file(py_file):
            dest_file = PROJECT_ROOT / py_file.name
            shutil.copy2(py_file, dest_file)
            logger.info(f"Copied file: {py_file.name}")

    # Copy requirements.txt and other config files
    for file_pattern in ["requirements*.txt", "*.yml", "*.yaml", "*.json", "*.md"]:
        for config_file in backend_dir.glob(file_pattern):
            if should_copy_file(config_file):
                dest_file = PROJECT_ROOT / config_file.name
                shutil.copy2(config_file, dest_file)
                logger.info(f"Copied file: {config_file.name}")

    logger.info("Backend files copied.")


def copy_drum_analysis_module():
    """Copy drum_analysis module from the original V2 project"""
    logger.info("Copying drum_analysis module from original project...")

    src_analysis_dir = ORIGINAL_V2_PROJECT / "drum_analysis"
    if not src_analysis_dir.exists():
        logger.warning(f"Drum analysis directory not found at {src_analysis_dir}")
        return

    dest_analysis_dir = PROJECT_ROOT / "drumtrackkit" / "drum_analysis"
    copy_directory_contents(src_analysis_dir, dest_analysis_dir)

    logger.info("Drum analysis module copied.")


def copy_directory_contents(src_dir, dest_dir):
    """Copy all contents from source to destination directory"""
    if not src_dir.exists():
        logger.warning(f"Source directory not found: {src_dir}")
        return

    dest_dir.mkdir(exist_ok=True)

    # Copy files
    file_count = 0
    for file_path in src_dir.glob("**/*"):
        if file_path.is_file() and should_copy_file(file_path):
            # Create the relative path in the destination
            rel_path = file_path.relative_to(src_dir)
            dest_file = dest_dir / rel_path

            # Create parent directories if they don't exist
            dest_file.parent.mkdir(exist_ok=True, parents=True)

            # Copy the file
            shutil.copy2(file_path, dest_file)
            file_count += 1

    logger.info(f"Copied {file_count} files from {src_dir.name} to {dest_dir.name}")


def update_imports():
    """Update import statements in Python files"""
    logger.info("Updating import statements...")

    # Replacement mapping
    replacements = {
        "from drumtrackkit.drum_analysis": "from drumtrackkit.drum_analysis",
        "import drumtrackkit.drum_analysis": "import drumtrackkit.drum_analysis",
        "from drumtrackkit": "from drumtrackkit",
        "import drumtrackkit": "import drumtrackkit",
    }

    # Get all Python files
    python_files = list(PROJECT_ROOT.glob("**/*.py"))
    updated_files = 0

    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for any needed replacements
            modified = False
            new_content = content

            for old_text, new_text in replacements.items():
                if old_text in new_content:
                    new_content = new_content.replace(old_text, new_text)
                    modified = True

            # Write back if changed
            if modified:
                with open(py_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                updated_files += 1
                logger.info(f"Updated imports in: {py_file}")

        except Exception as e:
            logger.warning(f"Error updating {py_file}: {e}")

    logger.info(f"Updated imports in {updated_files} files.")


def create_init_files():
    """Create __init__.py files in all Python package directories"""
    logger.info("Creating __init__.py files...")

    # Get all directories in the project
    for dir_path in PROJECT_ROOT.glob("**/"):
        # Skip venv, __pycache__, .git, etc.
        if should_copy_file(dir_path):
            # Check if there are any .py files in this directory
            py_files = list(dir_path.glob("*.py"))
            if py_files:
                init_file = dir_path / "__init__.py"
                if not init_file.exists():
                    # Create an empty __init__.py
                    with open(init_file, 'w', encoding='utf-8') as f:
                        package_name = str(dir_path.relative_to(PROJECT_ROOT)).replace("\\", ".")
                        f.write(f'"""\n{package_name} package\n"""\n\n')
                    logger.info(f"Created: {init_file}")

    logger.info("__init__.py files created.")


def run():
    """Run the reorganization process"""
    logger.info("Starting project reorganization...")

    try:
        # Create new structure
        create_new_structure()

        # Copy files from backend
        copy_files_from_backend()

        # Copy drum_analysis module
        copy_drum_analysis_module()

        # Update import statements
        update_imports()

        # Create __init__.py files
        create_init_files()

        logger.info("Project reorganization completed successfully!")
        logger.info("\nNext steps:")
        logger.info("1. Open the project in PyCharm")
        logger.info("2. Configure the Python interpreter")
        logger.info("3. Check that import statements are working correctly")
        logger.info("4. Run the application to verify functionality")

    except Exception as e:
        logger.error(f"Reorganization failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

    return True


if __name__ == "__main__":
    run()