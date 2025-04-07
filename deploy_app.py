#!/usr/bin/env python3
"""
Deployment Script for DrumTracKAI

This script handles the deployment of the DrumTracKAI application,
ensuring all components are properly installed and configured.
"""

import os
import sys
import time
import argparse
import subprocess
import shutil
from pathlib import Path

# Add config directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), "config"))

from config_manager import ConfigManager

class Deployer:
    """Handles deployment of the DrumTracKAI application."""
    
    def __init__(self, config_manager):
        """
        Initialize the deployer.
        
        Args:
            config_manager: Instance of ConfigManager
        """
        self.config_manager = config_manager
        self.base_path = config_manager.get_base_path()
    
    def run_command(self, command, cwd=None):
        """
        Run a command and return the result.
        
        Args:
            command: Command to run
            cwd: Working directory
            
        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        print(f"Running command: {command}")
        
        process = subprocess.Popen(
            command,
            cwd=cwd or self.base_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            text=True
        )
        
        stdout, stderr = process.communicate()
        
        return process.returncode, stdout, stderr
    
    def deploy_backend(self):
        """
        Deploy the FastAPI backend.
        
        Returns:
            True if successful, False otherwise
        """
        print("\n=== Deploying FastAPI Backend ===\n")
        
        # Get backend configuration
        backend_config = self.config_manager.get_component_config("fastapi_backend")
        backend_path = os.path.join(self.base_path, os.path.dirname(backend_config["path"]))
        
        # Check if the requirements file exists
        requirements_path = os.path.join(backend_path, "requirements.txt")
        if not os.path.exists(requirements_path):
            alt_requirements_path = os.path.join(self.base_path, "backend", "requirements.txt")
            if os.path.exists(alt_requirements_path):
                requirements_path = alt_requirements_path
            else:
                print(f"❌ Backend requirements file not found: {requirements_path}")
                return False
        
        # Install requirements
        print("Installing backend requirements...")
        returncode, stdout, stderr = self.run_command(
            f"{sys.executable} -m pip install -r {requirements_path}",
            cwd=backend_path
        )
        
        if returncode != 0:
            print(f"❌ Failed to install backend requirements: {stderr}")
            return False
        
        print("✅ Backend requirements installed successfully")
        
        # Run any database migrations or initialization
        if os.path.exists(os.path.join(backend_path, "init_db.py")):
            print("Initializing database...")
            returncode, stdout, stderr = self.run_command(
                f"{sys.executable} init_db.py",
                cwd=backend_path
            )
            
            if returncode != 0:
                print(f"❌ Failed to initialize database: {stderr}")
                return False
            
            print("✅ Database initialized successfully")
        
        print("✅ Backend deployment completed successfully")
        return True
    
    def deploy_frontend(self):
        """
        Deploy the Modern UI frontend.
        
        Returns:
            True if successful, False otherwise
        """
        print("\n=== Deploying Modern UI Frontend ===\n")
        
        # Get frontend configuration
        frontend_config = self.config_manager.get_component_config("modern_ui")
        frontend_path = os.path.join(self.base_path, frontend_config["path"])
        
        # Check if frontend directory exists
        if not os.path.isdir(frontend_path):
            # Try to find the frontend directory
            possible_frontend_paths = [
                os.path.join(self.base_path, "frontend", "modern-ui"),
                os.path.join(self.base_path, "frontend")
            ]
            
            for path in possible_frontend_paths:
                if os.path.isdir(path) and os.path.exists(os.path.join(path, "package.json")):
                    frontend_path = path
                    break
            else:
                print(f"❌ Frontend directory not found: {frontend_path}")
                return False
        
        # Check if package.json exists
        package_json_path = os.path.join(frontend_path, "package.json")
        if not os.path.exists(package_json_path):
            print(f"❌ Frontend package.json not found: {package_json_path}")
            return False
        
        # Install dependencies
        print("Installing frontend dependencies...")
        returncode, stdout, stderr = self.run_command(
            "npm install",
            cwd=frontend_path
        )
        
        if returncode != 0:
            print(f"❌ Failed to install frontend dependencies: {stderr}")
            return False
        
        print("✅ Frontend dependencies installed successfully")
        
        # Build the frontend
        print("Building frontend...")
        returncode, stdout, stderr = self.run_command(
            "npm run build",
            cwd=frontend_path
        )
        
        if returncode != 0:
            print(f"❌ Failed to build frontend: {stderr}")
            return False
        
        print("✅ Frontend built successfully")
        
        # Copy build to static directory if needed
        build_path = os.path.join(frontend_path, "build")
        if os.path.exists(build_path):
            static_path = os.path.join(self.base_path, "backend", "static")
            if not os.path.exists(static_path):
                os.makedirs(static_path)
            
            print(f"Copying build to static directory: {static_path}")
            for item in os.listdir(build_path):
                src = os.path.join(build_path, item)
                dst = os.path.join(static_path, item)
                
                if os.path.isdir(src):
                    if os.path.exists(dst):
                        shutil.rmtree(dst)
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)
            
            print("✅ Build copied to static directory")
        
        print("✅ Frontend deployment completed successfully")
        return True
    
    def deploy_training_dashboard(self):
        """
        Deploy the Training Dashboard.
        
        Returns:
            True if successful, False otherwise
        """
        print("\n=== Deploying Training Dashboard ===\n")
        
        # Get dashboard configuration
        dashboard_config = self.config_manager.get_component_config("training_dashboard")
        dashboard_path = os.path.join(self.base_path, os.path.dirname(dashboard_config["path"]))
        
        # Check if training dashboard script exists
        if not os.path.isdir(dashboard_path):
            # Try to find the training dashboard
            if os.path.exists(os.path.join(self.base_path, "training_dashboard.py")):
                dashboard_path = self.base_path
            else:
                print(f"❌ Training dashboard directory not found: {dashboard_path}")
                return False
        
        # Check if requirements exist
        requirements_paths = [
            os.path.join(dashboard_path, "requirements.txt"),
            os.path.join(self.base_path, "requirements.txt"),
            os.path.join(self.base_path, "ui-requirements.txt")
        ]
        
        for requirements_path in requirements_paths:
            if os.path.exists(requirements_path):
                print(f"Installing dashboard requirements from {requirements_path}...")
                returncode, stdout, stderr = self.run_command(
                    f"{sys.executable} -m pip install -r {requirements_path}",
                    cwd=dashboard_path
                )
                
                if returncode != 0:
                    print(f"❌ Failed to install dashboard requirements: {stderr}")
                    return False
                
                print("✅ Dashboard requirements installed successfully")
                break
        
        print("✅ Training Dashboard deployment completed successfully")
        return True
    
    def deploy_docker(self):
        """
        Deploy using Docker.
        
        Returns:
            True if successful, False otherwise
        """
        print("\n=== Deploying with Docker ===\n")
        
        # Check if docker-compose.yml exists
        docker_compose_path = os.path.join(self.base_path, "docker-compose.yml")
        if not os.path.exists(docker_compose_path):
            print(f"❌ Docker Compose file not found: {docker_compose_path}")
            return False
        
        # Build Docker images
        print("Building Docker images...")
        returncode, stdout, stderr = self.run_command(
            "docker-compose build",
            cwd=self.base_path
        )
        
        if returncode != 0:
            print(f"❌ Failed to build Docker images: {stderr}")
            return False
        
        print("✅ Docker images built successfully")
        
        # Start Docker containers
        print("Starting Docker containers...")
        returncode, stdout, stderr = self.run_command(
            "docker-compose up -d",
            cwd=self.base_path
        )
        
        if returncode != 0:
            print(f"❌ Failed to start Docker containers: {stderr}")
            return False
        
        print("✅ Docker containers started successfully")
        
        # Wait for services to initialize
        print("Waiting for services to initialize...")
        time.sleep(10)
        
        # Check if services are running
        returncode, stdout, stderr = self.run_command(
            "docker-compose ps",
            cwd=self.base_path
        )
        
        if "Exit" in stdout:
            print(f"❌ Some Docker containers exited: {stdout}")
            return False
        
        print("✅ Docker deployment completed successfully")
        return True
    
    def deploy_all(self, use_docker=False):
        """
        Deploy all components.
        
        Args:
            use_docker: Whether to use Docker for deployment
            
        Returns:
            True if successful, False otherwise
        """
        if use_docker:
            return self.deploy_docker()
        
        # Deploy individual components
        backend_success = self.deploy_backend()
        frontend_success = self.deploy_frontend()
        dashboard_success = self.deploy_training_dashboard()
        
        # Overall success
        success = backend_success and frontend_success and dashboard_success
        
        if success:
            print("\n✅ All components deployed successfully!")
        else:
            print("\n❌ Some components failed to deploy. Check the logs for details.")
        
        return success
    
    def start_all_services(self, use_docker=False):
        """
        Start all services after deployment.
        
        Args:
            use_docker: Whether to use Docker for services
            
        Returns:
            True if successful, False otherwise
        """
        print("\n=== Starting All Services ===\n")
        
        if use_docker:
            print("Services are already running in Docker containers.")
            return True
        
        # Use the validation pipeline to start services
        print("Using validation pipeline to start services...")
        returncode, stdout, stderr = self.run_command(
            f"{sys.executable} validation_pipeline.py --start",
            cwd=self.base_path
        )
        
        if returncode != 0:
            print(f"❌ Failed to start services: {stderr}")
            return False
        
        print("✅ Services started successfully")
        return True

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Deploy DrumTracKAI application")
    parser.add_argument("--docker", action="store_true", help="Use Docker for deployment")
    parser.add_argument("--backend-only", action="store_true", help="Deploy only the backend")
    parser.add_argument("--frontend-only", action="store_true", help="Deploy only the frontend")
    parser.add_argument("--dashboard-only", action="store_true", help="Deploy only the training dashboard")
    parser.add_argument("--no-start", action="store_true", help="Don't start services after deployment")
    
    args = parser.parse_args()
    
    # Create config manager
    config_manager = ConfigManager()
    
    # Create deployer
    deployer = Deployer(config_manager)
    
    # Deploy components
    if args.backend_only:
        success = deployer.deploy_backend()
    elif args.frontend_only:
        success = deployer.deploy_frontend()
    elif args.dashboard_only:
        success = deployer.deploy_training_dashboard()
    else:
        success = deployer.deploy_all(use_docker=args.docker)
    
    # Start services if deployment was successful
    if success and not args.no_start:
        deployer.start_all_services(use_docker=args.docker)

if __name__ == "__main__":
    main()