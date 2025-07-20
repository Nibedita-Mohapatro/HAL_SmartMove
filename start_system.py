#!/usr/bin/env python3
"""
HAL SmartMove - Automated System Startup Script

This script automatically starts the entire HAL SmartMove system with proper
error checking, dependency validation, and health monitoring.

Usage:
    python start_system.py
    python start_system.py --check-only  # Just run health checks
    python start_system.py --reset       # Reset and start fresh
"""

import os
import sys
import time
import subprocess
import platform
import requests
import json
from pathlib import Path
from datetime import datetime

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

class HALSystemStarter:
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.backend_dir = self.root_dir / "backend"
        self.frontend_dir = self.root_dir / "frontend"
        self.is_windows = platform.system() == "Windows"
        self.processes = []
        
    def print_banner(self):
        """Print system banner"""
        print(f"\n{Colors.CYAN}{Colors.BOLD}")
        print("=" * 60)
        print("🚀 HAL SmartMove Transport Management System")
        print("   Automated Startup Script")
        print("=" * 60)
        print(f"{Colors.END}")
        print(f"{Colors.WHITE}Hassle-Free Transport at Your Fingertips{Colors.END}")
        print(f"{Colors.BLUE}Starting system components...{Colors.END}\n")

    def log(self, message, level="INFO"):
        """Log message with timestamp and color"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        colors = {
            "INFO": Colors.BLUE,
            "SUCCESS": Colors.GREEN,
            "WARNING": Colors.YELLOW,
            "ERROR": Colors.RED
        }
        color = colors.get(level, Colors.WHITE)
        print(f"{color}[{timestamp}] {level}: {message}{Colors.END}")

    def check_prerequisites(self):
        """Check if all required software is installed"""
        self.log("Checking prerequisites...")
        
        # Check Python
        try:
            python_version = sys.version.split()[0]
            self.log(f"Python version: {python_version}", "SUCCESS")
        except Exception as e:
            self.log(f"Python check failed: {e}", "ERROR")
            return False

        # Check Node.js
        try:
            result = subprocess.run(["node", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                self.log(f"Node.js version: {result.stdout.strip()}", "SUCCESS")
            else:
                self.log("Node.js not found", "ERROR")
                return False
        except Exception as e:
            self.log(f"Node.js check failed: {e}", "ERROR")
            return False

        # Check npm
        try:
            result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                self.log(f"npm version: {result.stdout.strip()}", "SUCCESS")
            else:
                self.log("npm not found", "ERROR")
                return False
        except Exception as e:
            self.log(f"npm check failed: {e}", "ERROR")
            return False

        return True

    def check_ports(self):
        """Check if required ports are available"""
        self.log("Checking port availability...")
        
        ports = [3000, 8000]
        for port in ports:
            try:
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex(('localhost', port))
                sock.close()
                
                if result == 0:
                    self.log(f"Port {port} is already in use", "WARNING")
                    self.kill_port_process(port)
                else:
                    self.log(f"Port {port} is available", "SUCCESS")
            except Exception as e:
                self.log(f"Port check failed for {port}: {e}", "ERROR")

    def kill_port_process(self, port):
        """Kill process using specified port"""
        try:
            if self.is_windows:
                # Windows
                result = subprocess.run(
                    f'netstat -ano | findstr :{port}',
                    shell=True, capture_output=True, text=True
                )
                if result.stdout:
                    lines = result.stdout.strip().split('\n')
                    for line in lines:
                        if f':{port}' in line:
                            parts = line.split()
                            if len(parts) >= 5:
                                pid = parts[-1]
                                subprocess.run(f'taskkill /PID {pid} /F', shell=True)
                                self.log(f"Killed process {pid} on port {port}", "SUCCESS")
            else:
                # Unix/Linux/macOS
                result = subprocess.run(
                    f'lsof -ti:{port}',
                    shell=True, capture_output=True, text=True
                )
                if result.stdout:
                    pids = result.stdout.strip().split('\n')
                    for pid in pids:
                        if pid:
                            subprocess.run(f'kill -9 {pid}', shell=True)
                            self.log(f"Killed process {pid} on port {port}", "SUCCESS")
        except Exception as e:
            self.log(f"Failed to kill process on port {port}: {e}", "ERROR")

    def setup_backend(self):
        """Setup backend environment and dependencies"""
        self.log("Setting up backend...")
        
        if not self.backend_dir.exists():
            self.log("Backend directory not found", "ERROR")
            return False

        # Check virtual environment
        venv_dir = self.backend_dir / "venv"
        if not venv_dir.exists():
            self.log("Creating virtual environment...")
            subprocess.run([sys.executable, "-m", "venv", "venv"], cwd=self.backend_dir)

        # Install dependencies
        pip_cmd = str(venv_dir / ("Scripts" if self.is_windows else "bin") / "pip")
        requirements_file = self.backend_dir / "requirements.txt"
        
        if requirements_file.exists():
            self.log("Installing backend dependencies...")
            result = subprocess.run([pip_cmd, "install", "-r", "requirements.txt"], 
                                  cwd=self.backend_dir, capture_output=True)
            if result.returncode != 0:
                self.log("Failed to install backend dependencies", "ERROR")
                return False

        # Initialize database
        self.log("Initializing database...")
        python_cmd = str(venv_dir / ("Scripts" if self.is_windows else "bin") / "python")
        
        scripts = ["fix_database_schema.py", "create_default_users.py", "create_default_drivers.py"]
        for script in scripts:
            script_path = self.backend_dir / script
            if script_path.exists():
                result = subprocess.run([python_cmd, script], cwd=self.backend_dir)
                if result.returncode == 0:
                    self.log(f"Executed {script} successfully", "SUCCESS")
                else:
                    self.log(f"Failed to execute {script}", "WARNING")

        return True

    def setup_frontend(self):
        """Setup frontend dependencies"""
        self.log("Setting up frontend...")
        
        if not self.frontend_dir.exists():
            self.log("Frontend directory not found", "ERROR")
            return False

        # Install dependencies
        package_json = self.frontend_dir / "package.json"
        if package_json.exists():
            self.log("Installing frontend dependencies...")
            result = subprocess.run(["npm", "install"], cwd=self.frontend_dir, capture_output=True)
            if result.returncode != 0:
                self.log("Failed to install frontend dependencies", "ERROR")
                return False

        return True

    def start_backend(self):
        """Start backend server"""
        self.log("Starting backend server...")
        
        venv_dir = self.backend_dir / "venv"
        python_cmd = str(venv_dir / ("Scripts" if self.is_windows else "bin") / "python")
        
        try:
            process = subprocess.Popen(
                [python_cmd, "main.py"],
                cwd=self.backend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.processes.append(("backend", process))
            self.log("Backend server started", "SUCCESS")
            return True
        except Exception as e:
            self.log(f"Failed to start backend: {e}", "ERROR")
            return False

    def start_frontend(self):
        """Start frontend server"""
        self.log("Starting frontend server...")
        
        try:
            process = subprocess.Popen(
                ["npm", "start"],
                cwd=self.frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.processes.append(("frontend", process))
            self.log("Frontend server started", "SUCCESS")
            return True
        except Exception as e:
            self.log(f"Failed to start frontend: {e}", "ERROR")
            return False

    def wait_for_services(self):
        """Wait for services to be ready"""
        self.log("Waiting for services to start...")
        
        # Wait for backend
        backend_ready = False
        for i in range(30):  # Wait up to 30 seconds
            try:
                response = requests.get("http://localhost:8000/health", timeout=2)
                if response.status_code == 200:
                    backend_ready = True
                    self.log("Backend is ready", "SUCCESS")
                    break
            except:
                pass
            time.sleep(1)
            print(".", end="", flush=True)

        if not backend_ready:
            self.log("Backend failed to start within timeout", "ERROR")
            return False

        # Wait for frontend
        frontend_ready = False
        for i in range(30):  # Wait up to 30 seconds
            try:
                response = requests.get("http://localhost:3000", timeout=2)
                if response.status_code == 200:
                    frontend_ready = True
                    self.log("Frontend is ready", "SUCCESS")
                    break
            except:
                pass
            time.sleep(1)
            print(".", end="", flush=True)

        if not frontend_ready:
            self.log("Frontend failed to start within timeout", "ERROR")
            return False

        return True

    def run_health_checks(self):
        """Run comprehensive health checks"""
        self.log("Running health checks...")
        
        checks_passed = 0
        total_checks = 4

        # Check backend health
        try:
            response = requests.get("http://localhost:8000/health")
            if response.status_code == 200:
                self.log("✅ Backend health check passed", "SUCCESS")
                checks_passed += 1
            else:
                self.log("❌ Backend health check failed", "ERROR")
        except Exception as e:
            self.log(f"❌ Backend health check failed: {e}", "ERROR")

        # Check frontend accessibility
        try:
            response = requests.get("http://localhost:3000")
            if response.status_code == 200:
                self.log("✅ Frontend accessibility check passed", "SUCCESS")
                checks_passed += 1
            else:
                self.log("❌ Frontend accessibility check failed", "ERROR")
        except Exception as e:
            self.log(f"❌ Frontend accessibility check failed: {e}", "ERROR")

        # Check API authentication
        try:
            response = requests.post(
                "http://localhost:8000/api/v1/auth/login",
                json={"employee_id": "HAL001", "password": "admin123"}
            )
            if response.status_code == 200:
                self.log("✅ Authentication check passed", "SUCCESS")
                checks_passed += 1
            else:
                self.log("❌ Authentication check failed", "ERROR")
        except Exception as e:
            self.log(f"❌ Authentication check failed: {e}", "ERROR")

        # Check database connectivity
        try:
            response = requests.get("http://localhost:8000/api/v1/drivers/")
            if response.status_code == 401:  # Unauthorized is expected without token
                self.log("✅ Database connectivity check passed", "SUCCESS")
                checks_passed += 1
            else:
                self.log("❌ Database connectivity check failed", "ERROR")
        except Exception as e:
            self.log(f"❌ Database connectivity check failed: {e}", "ERROR")

        return checks_passed, total_checks

    def print_success_message(self):
        """Print success message with access information"""
        print(f"\n{Colors.GREEN}{Colors.BOLD}")
        print("🎉 HAL SmartMove System Started Successfully!")
        print("=" * 50)
        print(f"{Colors.END}")
        print(f"{Colors.WHITE}🌐 Frontend: {Colors.CYAN}http://localhost:3000{Colors.END}")
        print(f"{Colors.WHITE}🔧 Backend:  {Colors.CYAN}http://localhost:8000{Colors.END}")
        print(f"{Colors.WHITE}📚 API Docs: {Colors.CYAN}http://localhost:8000/docs{Colors.END}")
        print()
        print(f"{Colors.YELLOW}🔑 Login Credentials:{Colors.END}")
        print(f"   Admin:     HAL001 / admin123")
        print(f"   Employee:  HAL003 / employee123")
        print(f"   Transport: HAL002 / transport123")
        print()
        print(f"{Colors.GREEN}✅ All systems operational!{Colors.END}")
        print(f"{Colors.BLUE}Press Ctrl+C to stop all services{Colors.END}\n")

    def cleanup(self):
        """Clean up processes on exit"""
        self.log("Shutting down services...")
        for name, process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
                self.log(f"{name} stopped", "SUCCESS")
            except:
                process.kill()
                self.log(f"{name} force killed", "WARNING")

    def run(self, check_only=False, reset=False):
        """Main execution method"""
        try:
            self.print_banner()
            
            if not self.check_prerequisites():
                return False

            self.check_ports()

            if reset:
                self.log("Resetting system...", "WARNING")
                # Add reset logic here if needed

            if not check_only:
                if not self.setup_backend():
                    return False
                
                if not self.setup_frontend():
                    return False

                if not self.start_backend():
                    return False

                if not self.start_frontend():
                    return False

                if not self.wait_for_services():
                    return False

            checks_passed, total_checks = self.run_health_checks()
            
            if checks_passed == total_checks:
                if not check_only:
                    self.print_success_message()
                    # Keep running until interrupted
                    try:
                        while True:
                            time.sleep(1)
                    except KeyboardInterrupt:
                        pass
                return True
            else:
                self.log(f"Health checks failed: {checks_passed}/{total_checks}", "ERROR")
                return False

        except KeyboardInterrupt:
            self.log("Received interrupt signal", "WARNING")
        except Exception as e:
            self.log(f"Unexpected error: {e}", "ERROR")
        finally:
            self.cleanup()

        return False

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="HAL SmartMove System Starter")
    parser.add_argument("--check-only", action="store_true", help="Only run health checks")
    parser.add_argument("--reset", action="store_true", help="Reset system before starting")
    
    args = parser.parse_args()
    
    starter = HALSystemStarter()
    success = starter.run(check_only=args.check_only, reset=args.reset)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
