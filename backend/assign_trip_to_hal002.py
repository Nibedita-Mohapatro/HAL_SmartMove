#!/usr/bin/env python3
"""
Assign a pending transport request to HAL002 for testing
"""

import requests
import json

def assign_trip_to_hal002():
    """Assign a pending request to HAL002 transport user"""
    base_url = "http://localhost:8000/api/v1"
    
    print("🚗 Assigning Trip to HAL002 Transport User")
    print("=" * 50)
    
    # Test 1: Admin login
    print("\n1. Admin login...")
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
    
    # Test 2: Get pending requests
    print("\n2. Get pending requests...")
    requests_response = requests.get(f"{base_url}/admin/requests", headers=admin_headers)
    
    if requests_response.status_code != 200:
        print(f"❌ Failed to get requests: {requests_response.status_code}")
        return False
    
    requests_data = requests_response.json()
    pending_requests = [req for req in requests_data['requests'] if req['status'] == 'pending']
    
    if not pending_requests:
        print("❌ No pending requests found")
        return False
    
    # Pick the first pending request
    request_to_assign = pending_requests[0]
    request_id = request_to_assign['id']
    
    print(f"✅ Found {len(pending_requests)} pending requests")
    print(f"   - Assigning request ID {request_id}: {request_to_assign['origin']} → {request_to_assign['destination']}")
    
    # Test 3: Get assignment options
    print("\n3. Get assignment options...")
    options_response = requests.get(f"{base_url}/admin/requests/{request_id}/assignment-options", 
                                  headers=admin_headers)
    
    if options_response.status_code != 200:
        print(f"❌ Failed to get assignment options: {options_response.status_code}")
        return False
    
    options_data = options_response.json()
    
    # Find HAL002 driver
    hal002_driver = None
    for driver in options_data['available_drivers']:
        if driver['employee_id'] == 'HAL002':
            hal002_driver = driver
            break
    
    if not hal002_driver:
        print("❌ HAL002 driver not found in available drivers")
        print("Available drivers:")
        for driver in options_data['available_drivers']:
            print(f"   - {driver['employee_id']}: {driver['name']}")
        return False
    
    # Pick the first available vehicle
    if not options_data['available_vehicles']:
        print("❌ No available vehicles found")
        return False
    
    vehicle = options_data['available_vehicles'][0]
    
    print(f"✅ Assignment options retrieved")
    print(f"   - Vehicle: {vehicle['vehicle_number']} ({vehicle['vehicle_type']})")
    print(f"   - Driver: {hal002_driver['name']} ({hal002_driver['employee_id']})")
    
    # Test 4: Assign the request
    print("\n4. Assign request to HAL002...")
    assignment_data = {
        'vehicle_id': vehicle['id'],
        'driver_id': hal002_driver['id'],
        'estimated_departure': '09:00',
        'estimated_arrival': '11:00',
        'notes': 'Assigned to HAL002 for transport dashboard testing'
    }
    
    assign_response = requests.put(f"{base_url}/admin/requests/{request_id}/approve-with-assignment", 
                                 json=assignment_data, 
                                 headers=admin_headers)
    
    if assign_response.status_code != 200:
        print(f"❌ Failed to assign request: {assign_response.status_code}")
        print(f"Response: {assign_response.text}")
        return False
    
    print("✅ Request assigned successfully to HAL002")
    
    # Test 5: Verify assignment by checking HAL002's trips
    print("\n5. Verify assignment by checking HAL002's trips...")
    transport_login = requests.post(f"{base_url}/auth/login", json={
        'employee_id': 'HAL002',
        'password': 'transport123'
    })
    
    transport_token = transport_login.json()['access_token']
    transport_headers = {
        'Authorization': f'Bearer {transport_token}',
        'Content-Type': 'application/json'
    }
    
    trips_response = requests.get(f"{base_url}/transport/assigned-trips", headers=transport_headers)

    if trips_response.status_code != 200:
        print(f"❌ Failed to get HAL002 trips: {trips_response.status_code}")
        print(f"Response: {trips_response.text}")
        return False

    trips_data = trips_response.json()

    print(f"✅ HAL002 now has {trips_data.get('count', 0)} assigned trip(s)")
    if trips_data.get('count', 0) > 0:
        for trip in trips_data['assigned_trips']:
            print(f"   - {trip['origin']} → {trip['destination']}")
            print(f"     Date: {trip['request_date']}, Time: {trip['request_time']}")
            print(f"     Status: {trip['status']}, Vehicle: {trip['vehicle']['number']}")
    
    print("\n🎉 Trip assignment to HAL002 completed successfully!")
    return True

if __name__ == "__main__":
    success = assign_trip_to_hal002()
    if success:
        print("\n✅ HAL002 trip assignment successful!")
    else:
        print("\n❌ HAL002 trip assignment failed.")
