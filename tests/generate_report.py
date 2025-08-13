#!/usr/bin/env python3
"""
HTML Test Report Generator for RBAC Project.

This script generates comprehensive HTML test reports with custom styling
and additional project information.
"""

import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime
import json

def generate_html_report(test_type="all", include_coverage=True, custom_style=True):
    """Generate a comprehensive HTML test report."""
    
    # Change to project root directory
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Generate timestamp for unique report names
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Base pytest command
    cmd = ["python", "-m", "pytest"]
    
    # Add test type filters
    if test_type == "unit":
        cmd.extend(["-m", "unit"])
        report_name = f"unit_test_report_{timestamp}.html"
    elif test_type == "integration":
        cmd.extend(["-m", "integration"])
        report_name = f"integration_test_report_{timestamp}.html"
    elif test_type == "fast":
        cmd.extend(["-m", "not slow"])
        report_name = f"fast_test_report_{timestamp}.html"
    else:
        report_name = f"full_test_report_{timestamp}.html"
    
    # Add HTML report options
    cmd.extend([
        "--html", report_name,
        "--self-contained-html",
        "--metadata", "Project", "RBAC Agriculture Project",
        "--metadata", "Version", "1.0.0",
        "--metadata", "Generated", datetime.now().isoformat()
    ])
    
    # Add coverage if requested
    if include_coverage:
        cmd.extend([
            "--cov=app",
            "--cov-report=html",
            "--cov-report=term-missing"
        ])
        coverage_dir = "htmlcov"
    
    # Add test discovery
    cmd.append("tests/")
    
    print(f"🔍 Running tests for: {test_type}")
    print(f"📊 Generating report: {report_name}")
    print(f"📈 Coverage included: {include_coverage}")
    print("-" * 50)
    
    try:
        # Run tests and generate report
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        print("✅ Tests completed successfully!")
        print(f"📊 HTML report generated: {report_name}")
        
        if include_coverage:
            print(f"📈 Coverage report: {coverage_dir}/index.html")
        
        # Add custom styling if requested
        if custom_style:
            enhance_html_report(report_name, project_root)
        
        return report_name, True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Tests failed with exit code: {e.returncode}")
        print(f"📊 HTML report (with failures): {report_name}")
        
        if include_coverage:
            print(f"📈 Coverage report: {coverage_dir}/index.html")
        
        # Add custom styling even for failed tests
        if custom_style:
            enhance_html_report(report_name, project_root)
        
        return report_name, False

