#!/usr/bin/env python3
"""
Test script for the FastAPI backend component.

This script tests the key endpoints of the FastAPI backend to ensure
they are functioning correctly.
"""

import os
import sys
import json
import requests
import argparse

# Add config directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "config"))

from config_manager import ConfigManager

class FastAPIBackendTester:
    """Tester for the FastAPI backend component."""
    
    def __init__(self, base_url=None):
        """
        Initialize the tester.
        
        Args:
            base_url: Base URL of the FastAPI backend. If None, uses the config.
        """
        self.config_manager = ConfigManager()
        
        if base_url:
            self.base_url = base_url
        else:
            component = self.config_manager.get_component_config("fastapi_backend")
            self.base_url = f"http://localhost:{component['port']}"
        
        self.test_results = {}
    
    def test_health_endpoint(self):
        """
        Test the health endpoint.
        
        Returns:
            True if the test passes, False otherwise
        """
        print("Testing health endpoint...")
        
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            
            if response.status_code == 200:
                print(f"✓ Health endpoint returned 200 OK")
                
                # Check version if available
                try:
                    data = response.json()
                    if "version" in data:
                        expected_version = self.config_manager.get_component_config("fastapi_backend")["version"]
                        if data["version"] == expected_version:
                            print(f"✓ Version matches: {data['version']}")
                        else:
                            print(f"✗ Version mismatch. Expected: {expected_version}, Got: {data['version']}")
                            return False
                except ValueError:
                    # Not JSON or other issue
                    print("✗ Health endpoint response is not valid JSON")
                
                self.test_results["health_endpoint"] = True
                return True
            else:
                print(f"✗ Health endpoint returned {response.status_code}")
                self.test_results["health_endpoint"] = False
                return False
        except requests.exceptions.RequestException as e:
            print(f"✗ Error connecting to health endpoint: {str(e)}")
            self.test_results["health_endpoint"] = False
            return False
    
    def test_api_docs(self):
        """
        Test the API documentation endpoint.
        
        Returns:
            True if the test passes, False otherwise
        """
        print("Testing API documentation endpoint...")
        
        try:
            response = requests.get(f"{self.base_url}/docs", timeout=5)
            
            if response.status_code == 200:
                print(f"✓ API docs endpoint returned 200 OK")
                self.test_results["api_docs"] = True
                return True
            else:
                print(f"✗ API docs endpoint returned {response.status_code}")
                self.test_results["api_docs"] = False
                return False
        except requests.exceptions.RequestException as e:
            print(f"✗ Error connecting to API docs endpoint: {str(e)}")
            self.test_results["api_docs"] = False
            return False
    
    def test_extraction_endpoint(self):
        """
        Test the extraction endpoint with a sample request.
        
        Returns:
            True if the test passes, False otherwise
        """
        print("Testing extraction endpoint...")
        
        # Define a simple test payload
        # This should be adapted to your actual API
        payload = {
            "test_mode": True,
            "sample_data": "test"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/extraction", 
                json=payload,
                timeout=10
            )
            
            # Check if the response is successful (200-299)
            if 200 <= response.status_code < 300:
                print(f"✓ Extraction endpoint returned {response.status_code}")
                self.test_results["extraction_endpoint"] = True
                return True
            else:
                print(f"✗ Extraction endpoint returned {response.status_code}")
                self.test_results["extraction_endpoint"] = False
                return False
        except requests.exceptions.RequestException as e:
            print(f"✗ Error connecting to extraction endpoint: {str(e)}")
            self.test_results["extraction_endpoint"] = False
            return False
    
    def run_all_tests(self):
        """
        Run all tests.
        
        Returns:
            True if all tests pass, False otherwise
        """
        print(f"Testing FastAPI backend at {self.base_url}...")
        
        tests = [
            self.test_health_endpoint,
            self.test_api_docs,
            self.test_extraction_endpoint
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
        report = "# FastAPI Backend Test Results\n\n"
        
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
    parser = argparse.ArgumentParser(description="Test the FastAPI backend component")
    parser.add_argument("--url", help="Base URL of the FastAPI backend")
    parser.add_argument("--report", action="store_true", help="Generate a test report")
    
    args = parser.parse_args()
    
    # Create tester
    tester = FastAPIBackendTester(base_url=args.url)
    
    # Run tests
    tester.run_all_tests()
    
    # Generate report if requested
    if args.report:
        report = tester.generate_report()
        
        # Save report
        config_manager = ConfigManager()
        report_path = os.path.join(config_manager.get_base_path(), "fastapi_test_report.md")
        
        with open(report_path, "w") as f:
            f.write(report)
        
        print(f"\nTest report written to: {report_path}")

if __name__ == "__main__":
    main()