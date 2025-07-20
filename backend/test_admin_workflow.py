#!/usr/bin/env python3
"""
Test the admin dashboard transport request approval workflow
"""

import requests
import json
from datetime import date, time, datetime, timedelta

def test_admin_workflow():
    """Test the complete admin workflow for transport request approval"""
    base_url = "http://localhost:8000/api/v1"
    
    print("🧪 Testing Admin Dashboard Transport Request Workflow")
    print("=" * 60)
    
    # Test 1: Employee creates a request
    print("\n1. Employee creates transport request...")
    employee_login = requests.post(f"{base_url}/auth/login", json={
        'employee_id': 'HAL003',
        'password': 'employee123'
    })
    
    if employee_login.status_code != 200:
        print(f"❌ Employee login failed: {employee_login.status_code}")
        return False
    
    employee_token = employee_login.json()['access_token']
    employee_headers = {
        'Authorization': f'Bearer {employee_token}',
        'Content-Type': 'application/json'
    }
    
    tomorrow = (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d')
    # Use a fixed time that's unlikely to conflict
    unique_time = "08:00"

    request_data = {
        'origin': 'HAL Bangalore Office',
        'destination': 'Kempegowda International Airport',
        'request_date': tomorrow,
        'request_time': unique_time,
        'passenger_count': 2,
        'purpose': f'Client meeting - Admin Test {datetime.now().strftime("%Y%m%d%H%M%S")}',
        'priority': 'high'
    }
    
    create_response = requests.post(f"{base_url}/requests/", 
                                  json=request_data, 
                                  headers=employee_headers)
    
    if create_response.status_code != 200:
        print(f"❌ Request creation failed: {create_response.status_code}")
        print(f"Response: {create_response.text}")
        return False
    
    request_id = create_response.json()['id']
    print(f"✅ Transport request created (ID: {request_id})")
    
    # Test 2: Admin login
    print("\n2. Admin login...")
    admin_login = requests.post(f"{base_url}/auth/login", json={
        'employee_id': 'HAL001',
        'password': 'admin123'
    })
    
    if admin_login.status_code != 200:
        print(f"❌ Admin login failed: {admin_login.status_code}")
        return False
    
    admin_token = admin_login.json()['access_token']
    admin_headers = {
        'Authorization': f'Bearer {admin_token}',
        'Content-Type': 'application/json'
    }
    print("✅ Admin login successful")
    
    # Test 3: Admin views all requests
    print("\n3. Admin views all transport requests...")
    all_requests = requests.get(f"{base_url}/admin/requests", headers=admin_headers)
    
    if all_requests.status_code != 200:
        print(f"❌ Failed to get requests: {all_requests.status_code}")
        print(f"Response: {all_requests.text}")
        return False
    
    requests_data = all_requests.json()
    print(f"✅ Retrieved {len(requests_data['requests'])} requests")
    
    # Test 4: Admin gets assignment options
    print("\n4. Admin gets assignment options...")
    assignment_options = requests.get(f"{base_url}/admin/requests/{request_id}/assignment-options", 
                                    headers=admin_headers)
    
    if assignment_options.status_code != 200:
        print(f"❌ Failed to get assignment options: {assignment_options.status_code}")
        print(f"Response: {assignment_options.text}")
        return False
    
    options_data = assignment_options.json()
    print(f"✅ Retrieved assignment options:")
    print(f"   - Available vehicles: {options_data['total_available_vehicles']}")
    print(f"   - Available drivers: {options_data['total_available_drivers']}")
    
    if options_data['total_available_vehicles'] == 0:
        print("⚠️  No vehicles available for assignment")
        return False
    
    if options_data['total_available_drivers'] == 0:
        print("⚠️  No drivers available for assignment")
        return False
    
    # Test 5: Admin approves request with vehicle assignment
    print("\n5. Admin approves request with vehicle assignment...")
    vehicle_id = options_data['available_vehicles'][0]['id']
    driver_id = options_data['available_drivers'][0]['id']
    
    approval_data = {
        'vehicle_id': vehicle_id,
        'driver_id': driver_id,
        'estimated_departure': '09:00',
        'estimated_arrival': '11:00',
        'notes': 'Approved for client meeting'
    }
    
    approve_response = requests.put(f"{base_url}/admin/requests/{request_id}/approve-with-assignment",
                                  json=approval_data,
                                  headers=admin_headers)
    
    if approve_response.status_code != 200:
        print(f"❌ Failed to approve request: {approve_response.status_code}")
        print(f"Response: {approve_response.text}")
        return False
    
    print("✅ Request approved with vehicle assignment")
    
    # Test 6: Verify assignment was created
    print("\n6. Verify assignment was created...")
    updated_request = requests.get(f"{base_url}/admin/requests/{request_id}", 
                                 headers=admin_headers)
    
    if updated_request.status_code != 200:
        print(f"❌ Failed to get updated request: {updated_request.status_code}")
        return False
    
    request_details = updated_request.json()
    if request_details['status'] == 'approved':
        print("✅ Request status updated to approved")
    else:
        print(f"❌ Request status not updated: {request_details['status']}")
        return False
    
    print("\n🎉 Admin workflow test completed successfully!")
    return True

if __name__ == "__main__":
    success = test_admin_workflow()
    if success:
        print("\n✅ All admin workflow tests passed!")
    else:
        print("\n❌ Some admin workflow tests failed.")
