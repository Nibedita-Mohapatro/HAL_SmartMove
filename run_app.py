#!/usr/bin/env python3
"""
HAL SmartMove - Simple App Runner

This script provides the simplest way to run the HAL SmartMove application.
Just run this script and the app will start automatically.

Usage:
    python run_app.py
"""

import os
import sys
import subprocess
import time
import platform
from pathlib import Path

def print_banner():
    """Print app runner banner"""
    print("\n" + "="*50)
    print("🚀 HAL SmartMove - App Runner")
    print("   Starting your transport management system...")
    print("="*50)

def start_services():
    """Start both backend and frontend services"""
    print("🔧 Starting backend service...")
    
    # Start backend
    backend_dir = Path("backend")
    is_windows = platform.system() == "Windows"
    
    if is_windows:
        backend_cmd = "cd backend && venv\\Scripts\\activate && python main.py"
        backend_process = subprocess.Popen(backend_cmd, shell=True)
    else:
        backend_cmd = "cd backend && source venv/bin/activate && python main.py"
        backend_process = subprocess.Popen(backend_cmd, shell=True)
    
    print("✅ Backend starting...")
    
    # Wait a moment for backend to initialize
    time.sleep(3)
    
    print("🎨 Starting frontend service...")
    
    # Start frontend
    frontend_dir = Path("frontend")
    env = os.environ.copy()
    env["BROWSER"] = "none"  # Prevent auto-opening browser
    
    if is_windows:
        frontend_cmd = "cd frontend && npm start"
        frontend_process = subprocess.Popen(frontend_cmd, shell=True, env=env)
    else:
        frontend_cmd = "cd frontend && npm start"
        frontend_process = subprocess.Popen(frontend_cmd, shell=True, env=env)
    
    print("✅ Frontend starting...")
    
    return backend_process, frontend_process

def wait_for_ready():
    """Wait for services to be ready"""
    print("\n⏳ Waiting for services to be ready...")
    
    # Wait for services to start
    for i in range(45):
        try:
            import requests
            backend_ready = False
            frontend_ready = False
            
            # Check backend
            try:
                response = requests.get("http://localhost:8000/health", timeout=1)
                if response.status_code == 200:
                    backend_ready = True
            except:
                pass
            
            # Check frontend
            try:
                response = requests.get("http://localhost:3000", timeout=1)
                if response.status_code == 200:
                    frontend_ready = True
            except:
                pass
            
            if backend_ready and frontend_ready:
                print("\n✅ Both services are ready!")
                return True
                
        except ImportError:
            # requests not available, just wait
            pass
        
        time.sleep(1)
        print(".", end="", flush=True)
    
    print("\n⚠️ Services may still be starting...")
    return True

def print_success():
    """Print success message"""
    print("\n" + "="*50)
    print("🎉 HAL SmartMove is Running!")
    print("="*50)
    print()
    print("🌐 Open your browser and go to:")
    print("   http://localhost:3000")
    print()
    print("🔑 Login with these credentials:")
    print("   Admin:     HAL001 / admin123")
    print("   Employee:  HAL003 / employee123")
    print("   Transport: HAL002 / transport123")
    print()
    print("💡 Press Ctrl+C to stop the application")
    print("="*50)

def main():
    """Main execution"""
    try:
        print_banner()
        
        # Start services
        backend_process, frontend_process = start_services()
        
        # Wait for ready
        wait_for_ready()
        
        # Print success
        print_success()
        
        # Keep running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping services...")
            backend_process.terminate()
            frontend_process.terminate()
            print("✅ Application stopped. Goodbye!")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("💡 Make sure you have Python and Node.js installed")
        print("💡 Run 'python start_system.py' for detailed setup")

if __name__ == "__main__":
    main()