def enhance_html_report(report_file, project_root):
    """Enhance the HTML report with custom styling and project information."""
    
    try:
        # Read the generated HTML report
        with open(report_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Add custom CSS for better styling
        custom_css = """
        <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .header { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); 
                  color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .project-info { background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
        .test-summary { background: #e3f2fd; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
        .success { color: #2e7d32; font-weight: bold; }
        .failure { color: #c62828; font-weight: bold; }
        .warning { color: #f57c00; font-weight: bold; }
        table { border-collapse: collapse; width: 100%; margin: 20px 0; }
        th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        th { background-color: #f2f2f2; font-weight: bold; }
        tr:nth-child(even) { background-color: #f9f9f9; }
        tr:hover { background-color: #f5f5f5; }
        .nav { background: #f8f9fa; padding: 10px; border-radius: 5px; margin-bottom: 20px; }
        .nav a { margin-right: 15px; text-decoration: none; color: #007bff; }
        .nav a:hover { text-decoration: underline; }
        </style>
        """
        
        # Add project information header
        project_header = f"""
        <div class="header">
            <h1>🌾 RBAC Agriculture Project - Test Report</h1>
            <p>Comprehensive testing results for the Role-Based Access Control system</p>
        </div>
        
        <div class="project-info">
            <h3>📋 Project Information</h3>
            <ul>
                <li><strong>Project:</strong> RBAC Agriculture Project</li>
                <li><strong>Description:</strong> Role-Based Access Control System with RAG and SQL Querying</li>
                <li><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</li>
                <li><strong>Report Type:</strong> {report_file.split('_')[0].title()} Tests</li>
            </ul>
        </div>
        
        <div class="nav">
            <a href="#summary">Test Summary</a>
            <a href="#details">Test Details</a>
            <a href="#coverage">Coverage Report</a>
        </div>
        """
        
        # Insert custom content after the opening body tag
        if '<body>' in html_content:
            html_content = html_content.replace('<body>', f'<body>{custom_css}{project_header}')
        
        # Write enhanced HTML report
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print("🎨 HTML report enhanced with custom styling!")
        
    except Exception as e:
        print(f"⚠️ Warning: Could not enhance HTML report: {e}")

def generate_summary_report():
    """Generate a summary report of all test types."""
    
    print("📊 Generating comprehensive test summary...")
    
    # Generate reports for different test types
    reports = {}
    
    for test_type in ["unit", "integration", "all"]:
        print(f"\n🔍 Running {test_type} tests...")
        report_file, success = generate_html_report(test_type, include_coverage=True, custom_style=True)
        reports[test_type] = {"file": report_file, "success": success}
    
    # Create summary
    summary_file = f"test_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    
    summary_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>RBAC Project - Test Summary Report</title>
        <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; }}
        .header {{ background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); 
                  color: white; padding: 30px; border-radius: 12px; text-align: center; }}
        .summary {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .report-link {{ background: #e3f2fd; padding: 15px; border-radius: 8px; margin: 10px 0; }}
        .success {{ color: #2e7d32; }}
        .failure {{ color: #c62828; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🌾 RBAC Agriculture Project</h1>
            <h2>Comprehensive Test Summary Report</h2>
            <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="summary">
            <h3>📋 Test Summary</h3>
            <p>This summary provides links to detailed reports for different test categories.</p>
        </div>
        
        <div class="report-link">
            <h3>🧪 Unit Tests</h3>
            <p><strong>Status:</strong> <span class="{'success' if reports['unit']['success'] else 'failure'}">
                {'✅ PASSED' if reports['unit']['success'] else '❌ FAILED'}</span></p>
            <p><strong>Report:</strong> <a href="{reports['unit']['file']}">{reports['unit']['file']}</a></p>
        </div>
        
        <div class="report-link">
            <h3>🔗 Integration Tests</h3>
            <p><strong>Status:</strong> <span class="{'success' if reports['integration']['success'] else 'failure'}">
                {'✅ PASSED' if reports['integration']['success'] else '❌ FAILED'}</span></p>
            <p><strong>Report:</strong> <a href="{reports['integration']['file']}">{reports['integration']['file']}</a></p>
        </div>
        
        <div class="report-link">
            <h3>🚀 Full Test Suite</h3>
            <p><strong>Status:</strong> <span class="{'success' if reports['all']['success'] else 'failure'}">
                {'✅ PASSED' if reports['all']['success'] else '❌ FAILED'}</span></p>
            <p><strong>Report:</strong> <a href="{reports['all']['file']}">{reports['all']['file']}</a></p>
        </div>
        
        <div class="summary">
            <h3>📈 Coverage Reports</h3>
            <p>Detailed coverage information is available in the htmlcov/ directory for each test run.</p>
        </div>
    </body>
    </html>
    """
    
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(summary_html)
    
    print(f"📊 Summary report generated: {summary_file}")
    return summary_file

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate HTML test reports for RBAC Project")
    parser.add_argument(
        "--type",
        choices=["unit", "integration", "all", "fast", "summary"],
        default="all",
        help="Type of tests to run and report on"
    )
    parser.add_argument(
        "--no-coverage",
        action="store_true",
        help="Skip coverage report generation"
    )
    parser.add_argument(
        "--no-style",
        action="store_true",
        help="Skip custom styling enhancement"
    )
    
    args = parser.parse_args()
    
    print("🚀 RBAC Project HTML Report Generator")
    print("=" * 50)
    
    if args.type == "summary":
        # Generate comprehensive summary
        summary_file = generate_summary_report()
        print(f"\n🎉 Summary report ready: {summary_file}")
    else:
        # Generate specific test report
        report_file, success = generate_html_report(
            args.type,
            include_coverage=not args.no_coverage,
            custom_style=not args.no_style
        )
        
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"\n🎉 {args.type.title()} test report ready: {report_file}")
        print(f"📊 Test Status: {status}")

if __name__ == "__main__":
    main()
