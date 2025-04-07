#!/usr/bin/env python3
"""
System Integration Test Script for DrumTracKAI

This script tests the integration between components to ensure
the entire system functions correctly.
"""

import os
import sys
import time
import json
import requests
import argparse
import tempfile
import random
import string

# Add config directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "config"))

from config_manager import ConfigManager

class IntegrationTester:
    """Tester for integration between DrumTracKAI components."""
    
    def __init__(self):
        """Initialize the integration tester."""
        self.config_manager = ConfigManager()
        self.test_results = {}
        
        # Get component configurations
        self.api_config = self.config_manager.get_component_config("fastapi_backend")
        self.ui_config = self.config_manager.get_component_config("modern_ui")
        self.training_config = self.config_manager.get_component_config("training_dashboard")
        
        # Define base URLs
        self.api_url = f"http://localhost:{self.api_config['port']}"
        self.ui_url = f"http://localhost:{self.ui_config['port']}"
        self.training_url = f"http://localhost:{self.training_config['port']}"
    
    def test_api_ui_connection(self):
        """
        Test the connection between the API and UI.
        
        Returns:
            True if the test passes, False otherwise
        """
        print("Testing API-UI connection...")
        
        # First, check if both are accessible
        try:
            api_response = requests.get(f"{self.api_url}/health", timeout=5)
            ui_response = requests.get(self.ui_url, timeout=5)
            
            if api_response.status_code != 200:
                print(f"✗ API is not accessible (status code: {api_response.status_code})")
                self.test_results["api_ui_connection"] = False
                return False
            
            if ui_response.status_code != 200:
                print(f"✗ UI is not accessible (status code: {ui_response.status_code})")
                self.test_results["api_ui_connection"] = False
                return False
            
            print("✓ Both API and UI are accessible")
            
            # For a real-world test, you'd perform actions in the UI that trigger API calls,
            # but that requires browser automation. Here, we'll just verify the API endpoints
            # that the UI needs are available.
            
            # Try to access the API endpoints that the UI would typically use
            # This is a simplified example - adjust according to your actual API
            endpoints_to_check = [
                "/api/v1/extraction",
                "/api/v1/drums",
                "/api/v1/status"
            ]
            
            all_endpoints_accessible = True
            for endpoint in endpoints_to_check:
                try:
                    # Just check if the endpoint is accessible (not necessarily success)
                    response = requests.options(f"{self.api_url}{endpoint}", timeout=5)
                    
                    if response.status_code >= 400:  # Client or server error
                        print(f"✗ Endpoint {endpoint} returned status code {response.status_code}")
                        all_endpoints_accessible = False
                    else:
                        print(f"✓ Endpoint {endpoint} is accessible")
                except requests.exceptions.RequestException as e:
                    print(f"✗ Error connecting to endpoint {endpoint}: {str(e)}")
                    all_endpoints_accessible = False
            
            self.test_results["api_ui_connection"] = all_endpoints_accessible
            return all_endpoints_accessible
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Error during API-UI connection test: {str(e)}")
            self.test_results["api_ui_connection"] = False
            return False
    
    def test_extraction_workflow(self):
        """
        Test the full extraction workflow.
        This is a higher-level test that verifies the extraction functionality.
        
        Returns:
            True if the test passes, False otherwise
        """
        print("Testing extraction workflow...")
        
        # For a complete test, you'd upload a real audio file
        # Since that's complex in a script, we'll simulate with a test endpoint
        
        try:
            # Check if a test endpoint exists
            test_endpoint = f"{self.api_url}/api/v1/extraction/test"
            
            payload = {
                "test_mode": True,
                "simulate_extraction": True
            }
            
            response = requests.post(test_endpoint, json=payload, timeout=10)
            
            if response.status_code >= 400:
                print(f"✗ Extraction test endpoint returned status code {response.status_code}")
                self.test_results["extraction_workflow"] = False
                return False
            
            print(f"✓ Extraction test workflow completed successfully")
            self.test_results["extraction_workflow"] = True
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Error during extraction workflow test: {str(e)}")
            self.test_results["extraction_workflow"] = False
            return False
    
    def test_training_dashboard_api_connection(self):
        """
        Test the connection between the training dashboard and API.
        
        Returns:
            True if the test passes, False otherwise
        """
        print("Testing Training Dashboard-API connection...")
        
        try:
            # Check if both are accessible
            api_response = requests.get(f"{self.api_url}/health", timeout=5)
            dashboard_response = requests.get(self.training_url, timeout=5)
            
            if api_response.status_code != 200:
                print(f"✗ API is not accessible (status code: {api_response.status_code})")
                self.test_results["training_dashboard_api_connection"] = False
                return False
            
            if dashboard_response.status_code != 200:
                print(f"✗ Training Dashboard is not accessible (status code: {dashboard_response.status_code})")
                self.test_results["training_dashboard_api_connection"] = False
                return False
            
            print("✓ Both API and Training Dashboard are accessible")
            
            # Check the specific API endpoints that the training dashboard would use
            # This is a simplified example - adjust according to your actual API
            endpoints_to_check = [
                "/api/v1/training/status",
                "/api/v1/models"
            ]
            
            all_endpoints_accessible = True
            for endpoint in endpoints_to_check:
                try:
                    response = requests.options(f"{self.api_url}{endpoint}", timeout=5)
                    
                    if response.status_code >= 400:  # Client or server error
                        print(f"✗ Endpoint {endpoint} returned status code {response.status_code}")
                        all_endpoints_accessible = False
                    else:
                        print(f"✓ Endpoint {endpoint} is accessible")
                except requests.exceptions.RequestException as e:
                    print(f"✗ Error connecting to endpoint {endpoint}: {str(e)}")
                    all_endpoints_accessible = False
            
            self.test_results["training_dashboard_api_connection"] = all_endpoints_accessible
            return all_endpoints_accessible
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Error during Training Dashboard-API connection test: {str(e)}")
            self.test_results["training_dashboard_api_connection"] = False
            return False
    
    def run_all_tests(self):
        """
        Run all integration tests.
        
        Returns:
            True if all tests pass, False otherwise
        """
        print("Running DrumTracKAI integration tests...")
        
        tests = [
            self.test_api_ui_connection,
            self.test_extraction_workflow,
            self.test_training_dashboard_api_connection
            # Add more integration tests as needed
        ]
        
        results = []
        for test in tests:
            results.append(test())
        
        # Overall result
        overall = all(results)
        self.test_results["overall"] = overall
        
        if overall:
            print("\n✅ All integration tests passed!")
        else:
            print("\n❌ Some integration tests failed.")
        
        return overall
    
    def generate_report(self):
        """
        Generate a test report.
        
        Returns:
            Report as a string
        """
        report = "# DrumTracKAI Integration Test Results\n\n"
        
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
    parser = argparse.ArgumentParser(description="Run integration tests for DrumTracKAI")
    parser.add_argument("--report", action="store_true", help="Generate a test report")
    
    args = parser.parse_args()
    
    # Create tester
    tester = IntegrationTester()
    
    # Run tests
    tester.run_all_tests()
    
    # Generate report if requested
    if args.report:
        report = tester.generate_report()
        
        # Save report
        config_manager = ConfigManager()
        report_path = os.path.join(config_manager.get_base_path(), "integration_test_report.md")
        
        with open(report_path, "w") as f:
            f.write(report)
        
        print(f"\nTest report written to: {report_path}")

if __name__ == "__main__":
    main()