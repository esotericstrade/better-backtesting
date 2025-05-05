#!/usr/bin/env python3
"""
Stock Trading Performance Analyzer - Startup Script
This script runs the backend server and opens the frontend in a web browser.
"""

import os
import sys
import webbrowser
import time
import subprocess
import signal
import platform

# Configuration
BACKEND_PORT = 8003
BACKEND_URL = f"http://localhost:{BACKEND_PORT}"
FRONTEND_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend", "index.html")

def check_dependencies():
    """Check if all required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import pandas
        import numpy
        import plotly
        return True
    except ImportError as e:
        print(f"Error: Missing dependency - {str(e)}")
        print("Please install all required dependencies:")
        print("pip install -r backend/requirements.txt")
        return False

def start_backend():
    """Start the FastAPI backend server"""
    print(f"Starting backend server at {BACKEND_URL}...")
    
    # Change to backend directory
    backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
    os.chdir(backend_dir)
    
    # Start the backend server
    if platform.system() == "Windows":
        # On Windows, we need to use a different approach
        return subprocess.Popen(
            [sys.executable, "app.py"],
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
        )
    else:
        # On Unix-like systems
        return subprocess.Popen(
            [sys.executable, "app.py"],
            preexec_fn=os.setsid
        )

def open_frontend():
    """Open the frontend in the default web browser"""
    frontend_url = f"file://{os.path.abspath(FRONTEND_PATH)}"
    print(f"Opening frontend at {frontend_url}...")
    webbrowser.open(frontend_url)

def main():
    """Main function to run the application"""
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Start backend server
    backend_process = start_backend()
    
    try:
        # Wait for the server to start
        print("Waiting for backend server to start...")
        time.sleep(2)
        
        # Open frontend
        open_frontend()
        
        print("\nStock Trading Performance Analyzer is running!")
        print("Backend: " + BACKEND_URL)
        print("Frontend: file://" + os.path.abspath(FRONTEND_PATH))
        print("\nPress Ctrl+C to stop the application.")
        
        # Keep the script running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nStopping the application...")
    finally:
        # Stop the backend server
        if platform.system() == "Windows":
            backend_process.send_signal(signal.CTRL_BREAK_EVENT)
        else:
            os.killpg(os.getpgid(backend_process.pid), signal.SIGTERM)
        
        backend_process.wait()
        print("Application stopped.")

if __name__ == "__main__":
    main()