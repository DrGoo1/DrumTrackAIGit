#!/usr/bin/env python3
"""
DrumTracKAI Project Update Script
This script adds new directories and files to your existing DrumTracKAI project.
"""

import os
import sys
import shutil

# Set this to your project path
PROJECT_ROOT = r"C:\Users\goldw\DrumTracKAI"


def create_directory(path):
    """Create directory if it doesn't exist"""
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Created directory: {path}")
    else:
        print(f"Directory already exists: {path}")


def create_file(path, content="", overwrite=False):
    """Create file with given content"""
    dirname = os.path.dirname(path)
    if dirname and not os.path.exists(dirname):
        os.makedirs(dirname)

    if os.path.exists(path) and not overwrite:
        print(f"File already exists (not overwriting): {path}")
        return False

    with open(path, 'w') as f:
        f.write(content)
    print(f"Created file: {path}")
    return True


def update_project():
    """Update the DrumTracKAI project structure"""
    print(f"Updating DrumTracKAI project in: {PROJECT_ROOT}")

    # Create necessary directories if they don't exist
    print("\nCreating required directories...")
    create_directory(os.path.join(PROJECT_ROOT, "backend", "drumtrackkai", "utils"))
    create_directory(os.path.join(PROJECT_ROOT, "backend", "drumtrackkai", "static", "swagger"))
    create_directory(os.path.join(PROJECT_ROOT, "backend", "logs"))
    create_directory(os.path.join(PROJECT_ROOT, "backend", "uploads", "audio"))
    create_directory(os.path.join(PROJECT_ROOT, "backend", "results"))

    # Create __init__.py files if they don't exist
    print("\nCreating package __init__.py files...")
    create_file(os.path.join(PROJECT_ROOT, "backend", "drumtrackkai", "utils", "__init__.py"))

    # Add new files from artifacts
    print("\nAdding new artifact files...")

    # 1. Custom Exceptions
    exceptions_file = os.path.join(PROJECT_ROOT, "backend", "drumtrackkai", "utils", "exceptions.py")
    if create_file(exceptions_file, "", overwrite=False):
        print("Please copy the content from 'custom-exceptions' artifact to this file.")

    # 2. Error Handler
    error_handler_file = os.path.join(PROJECT_ROOT, "backend", "drumtrackkai", "utils", "error_handler.py")
    if create_file(error_handler_file, "", overwrite=False):
        print("Please copy the content from 'error-handler' artifact to this file.")

    # 3. Database Utilities
    db_utils_file = os.path.join(PROJECT_ROOT, "backend", "drumtrackkai", "utils", "db_utils.py")
    if create_file(db_utils_file, "", overwrite=False):
        print("Please copy the content from 'database-utils' artifact to this file.")

    # 4. Task Model
    task_model_file = os.path.join(PROJECT_ROOT, "backend", "drumtrackkai", "models", "task.py")
    if create_file(task_model_file, "", overwrite=False):
        print("Please copy the content from 'task-model' artifact to this file.")

    # 5. YouTube Service
    youtube_service_file = os.path.join(PROJECT_ROOT, "backend", "drumtrackkai", "services", "youtube_service.py")
    if create_file(youtube_service_file, "", overwrite=False):
        print("Please copy the content from 'youtube-service' artifact to this file.")

    # 6. Task Service
    task_service_file = os.path.join(PROJECT_ROOT, "backend", "drumtrackkai", "services", "task_service.py")
    if create_file(task_service_file, "", overwrite=False):
        print("Please copy the content from 'task-service' artifact to this file.")

    # 7. YouTube Controller
    youtube_controller_file = os.path.join(PROJECT_ROOT, "backend", "drumtrackkai", "api", "youtube.py")
    if create_file(youtube_controller_file, "", overwrite=False):
        print("Please copy the content from 'youtube-controller' artifact to this file.")

    # 8. Configuration
    config_file = os.path.join(PROJECT_ROOT, "backend", "drumtrackkai", "config.py")
    if create_file(config_file, "", overwrite=False):
        print("Please copy the content from 'config' artifact to this file.")

    # 9. Application Initialization
    init_file = os.path.join(PROJECT_ROOT, "backend", "drumtrackkai", "__init__.py")
    if os.path.exists(init_file):
        backup_file = init_file + ".backup"
        print(f"Backing up existing __init__.py to {backup_file}")
        shutil.copy2(init_file, backup_file)
        print("Please update __init__.py with content from 'init-file' artifact (after making backup).")
    else:
        create_file(init_file, "")
        print("Please copy the content from 'init-file' artifact to this file.")

    # 10. API Specification
    swagger_file = os.path.join(PROJECT_ROOT, "backend", "drumtrackkai", "static", "swagger", "swagger.json")
    if create_file(swagger_file, "", overwrite=False):
        print("Please copy the content from 'api-specification' artifact to this file.")

    print("\nDirectory structure updated!")
    print("\nNext steps:")
    print("1. Copy the content from each artifact into its corresponding file")
    print("2. Install additional dependencies:")
    print("   cd " + os.path.join(PROJECT_ROOT, "backend"))
    print("   pip install flask-swagger-ui yt-dlp google-api-python-client validators flask-limiter")
    print("3. Update the .env file with additional variables")
    print("4. Run the application:")
    print("   flask run")
    print("\nNote: Be careful when updating __init__.py to preserve your existing functionality")


if __name__ == "__main__":
    update_project()