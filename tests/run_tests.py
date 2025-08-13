#!/usr/bin/env python3
"""
Test runner script for the RBAC Project.

This script provides an easy way to run tests with different configurations.
"""

import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime

def run_tests(test_type="all", verbose=False, html_report=False, coverage=False):
    """Run tests with specified configuration."""
    
    # Change to project root directory
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Base pytest command
    cmd = ["python", "-m", "pytest"]
    
    # Add verbosity if requested
    if verbose:
        cmd.append("-v")
    
    # Add test type filters
    if test_type == "unit":
        cmd.extend(["-m", "unit"])
    elif test_type == "integration":
        cmd.extend(["-m", "integration"])
    elif test_type == "fast":
        cmd.extend(["-m", "not slow"])
    
    # Add HTML report if requested
    if html_report:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"test_report_{timestamp}.html"
        cmd.extend(["--html", report_file, "--self-contained-html"])
        print(f"📊 HTML report will be generated: {report_file}")
    
    # Add coverage if requested
    if coverage:
        cmd.extend(["--cov=app", "--cov-report=html", "--cov-report=term"])
        print("📈 Coverage report will be generated in htmlcov/ directory")
    
    # Add test discovery
    cmd.append("tests/")
    
    print(f"Running tests with command: {' '.join(cmd)}")
    print(f"Project root: {project_root}")
    print("-" * 50)
    
    try:
        result = subprocess.run(cmd, check=True)
        print("\n✅ All tests passed!")
        
        # Show report locations if generated
        if html_report:
            print(f"📊 HTML report: {report_file}")
        if coverage:
            print("📈 Coverage report: htmlcov/index.html")
            
        return 0
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tests failed with exit code: {e.returncode}")
        
        # Show report locations even if tests failed
        if html_report:
            print(f"📊 HTML report (may contain failure details): {report_file}")
        if coverage:
            print("📈 Coverage report: htmlcov/index.html")
            
        return e.returncode
    except FileNotFoundError:
        print("❌ Error: pytest not found. Please install pytest first:")
        print("   pip install pytest pytest-playwright pytest-html pytest-cov")
        return 1

def install_dependencies():
    """Install required testing dependencies."""
    print("🔧 Installing required testing dependencies...")
    
    dependencies = [
        "pytest",
        "pytest-playwright", 
        "pytest-html",
        "pytest-cov",
        "fastapi",
        "httpx"
    ]
    
    try:
        for dep in dependencies:
            print(f"Installing {dep}...")
            subprocess.run([sys.executable, "-m", "pip", "install", dep], check=True)
        print("✅ All dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run RBAC Project tests")
    parser.add_argument(
        "--type", 
        choices=["all", "unit", "integration", "fast"],
        default="all",
        help="Type of tests to run"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--html",
        action="store_true",
        help="Generate HTML report"
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Generate coverage report"
    )
    parser.add_argument(
        "--install-deps",
        action="store_true",
        help="Install required testing dependencies"
    )
    
    args = parser.parse_args()
    
    print("🚀 RBAC Project Test Runner")
    print("=" * 50)
    
    # Install dependencies if requested
    if args.install_deps:
        if not install_dependencies():
            sys.exit(1)
        print()
    
    exit_code = run_tests(args.type, args.verbose, args.html, args.coverage)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
