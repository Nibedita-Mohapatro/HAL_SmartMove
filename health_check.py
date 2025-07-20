#!/usr/bin/env python3
"""
HAL SmartMove - System Health Check Script

This script performs comprehensive health checks on the HAL SmartMove system
to ensure all components are functioning correctly.

Usage:
    python health_check.py
    python health_check.py --detailed
    python health_check.py --json
"""

import requests
import json
import time
import sys
from datetime import datetime
import argparse

class HealthChecker:
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"
        self.results = {}
        
    def check_backend_health(self):
        """Check backend health endpoint"""
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "healthy",
                    "response_time": response.elapsed.total_seconds(),
                    "data": data
                }
            else:
                return {
                    "status": "unhealthy",
                    "error": f"HTTP {response.status_code}",
                    "response_time": response.elapsed.total_seconds()
                }
        except requests.exceptions.ConnectionError:
            return {"status": "unreachable", "error": "Connection refused"}
        except requests.exceptions.Timeout:
            return {"status": "timeout", "error": "Request timeout"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def check_frontend_health(self):
        """Check frontend accessibility"""
        try:
            response = requests.get(self.frontend_url, timeout=5)
            if response.status_code == 200:
                return {
                    "status": "healthy",
                    "response_time": response.elapsed.total_seconds()
                }
            else:
                return {
                    "status": "unhealthy",
                    "error": f"HTTP {response.status_code}",
                    "response_time": response.elapsed.total_seconds()
                }
        except requests.exceptions.ConnectionError:
            return {"status": "unreachable", "error": "Connection refused"}
        except requests.exceptions.Timeout:
            return {"status": "timeout", "error": "Request timeout"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def check_authentication(self):
        """Check authentication system"""
        try:
            response = requests.post(
                f"{self.backend_url}/api/v1/auth/login",
                json={"employee_id": "HAL001", "password": "admin123"},
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    return {
                        "status": "healthy",
                        "response_time": response.elapsed.total_seconds(),
                        "token_received": True
                    }
                else:
                    return {
                        "status": "unhealthy",
                        "error": "No access token in response"
                    }
            else:
                return {
                    "status": "unhealthy",
                    "error": f"HTTP {response.status_code}",
                    "response_time": response.elapsed.total_seconds()
                }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def check_database_connectivity(self):
        """Check database connectivity through API"""
        try:
            # Try to access an endpoint that requires database
            response = requests.get(f"{self.backend_url}/api/v1/drivers/", timeout=5)
            # We expect 401 (unauthorized) which means the endpoint is working
            # but we need authentication
            if response.status_code == 401:
                return {
                    "status": "healthy",
                    "response_time": response.elapsed.total_seconds(),
                    "note": "Database accessible (authentication required)"
                }
            elif response.status_code == 200:
                return {
                    "status": "healthy",
                    "response_time": response.elapsed.total_seconds(),
                    "note": "Database accessible"
                }
            else:
                return {
                    "status": "unhealthy",
                    "error": f"HTTP {response.status_code}",
                    "response_time": response.elapsed.total_seconds()
                }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def check_api_endpoints(self):
        """Check critical API endpoints"""
        endpoints = [
            "/api/v1/auth/login",
            "/api/v1/drivers/",
            "/api/v1/vehicles/",
            "/api/v1/requests/",
            "/docs"
        ]
        
        results = {}
        for endpoint in endpoints:
            try:
                response = requests.get(f"{self.backend_url}{endpoint}", timeout=5)
                results[endpoint] = {
                    "status_code": response.status_code,
                    "response_time": response.elapsed.total_seconds(),
                    "accessible": response.status_code in [200, 401, 422]  # Expected codes
                }
            except Exception as e:
                results[endpoint] = {
                    "status_code": None,
                    "error": str(e),
                    "accessible": False
                }
        
        return results

    def check_system_resources(self):
        """Check system resource usage"""
        try:
            import psutil
            return {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent,
                "status": "healthy"
            }
        except ImportError:
            return {
                "status": "unavailable",
                "error": "psutil not installed"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    def run_all_checks(self, detailed=False):
        """Run all health checks"""
        print("🔍 Running HAL SmartMove Health Checks...")
        print("=" * 50)
        
        # Basic checks
        print("1. Backend Health...", end=" ")
        self.results["backend"] = self.check_backend_health()
        self._print_status(self.results["backend"]["status"])
        
        print("2. Frontend Health...", end=" ")
        self.results["frontend"] = self.check_frontend_health()
        self._print_status(self.results["frontend"]["status"])
        
        print("3. Authentication...", end=" ")
        self.results["authentication"] = self.check_authentication()
        self._print_status(self.results["authentication"]["status"])
        
        print("4. Database Connectivity...", end=" ")
        self.results["database"] = self.check_database_connectivity()
        self._print_status(self.results["database"]["status"])
        
        if detailed:
            print("5. API Endpoints...", end=" ")
            self.results["api_endpoints"] = self.check_api_endpoints()
            accessible_count = sum(1 for ep in self.results["api_endpoints"].values() if ep["accessible"])
            total_count = len(self.results["api_endpoints"])
            if accessible_count == total_count:
                self._print_status("healthy")
            else:
                self._print_status("unhealthy")
            
            print("6. System Resources...", end=" ")
            self.results["system_resources"] = self.check_system_resources()
            self._print_status(self.results["system_resources"]["status"])
        
        # Summary
        print("\n" + "=" * 50)
        self._print_summary()
        
        return self.results

    def _print_status(self, status):
        """Print colored status"""
        colors = {
            "healthy": "\033[92m✅ HEALTHY\033[0m",
            "unhealthy": "\033[91m❌ UNHEALTHY\033[0m",
            "unreachable": "\033[91m🔌 UNREACHABLE\033[0m",
            "timeout": "\033[93m⏰ TIMEOUT\033[0m",
            "error": "\033[91m💥 ERROR\033[0m",
            "unavailable": "\033[93m⚠️ UNAVAILABLE\033[0m"
        }
        print(colors.get(status, f"❓ {status.upper()}"))

    def _print_summary(self):
        """Print health check summary"""
        healthy_count = 0
        total_count = 0
        
        for component, result in self.results.items():
            if component == "api_endpoints":
                # Special handling for API endpoints
                accessible = sum(1 for ep in result.values() if ep["accessible"])
                total_endpoints = len(result)
                if accessible == total_endpoints:
                    healthy_count += 1
                total_count += 1
            else:
                if result.get("status") == "healthy":
                    healthy_count += 1
                total_count += 1
        
        print(f"📊 Health Check Summary: {healthy_count}/{total_count} components healthy")
        
        if healthy_count == total_count:
            print("🎉 All systems operational!")
            print("\n🌐 Access URLs:")
            print(f"   Frontend: http://localhost:3000")
            print(f"   Backend:  http://localhost:8000")
            print(f"   API Docs: http://localhost:8000/docs")
            print("\n🔑 Login Credentials:")
            print(f"   Admin:     HAL001 / admin123")
            print(f"   Employee:  HAL003 / employee123")
            print(f"   Transport: HAL002 / transport123")
        else:
            print("⚠️ Some components are not healthy. Check the details above.")
            print("💡 Try running: python start_system.py")

    def output_json(self):
        """Output results in JSON format"""
        output = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": self._get_overall_status(),
            "checks": self.results
        }
        print(json.dumps(output, indent=2))

    def _get_overall_status(self):
        """Get overall system status"""
        critical_components = ["backend", "frontend", "authentication", "database"]
        
        for component in critical_components:
            if component in self.results:
                if self.results[component].get("status") != "healthy":
                    return "unhealthy"
        
        return "healthy"

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="HAL SmartMove Health Checker")
    parser.add_argument("--detailed", action="store_true", help="Run detailed checks")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    
    args = parser.parse_args()
    
    checker = HealthChecker()
    results = checker.run_all_checks(detailed=args.detailed)
    
    if args.json:
        checker.output_json()
    
    # Exit with appropriate code
    overall_status = checker._get_overall_status()
    sys.exit(0 if overall_status == "healthy" else 1)

if __name__ == "__main__":
    main()
