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

def start_backend():
    """Start the FastAPI backend server"""
    print(f"Starting backend server at {BACKEND_URL}...")
    
    # Get absolute path to app.py
    backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
    app_path = os.path.join(backend_dir, "app.py")
    
    # Change to backend directory
    os.chdir(backend_dir)
    
    # Use the same Python executable that's running this script
    python_executable = sys.executable
    
    # Start the backend server
    if platform.system() == "Windows":
        # On Windows, we need to use a different approach
        return subprocess.Popen(
            [python_executable, app_path],
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
        )
    else:
        # On Unix-like systems
        return subprocess.Popen(
            [python_executable, app_path],
            preexec_fn=os.setsid
        )

def open_frontend():
    """Open the frontend in the default web browser"""
    frontend_url = f"file://{os.path.abspath(FRONTEND_PATH)}"
    print(f"Opening frontend at {frontend_url}...")
    webbrowser.open(frontend_url)

def main():
    """Main function to run the application"""
    print("=" * 80)
    print("Stock Trading Performance Analyzer")
    print("=" * 80)
    
    # Check if frontend exists
    if not os.path.exists(FRONTEND_PATH):
        print(f"Error: Frontend not found at {FRONTEND_PATH}")
        print("Make sure you are running this script from the project root directory.")
        sys.exit(1)
    
    # Start backend server directly without dependency checks
    try:
        backend_process = start_backend()
        print("Backend server started successfully.")
    except Exception as e:
        print(f"Error starting backend server: {str(e)}")
        sys.exit(1)
    
    try:
        # Wait for the server to start
        print("Waiting for backend server to start...")
        time.sleep(2)
        
        # Open frontend
        open_frontend()
        
        print("\nStock Trading Performance Analyzer is running!")
        print("=" * 80)
        print(f"Backend: {BACKEND_URL}")
        print(f"Frontend: file://{os.path.abspath(FRONTEND_PATH)}")
        print("\nAPI Documentation: http://localhost:8003/docs")
        print("\nPress Ctrl+C to stop the application.")
        
        # Keep the script running
        while True:
            # Check if backend process is still running
            if backend_process.poll() is not None:
                print("\nBackend server stopped unexpectedly. Exiting...")
                break
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nStopping the application...")
    finally:
        # Stop the backend server
        if backend_process.poll() is None:  # Only terminate if still running
            try:
                if platform.system() == "Windows":
                    backend_process.send_signal(signal.CTRL_BREAK_EVENT)
                else:
                    os.killpg(os.getpgid(backend_process.pid), signal.SIGTERM)
                
                # Wait for process to terminate with timeout
                for _ in range(5):  # Wait up to 5 seconds
                    if backend_process.poll() is not None:
                        break
                    time.sleep(1)
                
                # Force kill if still running
                if backend_process.poll() is None:
                    print("Backend server not responding. Forcing termination...")
                    if platform.system() == "Windows":
                        subprocess.call(['taskkill', '/F', '/T', '/PID', str(backend_process.pid)])
                    else:
                        os.killpg(os.getpgid(backend_process.pid), signal.SIGKILL)
            except Exception as e:
                print(f"Error stopping backend server: {str(e)}")
        
        print("Application stopped.")

if __name__ == "__main__":
    main()
