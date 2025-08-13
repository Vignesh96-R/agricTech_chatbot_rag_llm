#!/usr/bin/env python3
"""
Agriculture RBAC-Project Startup Script

This script provides an easy way to start the Agriculture RBAC-Project application.
It can run either the FastAPI backend or the Streamlit frontend.
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path

def run_backend():
    """Run the FastAPI backend server."""
    print("🚀 Starting FastAPI Backend Server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📚 API Documentation at: http://localhost:8000/docs")
    print("🔍 Health Check at: http://localhost:8000/health")
    print("\nPress Ctrl+C to stop the server\n")
    
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Backend server stopped.")

def run_frontend():
    """Run the Streamlit frontend."""
    print("🎨 Starting Streamlit Frontend...")
    print("📍 Frontend will be available at: http://localhost:8501")
    print("\nPress Ctrl+C to stop the frontend\n")
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "app/ui.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Frontend stopped.")

def run_both():
    """Run both backend and frontend in separate processes."""
    print("🌾 Starting Agriculture RBAC-Project Application...")
    print("📍 Backend: http://localhost:8000")
    print("📍 Frontend: http://localhost:8501")
    print("📚 API Docs: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop both services\n")
    
    try:
        # Start backend in background
        backend_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ])
        
        # Start frontend
        frontend_process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", 
            "app/ui.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
        
        # Wait for both processes
        backend_process.wait()
        frontend_process.wait()
        
    except KeyboardInterrupt:
        print("\n🛑 Stopping services...")
        backend_process.terminate()
        frontend_process.terminate()
        print("✅ Services stopped.")

def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = [
        "fastapi", "uvicorn", "streamlit", "pandas", 
        "duckdb", "openai", "langchain", "passlib"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n💡 Install them with: pip install -r requirements.txt")
        return False
    
    return True

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="RBAC-Project Application Startup Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_app.py --backend     # Run only the FastAPI backend
  python run_app.py --frontend    # Run only the Streamlit frontend
  python run_app.py --both        # Run both backend and frontend
  python run_app.py               # Run both (default)
        """
    )
    
    parser.add_argument(
        "--backend", 
        action="store_true", 
        help="Run only the FastAPI backend server"
    )
    
    parser.add_argument(
        "--frontend", 
        action="store_true", 
        help="Run only the Streamlit frontend"
    )
    
    parser.add_argument(
        "--both", 
        action="store_true", 
        help="Run both backend and frontend (default)"
    )
    
    parser.add_argument(
        "--check", 
        action="store_true", 
        help="Check dependencies and exit"
    )
    
    args = parser.parse_args()
    
    # Check if we're in the right directory
    if not Path("app").exists():
        print("❌ Error: 'app' directory not found.")
        print("💡 Make sure you're running this script from the project root directory.")
        sys.exit(1)
    
    # Check dependencies if requested
    if args.check:
        if check_dependencies():
            print("✅ All required dependencies are installed.")
        else:
            sys.exit(1)
        return
    
    # Check dependencies before starting
    if not check_dependencies():
        sys.exit(1)
    
    # Determine what to run
    if args.backend:
        run_backend()
    elif args.frontend:
        run_frontend()
    else:
        # Default: run both
        run_both()

if __name__ == "__main__":
    main()
