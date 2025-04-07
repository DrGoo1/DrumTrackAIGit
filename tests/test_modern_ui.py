#!/usr/bin/env python3
"""
Test script for the Modern UI component.

This script tests the basic functionality of the Modern UI component
to ensure it is accessible and responsive.
"""

import os
import sys
import time
import json
import requests
import argparse

# Add config directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "config"))

from config_manager import ConfigManager

class ModernUITester:
    """Tester for the Modern UI component."""
    
    def __init__(self, base_url=None):
        """
        Initialize the tester.
        
        Args:
            base_url: Base URL of the Modern UI. If None, uses the config.
        """
        self.config_manager = ConfigManager()
        
        if base_url:
            self.base_url = base_url
        else:
            component = self.config_manager.get_component_config("modern_ui")
            self.base_url = f"http://localhost:{component['port']}"
        
        self.test_results = {}
    
    def test_ui_accessibility(self):
        """
        Test that the UI is accessible.
        
        Returns:
            True if the test passes, False otherwise
        """
        print("Testing UI accessibility...")
        
        try:
            response = requests.get(self.base_url, timeout=5)
            
            if response.status_code == 200:
                print(f"✓ UI is accessible at {self.base_url}")
                self.test_results["ui_accessibility"] = True
                return True
            else:
                print(f"✗ UI returned status code {response.status_code}")
                self.test_results["ui_accessibility"] = False
                return False
        except requests.exceptions.RequestException as e:
            print(f"✗ Error connecting to UI: {str(e)}")
            self.test_results["ui_accessibility"] = False
            return False
    
    def test_api_connection(self):
        """
        Test the connection to the API from the UI.
        This is a basic check to ensure the UI can reach the API.
        
        Returns:
            True if the test passes, False otherwise
        """
        print("Testing API connection from UI...")
        
        try:
            # This is a basic check - it just verifies that the API endpoint
            # would be accessible from the UI based on how it's typically configured
            api_component = self.config_manager.get_component_config("fastapi_backend")
            api_url = f"http://localhost:{api_component['port']}/health"
            
            response = requests.get(api_url, timeout=5)
            
            if response.status_code == 200:
                print(f"✓ API is accessible at {api_url}")
                self.test_results["api_connection"] = True
                return True
            else:
                print(f"✗ API returned status code {response.status_code}")
                self.test_results["api_connection"] = False
                return False
        except requests.exceptions.RequestException as e:
            print(f"✗ Error connecting to API: {str(e)}")
            self.test_results["api_connection"] = False
            return False
    
    def run_all_tests(self):
        """
        Run all tests.
        
        Returns:
            True if all tests pass, False otherwise
        """
        print(f"Testing Modern UI at {self.base_url}...")
        
        tests = [
            self.test_ui_accessibility,
            self.test_api_connection
            # Add more tests as needed
        ]
        
        results = []
        for test in tests:
            results.append(test())
        
        # Overall result
        overall = all(results)
        self.test_results["overall"] = overall
        
        if overall:
            print("\n✅ All tests passed!")
        else:
            print("\n❌ Some tests failed.")
        
        return overall
    
    def generate_report(self):
        """
        Generate a test report.
        
        Returns:
            Report as a string
        """
        report = "# Modern UI Test Results\n\n"
        
        # Overall result
        if self.test_results.get("overall", False):
            report += "## ✅ Overall Status: PASSED\n\n"
        else:
            report += "## ❌ Overall Status: FAILED\n\n"
        
        # Individual tests
        report += "## Test Details\n\n"
        report += "| Test | Result |\n"
        report += "|------|--------|\n"
        
        for test, result in self.test_results.items():
            if test == "overall":
                continue
            
            status = "✅ PASSED" if result else "❌ FAILED"
            report += f"| {test} | {status} |\n"
        
        return report

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Test the Modern UI component")
    parser.add_argument("--url", help="Base URL of the Modern UI")
    parser.add_argument("--report", action="store_true", help="Generate a test report")
    
    args = parser.parse_args()
    
    # Create tester
    tester = ModernUITester(base_url=args.url)
    
    # Run tests
    tester.run_all_tests()
    
    # Generate report if requested
    if args.report:
        report = tester.generate_report()
        
        # Save report
        config_manager = ConfigManager()
        report_path = os.path.join(config_manager.get_base_path(), "modern_ui_test_report.md")
        
        with open(report_path, "w") as f:
            f.write(report)
        
        print(f"\nTest report written to: {report_path}")

if __name__ == "__main__":
    main()