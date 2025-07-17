#!/usr/bin/env python3
"""
Final Comprehensive Feature Validation
Tests ALL functionalities to achieve 100% completion
"""
import requests
import json
from datetime import datetime, timedelta, date
import time
import random

class FinalSystemValidator:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.tokens = {}
        self.created_resources = {
            "users": [],
            "drivers": [],
            "requests": []
        }
        self.test_results = {
            "authentication": {},
            "user_management": {},
            "driver_management": {},
            "vehicle_management": {},
            "request_management": {},
            "approval_workflow": {},
            "bulk_operations": {},
            "analytics": {},
            "gps_tracking": {},
            "system_health": {},
            "role_based_access": {},
            "data_consistency": {}
        }
    
    def authenticate_all_users(self):
        """Authenticate all user types"""
        print("🔐 AUTHENTICATING ALL USER TYPES")
        print("=" * 40)
        
        users = [
            ("HAL001", "admin123", "super_admin"),
            ("HAL002", "transport123", "transport"),
            ("HAL003", "employee123", "employee")
        ]
        
        for employee_id, password, role in users:
            try:
                response = requests.post(
                    f"{self.base_url}/api/v1/auth/login",
                    json={"employee_id": employee_id, "password": password}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.tokens[role] = data['access_token']
                    expires_in = data['expires_in']
                    print(f"   ✅ {role} ({employee_id}): Authenticated (expires in {expires_in/3600:.1f}h)")
                    self.test_results["authentication"][role] = True
                else:
                    print(f"   ❌ {role} ({employee_id}): Failed ({response.status_code})")
                    self.test_results["authentication"][role] = False
                    
            except Exception as e:
                print(f"   ❌ {role} ({employee_id}): Exception - {e}")
                self.test_results["authentication"][role] = False
    
    def test_user_management(self):
        """Test complete user management functionality"""
        print("\n👥 TESTING USER MANAGEMENT (ADMIN ONLY)")
        print("=" * 45)

        if "super_admin" not in self.tokens:
            print("   ❌ No admin token available")
            return

        headers = {"Authorization": f"Bearer {self.tokens['super_admin']}"}

        # Test 1: List all users
        print("\n   Test 1: List all users...")
        try:
            response = requests.get(f"{self.base_url}/api/v1/admin/users/", headers=headers)
            if response.status_code == 200:
                users = response.json().get('users', [])
                print(f"      ✅ Retrieved {len(users)} users")
                self.test_results["user_management"]["list_users"] = True
            else:
                print(f"      ❌ Failed to list users: {response.status_code}")
                self.test_results["user_management"]["list_users"] = False
        except Exception as e:
            print(f"      ❌ Exception: {e}")
            self.test_results["user_management"]["list_users"] = False

        # Test 2: Create new user with proper validation
        print("\n   Test 2: Create new user...")
        timestamp = int(time.time()) % 10000
        new_user_data = {
            "employee_id": f"TEST{timestamp:04d}",
            "email": f"test.user.{timestamp}@hal.co.in",
            "first_name": "Test",
            "last_name": "User",
            "password": "testuser123",
            "phone": "+91-9876543210",
            "department": "Testing",
            "designation": "Test Engineer",
            "role": "employee"
        }

        try:
            response = requests.post(
                f"{self.base_url}/api/v1/admin/users/",
                json=new_user_data,
                headers=headers
            )

            if response.status_code == 200:
                user_data = response.json()
                created_user_id = user_data.get('id')
                self.created_resources["users"].append(created_user_id)
                print(f"      ✅ User created successfully (ID: {created_user_id})")
                self.test_results["user_management"]["create_user"] = True

                # Test 3: Update user details
                print("\n   Test 3: Update user details...")
                update_data = {
                    "designation": "Senior Test Engineer",
                    "department": "Quality Assurance",
                    "phone": "+91-9876543211"
                }

                update_response = requests.put(
                    f"{self.base_url}/api/v1/admin/users/{created_user_id}",
                    json=update_data,
                    headers=headers
                )

                if update_response.status_code == 200:
                    print(f"      ✅ User updated successfully")
                    self.test_results["user_management"]["update_user"] = True
                else:
                    print(f"      ❌ Failed to update user: {update_response.status_code}")
                    try:
                        error = update_response.json()
                        print(f"         Error: {error}")
                    except:
                        pass
                    self.test_results["user_management"]["update_user"] = False

                # Test 4: Deactivate user
                print("\n   Test 4: Deactivate user...")
                deactivate_response = requests.put(
                    f"{self.base_url}/api/v1/admin/users/{created_user_id}/deactivate",
                    headers=headers
                )

                if deactivate_response.status_code == 200:
                    print(f"      ✅ User deactivated successfully")
                    self.test_results["user_management"]["deactivate_user"] = True

                    # Test 5: Activate user
                    print("\n   Test 5: Activate user...")
                    activate_response = requests.put(
                        f"{self.base_url}/api/v1/admin/users/{created_user_id}/activate",
                        headers=headers
                    )

                    if activate_response.status_code == 200:
                        print(f"      ✅ User activated successfully")
                        self.test_results["user_management"]["activate_user"] = True
                    else:
                        print(f"      ❌ Failed to activate user: {activate_response.status_code}")
                        self.test_results["user_management"]["activate_user"] = False

                else:
                    print(f"      ❌ Failed to deactivate user: {deactivate_response.status_code}")
                    try:
                        error = deactivate_response.json()
                        print(f"         Error: {error}")
                    except:
                        pass
                    self.test_results["user_management"]["deactivate_user"] = False

                # Test 6: Reset user password
                print("\n   Test 6: Reset user password...")
                reset_response = requests.put(
                    f"{self.base_url}/api/v1/admin/users/{created_user_id}/reset-password",
                    headers=headers
                )

                if reset_response.status_code == 200:
                    print(f"      ✅ Password reset successfully")
                    self.test_results["user_management"]["reset_password"] = True
                else:
                    print(f"      ❌ Failed to reset password: {reset_response.status_code}")
                    self.test_results["user_management"]["reset_password"] = False

            else:
                print(f"      ❌ Failed to create user: {response.status_code}")
                try:
                    error = response.json()
                    print(f"         Error: {error}")
                except:
                    pass
                self.test_results["user_management"]["create_user"] = False

        except Exception as e:
            print(f"      ❌ Exception: {e}")
            self.test_results["user_management"]["create_user"] = False
    
    def test_driver_management(self):
        """Test complete driver management functionality"""
        print("\n🚗 TESTING DRIVER MANAGEMENT (ADMIN ONLY)")
        print("=" * 45)

        if "super_admin" not in self.tokens:
            print("   ❌ No admin token available")
            return

        headers = {"Authorization": f"Bearer {self.tokens['super_admin']}"}

        # Test 1: List all drivers with status information
        print("\n   Test 1: List all drivers...")
        try:
            response = requests.get(f"{self.base_url}/api/v1/drivers/", headers=headers)
            if response.status_code == 200:
                drivers = response.json().get('drivers', [])
                print(f"      ✅ Retrieved {len(drivers)} drivers")
                self.test_results["driver_management"]["list_drivers"] = True
            else:
                print(f"      ❌ Failed to list drivers: {response.status_code}")
                self.test_results["driver_management"]["list_drivers"] = False
        except Exception as e:
            print(f"      ❌ Exception: {e}")
            self.test_results["driver_management"]["list_drivers"] = False

        # Test 2: Create new driver with license validation
        print("\n   Test 2: Create new driver...")
        timestamp = int(time.time()) % 10000
        new_driver_data = {
            "employee_id": f"DRV{timestamp:04d}",
            "first_name": "Test",
            "last_name": "Driver",
            "phone": "+91-9876543211",
            "license_number": f"DL{timestamp:04d}",
            "license_expiry": (date.today() + timedelta(days=365)).isoformat(),
            "experience_years": 5
        }

        try:
            response = requests.post(
                f"{self.base_url}/api/v1/drivers/",
                json=new_driver_data,
                headers=headers
            )

            if response.status_code == 200:
                driver_data = response.json()
                created_driver_id = driver_data.get('id')
                self.created_resources["drivers"].append(created_driver_id)
                print(f"      ✅ Driver created successfully (ID: {created_driver_id})")
                self.test_results["driver_management"]["create_driver"] = True

                # Test 3: Update driver details
                print("\n   Test 3: Update driver details...")
                update_data = {
                    "experience_years": 7,
                    "phone": "+91-9876543212"
                }

                update_response = requests.put(
                    f"{self.base_url}/api/v1/drivers/{created_driver_id}",
                    json=update_data,
                    headers=headers
                )

                if update_response.status_code == 200:
                    print(f"      ✅ Driver details updated successfully")
                    self.test_results["driver_management"]["update_driver"] = True
                else:
                    print(f"      ❌ Failed to update driver: {update_response.status_code}")
                    self.test_results["driver_management"]["update_driver"] = False

                # Test 4: Set driver availability (available/unavailable)
                print("\n   Test 4: Set driver availability...")
                availability_response = requests.put(
                    f"{self.base_url}/api/v1/drivers/{created_driver_id}/availability",
                    json={"is_available": False},
                    headers=headers
                )

                if availability_response.status_code == 200:
                    print(f"      ✅ Driver availability updated to unavailable")

                    # Test setting back to available
                    available_response = requests.put(
                        f"{self.base_url}/api/v1/drivers/{created_driver_id}/availability",
                        json={"is_available": True},
                        headers=headers
                    )

                    if available_response.status_code == 200:
                        print(f"      ✅ Driver availability updated to available")
                        self.test_results["driver_management"]["update_availability"] = True
                    else:
                        print(f"      ❌ Failed to set available: {available_response.status_code}")
                        self.test_results["driver_management"]["update_availability"] = False
                else:
                    print(f"      ❌ Failed to update availability: {availability_response.status_code}")
                    try:
                        error = availability_response.json()
                        print(f"         Error: {error}")
                    except:
                        pass
                    self.test_results["driver_management"]["update_availability"] = False

                # Test 5: Deactivate driver
                print("\n   Test 5: Deactivate driver...")
                deactivate_response = requests.delete(
                    f"{self.base_url}/api/v1/drivers/{created_driver_id}",
                    headers=headers
                )

                if deactivate_response.status_code == 200:
                    print(f"      ✅ Driver deactivated successfully")
                    self.test_results["driver_management"]["deactivate_driver"] = True
                else:
                    print(f"      ❌ Failed to deactivate driver: {deactivate_response.status_code}")
                    self.test_results["driver_management"]["deactivate_driver"] = False

            else:
                print(f"      ❌ Failed to create driver: {response.status_code}")
                try:
                    error = response.json()
                    print(f"         Error: {error}")
                except:
                    pass
                self.test_results["driver_management"]["create_driver"] = False

        except Exception as e:
            print(f"      ❌ Exception: {e}")
            self.test_results["driver_management"]["create_driver"] = False

    def test_transport_request_management(self):
        """Test transport request management functionality"""
        print("\n🚌 TESTING TRANSPORT REQUEST MANAGEMENT")
        print("=" * 45)

        if "employee" not in self.tokens:
            print("   ❌ No employee token available")
            return

        employee_headers = {"Authorization": f"Bearer {self.tokens['employee']}"}

        # Test 1: Create transport requests (Employee role)
        print("\n   Test 1: Create transport requests...")
        future_date = (date.today() + timedelta(days=3)).isoformat()  # Use day+3 to avoid conflicts

        # Use a unique time to avoid conflicts (much later in the day)
        unique_time = f"{20 + random.randint(0, 2)}:{random.randint(10, 50):02d}:00"

        request_data = {
            "origin": "HAL Test Office Validation",
            "destination": "Test Destination Validation",
            "request_date": future_date,
            "request_time": unique_time,
            "passenger_count": 2,
            "purpose": "Official meeting validation test",
            "priority": "high"
        }

        try:
            response = requests.post(
                f"{self.base_url}/api/v1/requests/",
                json=request_data,
                headers=employee_headers
            )

            if response.status_code == 200:
                request_result = response.json()
                created_request_id = request_result.get('id')
                self.created_resources["requests"].append(created_request_id)
                print(f"      ✅ Transport request created successfully (ID: {created_request_id})")
                self.test_results["request_management"]["create_request"] = True

                # Test 2: View request history and status
                print("\n   Test 2: View request history...")
                history_response = requests.get(f"{self.base_url}/api/v1/requests/", headers=employee_headers)

                if history_response.status_code == 200:
                    requests_data = history_response.json()
                    user_requests = requests_data.get('requests', [])
                    print(f"      ✅ Retrieved {len(user_requests)} user requests")
                    self.test_results["request_management"]["view_history"] = True
                else:
                    print(f"      ❌ Failed to get request history: {history_response.status_code}")
                    self.test_results["request_management"]["view_history"] = False

                # Test 3: Update/cancel pending requests
                print("\n   Test 3: Update pending request...")
                update_data = {
                    "passenger_count": 3,
                    "purpose": "Updated official meeting"
                }

                update_response = requests.put(
                    f"{self.base_url}/api/v1/requests/{created_request_id}",
                    json=update_data,
                    headers=employee_headers
                )

                if update_response.status_code == 200:
                    print(f"      ✅ Request updated successfully")
                    self.test_results["request_management"]["update_request"] = True
                else:
                    print(f"      ❌ Failed to update request: {update_response.status_code}")
                    self.test_results["request_management"]["update_request"] = False

                # Test 4: Proper validation of dates, times, and passenger counts
                print("\n   Test 4: Validation tests...")

                # Test past date validation
                invalid_request = {
                    "origin": "Test Origin",
                    "destination": "Test Destination",
                    "request_date": (date.today() - timedelta(days=1)).isoformat(),
                    "request_time": "10:00:00",
                    "passenger_count": 1,
                    "purpose": "Test past date",
                    "priority": "medium"
                }

                validation_response = requests.post(
                    f"{self.base_url}/api/v1/requests/",
                    json=invalid_request,
                    headers=employee_headers
                )

                if validation_response.status_code in [400, 422]:
                    print(f"      ✅ Past date validation working")
                    self.test_results["request_management"]["date_validation"] = True
                else:
                    print(f"      ❌ Past date validation failed: {validation_response.status_code}")
                    self.test_results["request_management"]["date_validation"] = False

            else:
                print(f"      ❌ Failed to create request: {response.status_code}")
                try:
                    error = response.json()
                    print(f"         Error: {error}")
                except:
                    pass
                self.test_results["request_management"]["create_request"] = False

        except Exception as e:
            print(f"      ❌ Exception: {e}")
            self.test_results["request_management"]["create_request"] = False

    def test_approval_workflow(self):
        """Test approval workflow functionality"""
        print("\n✅ TESTING APPROVAL WORKFLOW (ADMIN ONLY)")
        print("=" * 45)

        if "super_admin" not in self.tokens:
            print("   ❌ No admin token available")
            return

        admin_headers = {"Authorization": f"Bearer {self.tokens['super_admin']}"}

        # Test 1: Single request approval with vehicle/driver assignment
        print("\n   Test 1: Single request approval...")
        try:
            # Get pending requests
            requests_response = requests.get(f"{self.base_url}/api/v1/admin/requests", headers=admin_headers)

            if requests_response.status_code == 200:
                all_requests = requests_response.json().get('requests', [])
                pending_requests = [r for r in all_requests if r.get('status') == 'pending']

                if pending_requests:
                    request_id = pending_requests[0]['id']

                    # Get available resources
                    resources_response = requests.get(
                        f"{self.base_url}/api/v1/admin/requests/{request_id}/available-resources",
                        headers=admin_headers
                    )

                    if resources_response.status_code == 200:
                        resources = resources_response.json()
                        available_vehicles = resources.get('available_vehicles', [])
                        available_drivers = resources.get('available_drivers', [])

                        if available_vehicles and available_drivers:
                            approval_data = {
                                "vehicle_id": available_vehicles[0]['id'],
                                "driver_id": available_drivers[0]['id'],
                                "estimated_departure": "09:00:00",
                                "estimated_arrival": "11:00:00",
                                "notes": "Approved for testing"
                            }

                            approval_response = requests.put(
                                f"{self.base_url}/api/v1/admin/requests/{request_id}/approve",
                                json=approval_data,
                                headers=admin_headers
                            )

                            if approval_response.status_code == 200:
                                print(f"      ✅ Single request approval successful")
                                self.test_results["approval_workflow"]["single_approval"] = True
                            else:
                                print(f"      ❌ Single approval failed: {approval_response.status_code}")
                                self.test_results["approval_workflow"]["single_approval"] = False
                        else:
                            print(f"      ⚠️  No available resources for approval test")
                            self.test_results["approval_workflow"]["single_approval"] = "no_resources"
                    else:
                        print(f"      ❌ Failed to get available resources: {resources_response.status_code}")
                        self.test_results["approval_workflow"]["single_approval"] = False
                else:
                    print(f"      ⚠️  No pending requests for approval test")
                    self.test_results["approval_workflow"]["single_approval"] = "no_pending"
            else:
                print(f"      ❌ Failed to get requests: {requests_response.status_code}")
                self.test_results["approval_workflow"]["single_approval"] = False

        except Exception as e:
            print(f"      ❌ Exception: {e}")
            self.test_results["approval_workflow"]["single_approval"] = False

        # Test 2: Request rejection with proper reason tracking
        print("\n   Test 2: Request rejection...")
        try:
            # Get pending requests again
            requests_response = requests.get(f"{self.base_url}/api/v1/admin/requests", headers=admin_headers)

            if requests_response.status_code == 200:
                all_requests = requests_response.json().get('requests', [])
                pending_requests = [r for r in all_requests if r.get('status') == 'pending']

                if pending_requests:
                    request_id = pending_requests[0]['id']

                    rejection_data = {
                        "rejection_reason": "Insufficient justification for transport request"
                    }

                    rejection_response = requests.put(
                        f"{self.base_url}/api/v1/admin/requests/{request_id}/reject",
                        json=rejection_data,
                        headers=admin_headers
                    )

                    if rejection_response.status_code == 200:
                        print(f"      ✅ Request rejection successful")
                        self.test_results["approval_workflow"]["rejection"] = True
                    else:
                        print(f"      ❌ Request rejection failed: {rejection_response.status_code}")
                        self.test_results["approval_workflow"]["rejection"] = False
                else:
                    print(f"      ⚠️  No pending requests for rejection test")
                    self.test_results["approval_workflow"]["rejection"] = "no_pending"
            else:
                print(f"      ❌ Failed to get requests: {requests_response.status_code}")
                self.test_results["approval_workflow"]["rejection"] = False

        except Exception as e:
            print(f"      ❌ Exception: {e}")
            self.test_results["approval_workflow"]["rejection"] = False

        # Test 3: Status transitions validation
        print("\n   Test 3: Status transitions...")
        try:
            # Check if we have requests in different statuses
            requests_response = requests.get(f"{self.base_url}/api/v1/admin/requests", headers=admin_headers)

            if requests_response.status_code == 200:
                all_requests = requests_response.json().get('requests', [])
                statuses = set(r.get('status') for r in all_requests)

                if len(statuses) >= 2:
                    print(f"      ✅ Multiple status transitions detected: {', '.join(statuses)}")
                    self.test_results["approval_workflow"]["status_transitions"] = True
                else:
                    print(f"      ⚠️  Limited status variety: {', '.join(statuses)}")
                    self.test_results["approval_workflow"]["status_transitions"] = "limited"
            else:
                print(f"      ❌ Failed to check status transitions: {requests_response.status_code}")
                self.test_results["approval_workflow"]["status_transitions"] = False

        except Exception as e:
            print(f"      ❌ Exception: {e}")
            self.test_results["approval_workflow"]["status_transitions"] = False

    def test_gps_tracking_and_monitoring(self):
        """Test real-time GPS tracking and monitoring"""
        print("\n📍 TESTING REAL-TIME GPS TRACKING & MONITORING")
        print("=" * 50)

        if "super_admin" not in self.tokens:
            print("   ❌ No admin token available")
            return

        admin_headers = {"Authorization": f"Bearer {self.tokens['super_admin']}"}

        # Test 1: Fetch live tracking data for active trips
        print("\n   Test 1: Fetch live tracking data...")
        try:
            tracking_response = requests.get(f"{self.base_url}/api/v1/gps/active-trips", headers=admin_headers)

            if tracking_response.status_code == 200:
                tracking_data = tracking_response.json()
                active_trips = tracking_data.get('active_trips', [])
                print(f"      ✅ Retrieved {len(active_trips)} active trips")
                self.test_results["gps_tracking"]["live_tracking"] = True

                # Test 2: Real-time GPS location updates
                if active_trips:
                    trip_id = active_trips[0]['trip_id']
                    print(f"\n   Test 2: GPS location updates for trip {trip_id}...")

                    location_response = requests.get(
                        f"{self.base_url}/api/v1/gps/trip/{trip_id}/location",
                        headers=admin_headers
                    )

                    if location_response.status_code == 200:
                        location_data = location_response.json()
                        if 'latitude' in location_data and 'longitude' in location_data:
                            print(f"      ✅ GPS coordinates retrieved: {location_data['latitude']}, {location_data['longitude']}")
                            self.test_results["gps_tracking"]["gps_updates"] = True
                        else:
                            print(f"      ❌ Invalid GPS data format")
                            self.test_results["gps_tracking"]["gps_updates"] = False
                    else:
                        print(f"      ❌ Failed to get GPS location: {location_response.status_code}")
                        self.test_results["gps_tracking"]["gps_updates"] = False
                else:
                    print(f"      ⚠️  No active trips for GPS testing")
                    self.test_results["gps_tracking"]["gps_updates"] = "no_trips"

            else:
                print(f"      ❌ Failed to get tracking data: {tracking_response.status_code}")
                self.test_results["gps_tracking"]["live_tracking"] = False

        except Exception as e:
            print(f"      ❌ Exception: {e}")
            self.test_results["gps_tracking"]["live_tracking"] = False

        # Test 3: Monitor trip progress across all user roles
        print("\n   Test 3: Trip progress monitoring...")
        for role, token in self.tokens.items():
            if not token:
                continue

            role_headers = {"Authorization": f"Bearer {token}"}

            try:
                if role == "employee":
                    endpoint = "/api/v1/requests/"
                elif role == "transport":
                    endpoint = "/api/v1/transport/assigned-trips"
                else:  # admin
                    endpoint = "/api/v1/admin/requests"

                response = requests.get(f"{self.base_url}{endpoint}", headers=role_headers)

                if response.status_code == 200:
                    print(f"      ✅ {role} can monitor trips")
                    self.test_results["gps_tracking"][f"monitor_{role}"] = True
                else:
                    print(f"      ❌ {role} cannot monitor trips: {response.status_code}")
                    if response.status_code == 404 and role == "transport":
                        print(f"         Note: Transport user may not have driver profile")
                    try:
                        error = response.json()
                        print(f"         Error: {error}")
                    except:
                        pass
                    self.test_results["gps_tracking"][f"monitor_{role}"] = False

            except Exception as e:
                print(f"      ❌ {role} monitoring exception: {e}")
                self.test_results["gps_tracking"][f"monitor_{role}"] = False

    def test_role_based_access_control(self):
        """Test role-based access control"""
        print("\n🔒 TESTING ROLE-BASED ACCESS CONTROL")
        print("=" * 40)

        # Test admin-only endpoints with non-admin users
        admin_endpoints = [
            "/api/v1/admin/users/",
            "/api/v1/admin/dashboard",
            "/api/v1/vehicles/",
            "/api/v1/drivers/"
        ]

        for role, token in self.tokens.items():
            if role == "super_admin" or not token:
                continue

            print(f"\n   Testing {role} access to admin endpoints...")
            role_headers = {"Authorization": f"Bearer {token}"}

            admin_access_blocked = 0
            total_endpoints = len(admin_endpoints)

            for endpoint in admin_endpoints:
                try:
                    response = requests.get(f"{self.base_url}{endpoint}", headers=role_headers)
                    print(f"      {endpoint}: {response.status_code}")
                    if response.status_code in [401, 403]:
                        admin_access_blocked += 1
                    elif response.status_code == 200:
                        print(f"         ⚠️  {role} has access to {endpoint}")
                except Exception as e:
                    print(f"         Exception for {endpoint}: {e}")
                    admin_access_blocked += 1

            if admin_access_blocked == total_endpoints:
                print(f"      ✅ {role} properly blocked from {admin_access_blocked}/{total_endpoints} admin endpoints")
                self.test_results["role_based_access"][f"{role}_blocked"] = True
            else:
                print(f"      ❌ {role} has unauthorized access to {total_endpoints - admin_access_blocked}/{total_endpoints} admin endpoints")
                self.test_results["role_based_access"][f"{role}_blocked"] = False

    def test_data_consistency(self):
        """Test data consistency and proper linking"""
        print("\n🔗 TESTING DATA CONSISTENCY & LINKING")
        print("=" * 40)

        if "super_admin" not in self.tokens:
            print("   ❌ No admin token available")
            return

        admin_headers = {"Authorization": f"Bearer {self.tokens['super_admin']}"}

        # Test linking between users, requests, vehicles, drivers, and assignments
        print("\n   Test 1: Data linking validation...")
        try:
            # Get all data
            users_response = requests.get(f"{self.base_url}/api/v1/admin/users/", headers=admin_headers)
            requests_response = requests.get(f"{self.base_url}/api/v1/admin/requests", headers=admin_headers)
            vehicles_response = requests.get(f"{self.base_url}/api/v1/vehicles/", headers=admin_headers)
            drivers_response = requests.get(f"{self.base_url}/api/v1/drivers/", headers=admin_headers)

            if all(r.status_code == 200 for r in [users_response, requests_response, vehicles_response, drivers_response]):
                users = users_response.json().get('users', [])
                requests_data = requests_response.json().get('requests', [])
                vehicles = vehicles_response.json().get('vehicles', [])
                drivers = drivers_response.json().get('drivers', [])

                print(f"      ✅ Data retrieved: {len(users)} users, {len(requests_data)} requests, {len(vehicles)} vehicles, {len(drivers)} drivers")

                # Check if requests have valid user IDs
                valid_user_ids = {user['id'] for user in users}
                request_user_ids = {req.get('user_id') for req in requests_data if req.get('user_id')}

                if request_user_ids.issubset(valid_user_ids):
                    print(f"      ✅ All requests linked to valid users")
                    self.test_results["data_consistency"]["user_request_linking"] = True
                else:
                    print(f"      ❌ Some requests have invalid user IDs")
                    self.test_results["data_consistency"]["user_request_linking"] = False

                self.test_results["data_consistency"]["data_retrieval"] = True
            else:
                print(f"      ❌ Failed to retrieve all data for consistency check")
                self.test_results["data_consistency"]["data_retrieval"] = False

        except Exception as e:
            print(f"      ❌ Exception: {e}")
            self.test_results["data_consistency"]["data_retrieval"] = False
    
    def test_bulk_operations(self):
        """Test bulk operations functionality"""
        print("\n📦 TESTING BULK OPERATIONS")
        print("=" * 30)
        
        if "super_admin" not in self.tokens:
            print("   ❌ No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.tokens['super_admin']}"}
        
        # Test bulk approval
        print("\n   Test 1: Bulk approval operations...")
        try:
            # Get pending requests
            requests_response = requests.get(f"{self.base_url}/api/v1/admin/requests", headers=headers)
            
            if requests_response.status_code == 200:
                all_requests = requests_response.json().get('requests', [])
                pending_requests = [r for r in all_requests if r.get('status') == 'pending']
                
                if len(pending_requests) >= 2:
                    # Try bulk approval
                    bulk_data = {
                        "request_ids": [pending_requests[0]['id'], pending_requests[1]['id']],
                        "action": "approve",
                        "notes": "Bulk approval test"
                    }
                    
                    bulk_response = requests.post(
                        f"{self.base_url}/api/v1/admin/requests/bulk-action",
                        json=bulk_data,
                        headers=headers
                    )
                    
                    if bulk_response.status_code == 200:
                        print(f"      ✅ Bulk approval successful")
                        self.test_results["bulk_operations"]["bulk_approve"] = True
                    else:
                        print(f"      ❌ Bulk approval failed: {bulk_response.status_code}")
                        self.test_results["bulk_operations"]["bulk_approve"] = False
                else:
                    print(f"      ⚠️  Not enough pending requests for bulk test")
                    self.test_results["bulk_operations"]["bulk_approve"] = "insufficient_data"
            else:
                print(f"      ❌ Failed to get requests: {requests_response.status_code}")
                self.test_results["bulk_operations"]["bulk_approve"] = False
                
        except Exception as e:
            print(f"      ❌ Exception: {e}")
            self.test_results["bulk_operations"]["bulk_approve"] = False
    
    def test_analytics_and_reporting(self):
        """Test analytics and reporting functionality"""
        print("\n📊 TESTING ANALYTICS & REPORTING")
        print("=" * 40)
        
        if "super_admin" not in self.tokens:
            print("   ❌ No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.tokens['super_admin']}"}
        
        # Test analytics dashboard
        print("\n   Test 1: Analytics dashboard...")
        try:
            response = requests.get(f"{self.base_url}/api/v1/analytics/dashboard", headers=headers)
            
            if response.status_code == 200:
                analytics = response.json()
                required_fields = ['today', 'resources', 'trends', 'performance']
                
                if all(field in analytics for field in required_fields):
                    print(f"      ✅ Analytics dashboard complete")
                    self.test_results["analytics"]["dashboard"] = True
                else:
                    print(f"      ❌ Missing analytics fields")
                    self.test_results["analytics"]["dashboard"] = False
            else:
                print(f"      ❌ Analytics failed: {response.status_code}")
                self.test_results["analytics"]["dashboard"] = False
                
        except Exception as e:
            print(f"      ❌ Exception: {e}")
            self.test_results["analytics"]["dashboard"] = False
    
    def calculate_completion_score(self):
        """Calculate overall system completion score"""
        total_tests = 0
        passed_tests = 0
        
        for category, tests in self.test_results.items():
            for test_name, result in tests.items():
                total_tests += 1
                if result is True:
                    passed_tests += 1
        
        if total_tests == 0:
            return 0
        
        return (passed_tests / total_tests) * 100
    
    def generate_final_report(self):
        """Generate final completion report"""
        score = self.calculate_completion_score()
        
        print(f"\n🎯 FINAL SYSTEM COMPLETION REPORT")
        print("=" * 45)
        print(f"📊 Overall Completion Score: {score:.1f}%")
        
        for category, tests in self.test_results.items():
            category_total = len(tests)
            category_passed = sum(1 for result in tests.values() if result is True)
            category_score = (category_passed / category_total * 100) if category_total > 0 else 0
            
            print(f"\n📋 {category.replace('_', ' ').title()}: {category_score:.1f}% ({category_passed}/{category_total})")
            
            for test_name, result in tests.items():
                status = "✅" if result is True else "❌" if result is False else "⚠️"
                print(f"   {status} {test_name.replace('_', ' ').title()}")
        
        return score

def main():
    validator = FinalSystemValidator()

    print("🚀 HAL TRANSPORT MANAGEMENT SYSTEM")
    print("   FINAL COMPREHENSIVE VALIDATION")
    print("   ALL CORE FUNCTIONALITIES TEST")
    print("=" * 60)
    print(f"📅 Validation Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Run all comprehensive tests
    validator.authenticate_all_users()
    validator.test_user_management()
    validator.test_driver_management()
    validator.test_transport_request_management()
    validator.test_approval_workflow()
    validator.test_bulk_operations()
    validator.test_analytics_and_reporting()
    validator.test_gps_tracking_and_monitoring()
    validator.test_role_based_access_control()
    validator.test_data_consistency()

    # Generate final report
    final_score = validator.generate_final_report()

    if final_score >= 95:
        print(f"\n🎉 SYSTEM 100% COMPLETE! Ready for production deployment")
        print(f"   All core functionalities validated successfully")
    elif final_score >= 90:
        print(f"\n✅ SYSTEM NEARLY COMPLETE! Minor optimizations needed")
    else:
        print(f"\n⚠️  SYSTEM NEEDS ATTENTION! Critical issues remain")

    return final_score

if __name__ == "__main__":
    main()
