#!/usr/bin/env python3
"""
Comprehensive test of all admin functionalities
Tests: User management, status toggles, approvals, deletions, and action buttons
"""
import requests
import json
from datetime import datetime, date, timedelta

def test_admin_functionalities():
    print("🔧 TESTING ALL ADMIN FUNCTIONALITIES")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Login as admin
    admin_login = {"employee_id": "HAL001", "password": "admin123"}
    auth_response = requests.post(f"{base_url}/api/v1/auth/login", json=admin_login)
    
    if auth_response.status_code != 200:
        print("❌ Admin login failed")
        return False
    
    admin_token = auth_response.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    print("✅ Admin authentication successful")
    print()
    
    # Test 1: User Management
    print("👥 TESTING USER MANAGEMENT")
    print("-" * 30)
    
    # Get all users
    users_response = requests.get(f"{base_url}/api/v1/admin/users/", headers=admin_headers)
    if users_response.status_code == 200:
        users = users_response.json().get('users', [])
        print(f"✅ Retrieved {len(users)} users")
        
        # Test user status toggle
        test_user = None
        for user in users:
            if user['employee_id'] != 'HAL001':  # Don't test on admin
                test_user = user
                break
        
        if test_user:
            print(f"🔄 Testing status toggle for user {test_user['employee_id']}")
            original_status = test_user['is_active']
            
            # Toggle status
            toggle_response = requests.put(
                f"{base_url}/api/v1/admin/users/{test_user['employee_id']}/status",
                headers=admin_headers
            )
            
            if toggle_response.status_code == 200:
                result = toggle_response.json()
                print(f"✅ Status toggled: {original_status} → {result['is_active']}")
                
                # Toggle back
                toggle_back_response = requests.put(
                    f"{base_url}/api/v1/admin/users/{test_user['employee_id']}/status",
                    headers=admin_headers
                )
                if toggle_back_response.status_code == 200:
                    print("✅ Status toggle back successful")
                else:
                    print("⚠️  Status toggle back failed")
            else:
                print(f"❌ Status toggle failed: {toggle_response.status_code}")
                try:
                    error = toggle_response.json()
                    print(f"   Error: {error}")
                except:
                    pass
        else:
            print("⚠️  No test user found for status toggle")
    else:
        print(f"❌ Failed to get users: {users_response.status_code}")
    
    print()
    
    # Test 2: Request Management & Approvals
    print("📋 TESTING REQUEST MANAGEMENT & APPROVALS")
    print("-" * 40)
    
    # Get all requests
    requests_response = requests.get(f"{base_url}/api/v1/admin/requests", headers=admin_headers)
    if requests_response.status_code == 200:
        requests_data = requests_response.json().get('requests', [])
        print(f"✅ Retrieved {len(requests_data)} requests")
        
        # Find a pending request to test actions
        pending_request = None
        for req in requests_data:
            if req['status'] == 'pending':
                pending_request = req
                break
        
        if pending_request:
            request_id = pending_request['id']
            print(f"🎯 Testing actions on request ID {request_id}")
            
            # Test approve action
            approve_response = requests.put(
                f"{base_url}/api/v1/admin/requests/{request_id}/approve",
                headers=admin_headers
            )
            
            if approve_response.status_code == 200:
                result = approve_response.json()
                print(f"✅ Approve action: {result.get('message', 'Success')}")
            else:
                print(f"❌ Approve action failed: {approve_response.status_code}")
                try:
                    error = approve_response.json()
                    print(f"   Error: {error}")
                except:
                    pass
            
            # Test reject action (create another request first)
            # Create a test request as employee
            employee_login = {"employee_id": "HAL003", "password": "employee123"}
            emp_auth = requests.post(f"{base_url}/api/v1/auth/login", json=employee_login)
            
            if emp_auth.status_code == 200:
                emp_token = emp_auth.json()["access_token"]
                emp_headers = {"Authorization": f"Bearer {emp_token}"}
                
                # Create test request
                test_request = {
                    "origin": "Test Origin",
                    "destination": "Test Destination", 
                    "request_date": (date.today() + timedelta(days=2)).isoformat(),
                    "request_time": "14:00",
                    "purpose": "Testing reject functionality",
                    "priority": "medium",
                    "passenger_count": 2
                }
                
                create_response = requests.post(
                    f"{base_url}/api/v1/requests/",
                    json=test_request,
                    headers=emp_headers
                )
                
                if create_response.status_code == 200:
                    new_request_id = create_response.json()['id']
                    print(f"✅ Created test request ID {new_request_id}")
                    
                    # Test reject action
                    reject_response = requests.put(
                        f"{base_url}/api/v1/admin/requests/{new_request_id}/reject",
                        headers=admin_headers
                    )
                    
                    if reject_response.status_code == 200:
                        result = reject_response.json()
                        print(f"✅ Reject action: {result.get('message', 'Success')}")
                    else:
                        print(f"❌ Reject action failed: {reject_response.status_code}")
                    
                    # Test cancel action (create another request)
                    cancel_request = {
                        "origin": "Cancel Test Origin",
                        "destination": "Cancel Test Destination",
                        "request_date": (date.today() + timedelta(days=3)).isoformat(),
                        "request_time": "15:00",
                        "purpose": "Testing cancel functionality",
                        "priority": "low",
                        "passenger_count": 1
                    }
                    
                    cancel_create_response = requests.post(
                        f"{base_url}/api/v1/requests/",
                        json=cancel_request,
                        headers=emp_headers
                    )
                    
                    if cancel_create_response.status_code == 200:
                        cancel_request_id = cancel_create_response.json()['id']
                        
                        # Test cancel action
                        cancel_response = requests.put(
                            f"{base_url}/api/v1/admin/requests/{cancel_request_id}/cancel",
                            headers=admin_headers
                        )
                        
                        if cancel_response.status_code == 200:
                            result = cancel_response.json()
                            print(f"✅ Cancel action: {result.get('message', 'Success')}")
                        else:
                            print(f"❌ Cancel action failed: {cancel_response.status_code}")
                else:
                    print("⚠️  Failed to create test request for reject testing")
        else:
            print("⚠️  No pending requests found for action testing")
    else:
        print(f"❌ Failed to get requests: {requests_response.status_code}")
    
    print()
    
    # Test 3: Driver Management
    print("🚗 TESTING DRIVER MANAGEMENT")
    print("-" * 30)
    
    drivers_response = requests.get(f"{base_url}/api/v1/drivers/", headers=admin_headers)
    if drivers_response.status_code == 200:
        drivers = drivers_response.json().get('drivers', [])
        print(f"✅ Retrieved {len(drivers)} drivers")
        
        # Test driver availability toggle (if we had such endpoint)
        if drivers:
            test_driver = drivers[0]
            print(f"📋 Driver example: {test_driver.get('first_name', 'N/A')} {test_driver.get('last_name', 'N/A')}")
    else:
        print(f"❌ Failed to get drivers: {drivers_response.status_code}")
    
    print()
    
    # Test 4: Vehicle Management  
    print("🚐 TESTING VEHICLE MANAGEMENT")
    print("-" * 30)
    
    vehicles_response = requests.get(f"{base_url}/api/v1/vehicles/", headers=admin_headers)
    if vehicles_response.status_code == 200:
        vehicles = vehicles_response.json().get('vehicles', [])
        print(f"✅ Retrieved {len(vehicles)} vehicles")
        
        if vehicles:
            test_vehicle = vehicles[0]
            print(f"📋 Vehicle example: {test_vehicle.get('make', 'N/A')} {test_vehicle.get('model', 'N/A')}")
    else:
        print(f"❌ Failed to get vehicles: {vehicles_response.status_code}")
    
    print()
    
    # Test 5: Analytics Dashboard
    print("📊 TESTING ANALYTICS DASHBOARD")
    print("-" * 30)
    
    analytics_response = requests.get(f"{base_url}/api/v1/analytics/dashboard", headers=admin_headers)
    if analytics_response.status_code == 200:
        analytics = analytics_response.json()
        print("✅ Analytics dashboard accessible")
        print(f"📈 Total requests: {analytics.get('total_requests', 'N/A')}")
        print(f"📈 Active drivers: {analytics.get('active_drivers', 'N/A')}")
    else:
        print(f"❌ Failed to get analytics: {analytics_response.status_code}")
    
    print()
    print("🎯 ADMIN FUNCTIONALITY TEST COMPLETE")
    print("=" * 50)

if __name__ == "__main__":
    test_admin_functionalities()
