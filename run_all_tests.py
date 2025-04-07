#!/usr/bin/env python3
"""
Master Testing Script for DrumTracKAI

This script runs all test scripts in sequence and generates
a comprehensive test report.
"""

import os
import sys
import time
import argparse
import subprocess
from datetime import datetime
from pathlib import Path

# Add config directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), "config"))

from config_manager import ConfigManager

def run_command(command, cwd=None):
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
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        text=True
    )
    
    stdout, stderr = process.communicate()
    
    return process.returncode, stdout, stderr

def run_all_tests(validate_only=False, start_components=False):
    """
    Run all tests.
    
    Args:
        validate_only: Only run validation, not component tests
        start_components: Start missing components
        
    Returns:
        True if all tests pass, False otherwise
    """
    # Get config manager
    config_manager = ConfigManager()
    base_path = config_manager.get_base_path()
    
    # Dictionary to store test results
    test_results = {}
    
    # 1. Run validation
    print("\n=== Running Validation Pipeline ===\n")
    
    validation_cmd = [sys.executable, "validation_pipeline.py"]
    if start_components:
        validation_cmd.append("--start")
    validation_cmd.append("--report")
    
    returncode, stdout, stderr = run_command(
        " ".join(validation_cmd),
        cwd=base_path
    )
    
    validation_success = returncode == 0
    test_results["validation"] = validation_success
    
    print(stdout)
    if stderr:
        print(f"Validation errors:\n{stderr}")
    
    if validate_only:
        # Only running validation
        return validation_success
    
    # 2. Run component tests
    # Only run these if validation passed or if we started components
    if validation_success or start_components:
        # 2.1 FastAPI Backend Test
        print("\n=== Running FastAPI Backend Tests ===\n")
        
        api_test_cmd = [
            sys.executable, 
            "tests/test_fastapi_backend.py",
            "--report"
        ]
        
        returncode, stdout, stderr = run_command(
            " ".join(api_test_cmd),
            cwd=base_path
        )
        
        api_success = returncode == 0
        test_results["fastapi_backend"] = api_success
        
        print(stdout)
        if stderr:
            print(f"FastAPI test errors:\n{stderr}")
        
        # 2.2 Modern UI Test
        print("\n=== Running Modern UI Tests ===\n")
        
        ui_test_cmd = [
            sys.executable, 
            "tests/test_modern_ui.py",
            "--report"
        ]
        
        returncode, stdout, stderr = run_command(
            " ".join(ui_test_cmd),
            cwd=base_path
        )
        
        ui_success = returncode == 0
        test_results["modern_ui"] = ui_success
        
        print(stdout)
        if stderr:
            print(f"UI test errors:\n{stderr}")
        
        # 2.3 Integration Test
        print("\n=== Running Integration Tests ===\n")
        
        integration_test_cmd = [
            sys.executable, 
            "tests/test_system_integration.py",
            "--report"
        ]
        
        returncode, stdout, stderr = run_command(
            " ".join(integration_test_cmd),
            cwd=base_path
        )
        
        integration_success = returncode == 0
        test_results["integration"] = integration_success
        
        print(stdout)
        if stderr:
            print(f"Integration test errors:\n{stderr}")
    else:
        print("\n❌ Validation failed. Skipping component tests.")
        test_results["fastapi_backend"] = False
        test_results["modern_ui"] = False
        test_results["integration"] = False
    
    # 3. Generate comprehensive report
    generate_comprehensive_report(test_results, base_path)
    
    # Overall success
    overall_success = all(test_results.values())
    
    if overall_success:
        print("\n✅ All tests passed successfully!")
    else:
        print("\n❌ Some tests failed. Check the comprehensive report for details.")
    
    return overall_success

def generate_comprehensive_report(test_results, base_path):
    """
    Generate a comprehensive test report.
    
    Args:
        test_results: Dictionary of test results
        base_path: Base path of the project
    """
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    report_filename = f"test_report_{timestamp}.md"
    report_path = os.path.join(base_path, report_filename)
    
    print(f"Generating comprehensive test report: {report_path}")
    
    # Read individual reports if they exist
    report_paths = {
        "validation": os.path.join(base_path, "validation_report.md"),
        "fastapi_backend": os.path.join(base_path, "fastapi_test_report.md"),
        "modern_ui": os.path.join(base_path, "modern_ui_test_report.md"),
        "integration": os.path.join(base_path, "integration_test_report.md")
    }
    
    report_contents = {}
    for name, path in report_paths.items():
        if os.path.exists(path):
            with open(path, "r") as f:
                report_contents[name] = f.read()
    
    # Generate comprehensive report
    with open(report_path, "w") as f:
        f.write("# DrumTracKAI Comprehensive Test Report\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Overall summary
        f.write("## Overall Test Summary\n\n")
        f.write("| Test | Result |\n")
        f.write("|------|--------|\n")
        
        for name, result in test_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            f.write(f"| {name.replace('_', ' ').title()} | {status} |\n")
        
        # Overall result
        overall_success = all(test_results.values())
        overall_status = "✅ PASSED" if overall_success else "❌ FAILED"
        f.write(f"\n**Overall Status: {overall_status}**\n\n")
        
        # Include individual reports
        for name, content in report_contents.items():
            f.write(f"## {name.replace('_', ' ').title()} Test Report\n\n")
            
            # Remove the first line (title) to avoid duplication
            content_lines = content.split("\n")
            if content_lines:
                content = "\n".join(content_lines[1:])
            
            f.write(content)
            f.write("\n\n")
        
        # Recommendations
        f.write("## Recommendations\n\n")
        
        if not test_results.get("validation", True):
            f.write("- ⚠️ **Validation Failed**: Check component configurations and ensure all components are present.\n")
        
        if not test_results.get("fastapi_backend", True):
            f.write("- ⚠️ **FastAPI Backend Tests Failed**: Check the API server is running correctly.\n")
        
        if not test_results.get("modern_ui", True):
            f.write("- ⚠️ **Modern UI Tests Failed**: Verify the UI is accessible and properly configured.\n")
        
        if not test_results.get("integration", True):
            f.write("- ⚠️ **Integration Tests Failed**: Ensure all components are communicating correctly.\n")
        
        if overall_success:
            f.write("- ✅ All tests passed! The system appears to be functioning correctly.\n")
    
    print(f"Comprehensive test report generated: {report_path}")
    
    # Create a symlink to the latest report
    latest_report_path = os.path.join(base_path, "latest_test_report.md")
    try:
        if os.path.exists(latest_report_path):
            os.remove(latest_report_path)
        
        # On Windows, symlinks may require admin privileges, so handle gracefully
        try:
            os.symlink(report_path, latest_report_path)
            print(f"Latest report symlink created: {latest_report_path}")
        except (OSError, NotImplementedError):
            # Fall back to just copying the file
            import shutil
            shutil.copy2(report_path, latest_report_path)
            print(f"Latest report copied to: {latest_report_path}")
    except Exception as e:
        print(f"Could not create latest report link: {str(e)}")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run all DrumTracKAI tests")
    parser.add_argument("--validate-only", action="store_true", help="Only run validation, not component tests")
    parser.add_argument("--start", action="store_true", help="Start missing components")
    
    args = parser.parse_args()
    
    # Run all tests
    run_all_tests(
        validate_only=args.validate_only,
        start_components=args.start
    )

if __name__ == "__main__":
    main()