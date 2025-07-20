#!/usr/bin/env python3
"""
HAL Transport Management System - Quick Start Script
Run this script to quickly start the entire system and verify it's working.
"""

import subprocess
import sys
import time
import requests
import os
from pathlib import Path

def print_header(title):
    print(f"\n{'='*60}")
    print(f"🚀 {title}")
    print(f"{'='*60}")

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def print_info(message):
    print(f"ℹ️  {message}")

def check_backend_running():
    """Check if backend is running"""
    try:
        response = requests.get("http://localhost:8000/docs", timeout=5)
        return response.status_code == 200
    except:
        return False

def check_frontend_running():
    """Check if frontend is running"""
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        return response.status_code == 200
    except:
        return False

def start_backend():
    """Start the backend server"""
    print_header("STARTING BACKEND SERVER")
    
    backend_path = Path("backend")
    if not backend_path.exists():
        print_error("Backend directory not found!")
        return False
    
    # Check if already running
    if check_backend_running():
        print_success("Backend server is already running")
        return True
    
    print_info("Starting backend server...")
    print_info("Backend will be available at: http://localhost:8000")
    print_info("API documentation at: http://localhost:8000/docs")
    
    # Start backend in a new process
    try:
        if os.name == 'nt':  # Windows
            subprocess.Popen([
                "cmd", "/c", "cd backend && venv\\Scripts\\activate && python main.py"
            ], shell=True)
        else:  # Linux/Mac
            subprocess.Popen([
                "bash", "-c", "cd backend && source venv/bin/activate && python main.py"
            ], shell=True)
        
        # Wait for backend to start
        print_info("Waiting for backend to start...")
        for i in range(30):  # Wait up to 30 seconds
            if check_backend_running():
                print_success("Backend server started successfully!")
                return True
            time.sleep(1)
            print(".", end="", flush=True)
        
        print_error("Backend server failed to start within 30 seconds")
        return False
        
    except Exception as e:
        print_error(f"Failed to start backend: {e}")
        return False

def start_frontend():
    """Start the frontend server"""
    print_header("STARTING FRONTEND SERVER")
    
    frontend_path = Path("frontend")
    if not frontend_path.exists():
        print_error("Frontend directory not found!")
        return False
    
    # Check if already running
    if check_frontend_running():
        print_success("Frontend server is already running")
        return True
    
    print_info("Starting frontend server...")
    print_info("Frontend will be available at: http://localhost:3000")
    
    # Start frontend in a new process
    try:
        if os.name == 'nt':  # Windows
            subprocess.Popen([
                "cmd", "/c", "cd frontend && npm start"
            ], shell=True)
        else:  # Linux/Mac
            subprocess.Popen([
                "bash", "-c", "cd frontend && npm start"
            ], shell=True)
        
        # Wait for frontend to start
        print_info("Waiting for frontend to start...")
        for i in range(60):  # Wait up to 60 seconds
            if check_frontend_running():
                print_success("Frontend server started successfully!")
                return True
            time.sleep(1)
            print(".", end="", flush=True)
        
        print_error("Frontend server failed to start within 60 seconds")
        return False
        
    except Exception as e:
        print_error(f"Failed to start frontend: {e}")
        return False

def run_verification():
    """Run system verification"""
    print_header("RUNNING SYSTEM VERIFICATION")
    
    try:
        result = subprocess.run([
            sys.executable, "backend/verify_system_integrity.py"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print_success("System verification passed!")
            return True
        else:
            print_error("System verification failed!")
            print(result.stdout)
            print(result.stderr)
            return False
            
    except Exception as e:
        print_error(f"Verification failed: {e}")
        return False

def main():
    """Main quick start function"""
    print_header("HAL TRANSPORT MANAGEMENT SYSTEM - QUICK START")
    
    # Start backend
    if not start_backend():
        print_error("Failed to start backend server")
        return False
    
    # Start frontend
    if not start_frontend():
        print_error("Failed to start frontend server")
        return False
    
    # Run verification
    if not run_verification():
        print_error("System verification failed")
        return False
    
    # Success message
    print_header("SYSTEM READY!")
    print_success("HAL Transport Management System is now running!")
    print_info("🌐 Frontend: http://localhost:3000")
    print_info("🔧 Backend API: http://localhost:8000")
    print_info("📚 API Docs: http://localhost:8000/docs")
    print_info("")
    print_info("👥 Demo Credentials:")
    print_info("   🔧 Admin: HAL001 / admin123")
    print_info("   🚗 Transport: HAL002 / transport123")
    print_info("   👤 Employee: HAL003 / employee123")
    print_info("")
    print_info("Press Ctrl+C to stop the servers")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            # Keep the script running
            while True:
                time.sleep(1)
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        print_info("\nShutting down...")
        sys.exit(0)
