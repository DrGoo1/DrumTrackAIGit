#!/usr/bin/env python3
"""
Validation Pipeline for DrumTracKAI

This script verifies that all components are present, correctly configured,
and can be launched successfully.
"""

import os
import sys
import time
import json
import subprocess
import requests
from pathlib import Path
import argparse
import psutil

# Add config directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), "config"))

from config_manager import ConfigManager

class ValidationPipeline:
    """Pipeline for validating DrumTracKAI components."""
    
    def __init__(self, config_manager):
        """
        Initialize the validation pipeline.
        
        Args:
            config_manager: Instance of ConfigManager
        """
        self.config_manager = config_manager
        self.results = {}
        
    def validate_component_files(self, component_name):
        """
        Validate that a component's files exist.
        
        Args:
            component_name: Name of the component
            
        Returns:
            True if files exist, False otherwise
        """
        component_path = self.config_manager.get_component_path(component_name)
        if not component_path:
            print(f"Error: No path configuration for component {component_name}")
            return False
        
        # Check if the path exists
        parent_dir = os.path.dirname(component_path)
        if os.path.exists(parent_dir):
            print(f"✓ Component '{component_name}' parent directory found at: {parent_dir}")
            return True
        else:
            print(f"✗ Component '{component_name}' parent directory not found at: {parent_dir}")
            return False
    
    def validate_launch_script(self, component_name):
        """
        Validate that a component's launch script exists.
        
        Args:
            component_name: Name of the component
            
        Returns:
            True if the launch script exists, False otherwise
        """
        component = self.config_manager.get_component_config(component_name)
        if not component:
            return False
        
        # If it's a direct command (like python script.py)
        if component["launch_script"].startswith("python"):
            script_path = component["launch_script"].split()[1]
            full_path = os.path.join(self.config_manager.get_base_path(), script_path)
        else:
            # It's a script file
            full_path = self.config_manager.get_component_launch_script(component_name)
        
        if os.path.exists(full_path):
            print(f"✓ Launch script for '{component_name}' found at: {full_path}")
            return True
        else:
            print(f"✗ Launch script for '{component_name}' not found at: {full_path}")
            return False
    
    def is_port_in_use(self, port):
        """Check if a port is in use."""
        try:
            for conn in psutil.net_connections():
                if hasattr(conn, 'laddr') and hasattr(conn.laddr, 'port'):
                    if conn.laddr.port == port and conn.status == 'LISTEN':
                        return True
            return False
        except (psutil.AccessDenied, AttributeError):
            # Fallback method if psutil doesn't have access
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            return result == 0
    
    def check_component_running(self, component_name):
        """
        Check if a component is already running.
        
        Args:
            component_name: Name of the component
            
        Returns:
            True if the component is running, False otherwise
        """
        component = self.config_manager.get_component_config(component_name)
        if not component:
            return False
        
        # Check if the component has a port
        if "port" in component:
            port = component["port"]
            if self.is_port_in_use(port):
                print(f"✓ Component '{component_name}' is running on port {port}")
                
                # If it has a health endpoint, check that too
                if "health_endpoint" in component:
                    try:
                        health_url = f"http://localhost:{port}{component['health_endpoint']}"
                        response = requests.get(health_url, timeout=5)
                        if response.status_code == 200:
                            print(f"✓ Health check passed for '{component_name}'")
                            return True
                        else:
                            print(f"✗ Health check failed for '{component_name}': Status {response.status_code}")
                    except requests.exceptions.RequestException:
                        print(f"✗ Health check connection failed for '{component_name}'")
                else:
                    # No health endpoint, just assume it's running
                    return True
            else:
                print(f"✗ Component '{component_name}' is not running on port {port}")
                return False
        
        # If no port is specified, we can't check if it's running
        print(f"! Cannot determine if '{component_name}' is running (no port specified)")
        return None
    
    def start_component(self, component_name):
        """
        Start a component.
        
        Args:
            component_name: Name of the component
            
        Returns:
            True if the component was started successfully, False otherwise
        """
        print(f"Starting component '{component_name}'...")
        
        # Check dependencies
        for dependency in self.config_manager.get_component_dependencies(component_name):
            if not self.check_component_running(dependency):
                print(f"✗ Cannot start '{component_name}': Dependency '{dependency}' is not running")
                return False
        
        # Get the launch script
        launch_script = self.config_manager.get_component_launch_script(component_name)
        base_path = self.config_manager.get_base_path()
        
        try:
            if launch_script.endswith(".bat") or launch_script.endswith(".sh"):
                # It's a script file
                process = subprocess.Popen(launch_script, cwd=base_path, shell=True)
            else:
                # It's a direct command
                process = subprocess.Popen(launch_script, cwd=base_path, shell=True)
            
            # Wait a moment for the process to start
            time.sleep(5)
            
            # Check if the component is now running
            if self.check_component_running(component_name):
                print(f"✓ Successfully started '{component_name}'")
                return True
            else:
                print(f"✗ Failed to start '{component_name}'")
                return False
        except Exception as e:
            print(f"✗ Error starting '{component_name}': {str(e)}")
            return False
    
    def validate_all_components(self):
        """
        Validate all components.
        
        Returns:
            Dictionary of validation results
        """
        components = self.config_manager.get_all_components()
        
        for component in components:
            print(f"\n=== Validating component: {component} ===")
            
            # Check if files exist
            files_exist = self.validate_component_files(component)
            
            # Check if launch script exists
            script_exists = self.validate_launch_script(component)
            
            # Check if component is running
            is_running = self.check_component_running(component)
            
            # Store results
            self.results[component] = {
                "files_exist": files_exist,
                "script_exists": script_exists,
                "is_running": is_running
            }
        
        return self.results
    
    def start_required_components(self, components=None):
        """
        Start components that are not running.
        
        Args:
            components: List of component names to start. If None, starts all.
            
        Returns:
            List of components that were successfully started
        """
        if not components:
            # Get components in correct order based on dependencies
            components = self.config_manager.get_component_launch_order()
        
        started = []
        
        for component in components:
            # Check if component is running
            if self.check_component_running(component) is not True:
                # Not running, try to start it
                if self.start_component(component):
                    started.append(component)
        
        return started
    
    def generate_report(self):
        """
        Generate a validation report.
        
        Returns:
            Report as a string
        """
        report = "# DrumTracKAI Validation Report\n\n"
        report += f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        report += "## Component Status\n\n"
        report += "| Component | Files Exist | Launch Script | Running |\n"
        report += "|-----------|------------|--------------|--------|\n"
        
        for component, result in self.results.items():
            files = "✅" if result["files_exist"] else "❌"
            script = "✅" if result["script_exists"] else "❌"
            running = "✅" if result["is_running"] is True else "❌" if result["is_running"] is False else "❓"
            
            report += f"| {component} | {files} | {script} | {running} |\n"
        
        report += "\n## Recommendations\n\n"
        
        # Make recommendations
        for component, result in self.results.items():
            if not result["files_exist"]:
                report += f"- Component '{component}' files are missing. Check the path in the configuration.\n"
            if not result["script_exists"]:
                report += f"- Launch script for '{component}' is missing. Check the script path.\n"
            if result["is_running"] is False:
                report += f"- Component '{component}' is not running. Start it with `{self.config_manager.get_component_launch_script(component)}`\n"
        
        return report

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Validate DrumTracKAI components")
    parser.add_argument("--start", action="store_true", help="Start components that are not running")
    parser.add_argument("--report", action="store_true", help="Generate a validation report")
    parser.add_argument("--component", help="Validate only this component")
    
    args = parser.parse_args()
    
    # Initialize the config manager
    config_manager = ConfigManager()
    
    # Create validation pipeline
    pipeline = ValidationPipeline(config_manager)
    
    # Validate components
    if args.component:
        # Validate only one component
        print(f"\n=== Validating component: {args.component} ===")
        pipeline.validate_component_files(args.component)
        pipeline.validate_launch_script(args.component)
        pipeline.check_component_running(args.component)
        
        # Start if requested
        if args.start and pipeline.check_component_running(args.component) is not True:
            pipeline.start_component(args.component)
    else:
        # Validate all components
        pipeline.validate_all_components()
        
        # Start components if requested
        if args.start:
            print("\n=== Starting missing components ===")
            started = pipeline.start_required_components()
            if started:
                print(f"\nStarted {len(started)} components: {', '.join(started)}")
            else:
                print("\nNo components needed to be started")
    
    # Generate report if requested
    if args.report:
        report = pipeline.generate_report()
        report_path = os.path.join(config_manager.get_base_path(), "validation_report.md")
        
        with open(report_path, "w") as f:
            f.write(report)
        
        print(f"\nValidation report written to: {report_path}")

if __name__ == "__main__":
    main()