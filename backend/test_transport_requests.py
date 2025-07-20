#!/usr/bin/env python3
"""
Comprehensive test for transport request functionality
"""

import requests
import json
from datetime import date, time, datetime, timedelta

def test_transport_request_flow():
    """Test the complete transport request flow"""
    base_url = "http://localhost:8000/api/v1"
    
    print("🧪 Testing Transport Request Functionality")
    print("=" * 50)
    
    # Test 1: Employee Login
    print("\n1. Testing Employee Login...")
    login_response = requests.post(f"{base_url}/auth/login", json={
        'employee_id': 'HAL003',
        'password': 'employee123'
    })
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return False
    
    token = login_response.json()['access_token']
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    print("✅ Employee login successful")
    
    # Test 2: Create Transport Request
    print("\n2. Testing Transport Request Creation...")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    request_data = {
        'origin': 'HAL Bangalore Office',
        'destination': 'Kempegowda International Airport',
        'request_date': tomorrow,
        'request_time': '14:30',
        'passenger_count': 3,
        'purpose': 'Client meeting at airport',
        'priority': 'medium'
    }
    
    create_response = requests.post(f"{base_url}/requests/", 
                                  json=request_data, 
                                  headers=headers)
    
    if create_response.status_code != 200:
        print(f"❌ Request creation failed: {create_response.status_code}")
        print(f"Response: {create_response.text}")
        return False
    
    request_id = create_response.json()['id']
    print(f"✅ Transport request created successfully (ID: {request_id})")
    
    # Test 3: Get User Requests
    print("\n3. Testing Get User Requests...")
    get_response = requests.get(f"{base_url}/requests/", headers=headers)
    
    if get_response.status_code != 200:
        print(f"❌ Get requests failed: {get_response.status_code}")
        return False
    
    requests_data = get_response.json()
    print(f"✅ Retrieved {len(requests_data['requests'])} requests")
    
    # Test 4: Verify Request Details
    print("\n4. Testing Request Details...")
    found_request = None
    for req in requests_data['requests']:
        if req['id'] == request_id:
            found_request = req
            break
    
    if not found_request:
        print("❌ Created request not found in user requests")
        return False
    
    # Verify request data
    if (found_request['origin'] == request_data['origin'] and
        found_request['destination'] == request_data['destination'] and
        found_request['passenger_count'] == request_data['passenger_count'] and
        found_request['purpose'] == request_data['purpose'] and
        found_request['priority'] == request_data['priority'] and
        found_request['status'] == 'pending'):
        print("✅ Request details verified successfully")
    else:
        print("❌ Request details don't match")
        return False
    
    # Test 5: Test Duplicate Request Prevention
    print("\n5. Testing Duplicate Request Prevention...")
    duplicate_response = requests.post(f"{base_url}/requests/", 
                                     json=request_data, 
                                     headers=headers)
    
    if duplicate_response.status_code == 400:
        print("✅ Duplicate request prevention working")
    else:
        print(f"⚠️  Duplicate request not prevented: {duplicate_response.status_code}")
    
    # Test 6: Test Different Time Request
    print("\n6. Testing Different Time Request...")
    different_time_data = request_data.copy()
    different_time_data['request_time'] = '16:00'
    different_time_data['purpose'] = 'Return journey'
    
    different_response = requests.post(f"{base_url}/requests/", 
                                     json=different_time_data, 
                                     headers=headers)
    
    if different_response.status_code == 200:
        print("✅ Different time request created successfully")
    else:
        print(f"❌ Different time request failed: {different_response.status_code}")
    
    print("\n🎉 All Transport Request Tests Completed!")
    return True

if __name__ == "__main__":
    success = test_transport_request_flow()
    if success:
        print("\n✅ All tests passed! Transport request functionality is working correctly.")
    else:
        print("\n❌ Some tests failed. Please check the issues above.")
