#!/usr/bin/env python3
"""
Configuration Manager for DrumTracKAI

This script provides utilities for loading, validating, and accessing
the central configuration for the DrumTracKAI application.
"""

import json
import os
import sys
from pathlib import Path

class ConfigManager:
    """Manager for the application configuration."""
    
    def __init__(self, config_path=None):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Path to the configuration file. If None, uses default path.
        """
        if config_path is None:
            # Determine base path
            script_dir = Path(__file__).resolve().parent
            base_path = script_dir.parent
            config_path = base_path / "config" / "app_config.json"
        
        self.config_path = config_path
        self.config = self._load_config()
        
    def _load_config(self):
        """Load the configuration from file."""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            return config
        except FileNotFoundError:
            print(f"Error: Configuration file not found at {self.config_path}")
            sys.exit(1)
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in configuration file at {self.config_path}")
            sys.exit(1)
    
    def get_component_config(self, component_name):
        """
        Get configuration for a specific component.
        
        Args:
            component_name: Name of the component
            
        Returns:
            Component configuration dictionary or None if not found
        """
        return self.config["components"].get(component_name)
    
    def get_base_path(self):
        """Get the base path of the project."""
        return self.config["project"]["base_path"]
    
    def get_component_path(self, component_name):
        """
        Get the full path to a component.
        
        Args:
            component_name: Name of the component
            
        Returns:
            Full path to the component or None if not found
        """
        component = self.get_component_config(component_name)
        if not component:
            return None
        
        return os.path.join(self.get_base_path(), component["path"])
    
    def get_component_launch_script(self, component_name):
        """
        Get the full path to a component's launch script.
        
        Args:
            component_name: Name of the component
            
        Returns:
            Full path to the launch script or None if not found
        """
        component = self.get_component_config(component_name)
        if not component:
            return None
        
        script = component["launch_script"]
        
        # Check if it's a direct command or a script file
        if script.endswith(".bat") or script.endswith(".sh"):
            return os.path.join(self.get_base_path(), script)
        
        return script
    
    def get_all_components(self):
        """Get a list of all component names."""
        return list(self.config["components"].keys())
    
    def get_component_dependencies(self, component_name):
        """
        Get the dependencies for a component.
        
        Args:
            component_name: Name of the component
            
        Returns:
            List of dependency component names
        """
        component = self.get_component_config(component_name)
        if not component:
            return []
        
        return component.get("dependencies", [])
    
    def get_component_launch_order(self):
        """
        Get the correct order to launch components based on dependencies.
        
        Returns:
            List of component names in correct launch order
        """
        # Simple topological sort
        components = self.get_all_components()
        visited = set()
        result = []
        
        def visit(component):
            if component in visited:
                return
            visited.add(component)
            
            for dep in self.get_component_dependencies(component):
                visit(dep)
            
            result.append(component)
        
        for component in components:
            visit(component)
        
        return result

# Example usage
if __name__ == "__main__":
    config_manager = ConfigManager()
    
    # Print component launch order
    print("Component Launch Order:")
    for component in config_manager.get_component_launch_order():
        print(f"- {component}")
        
    # Print component paths
    print("\nComponent Paths:")
    for component in config_manager.get_all_components():
        path = config_manager.get_component_path(component)
        print(f"- {component}: {path}")