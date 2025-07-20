#!/usr/bin/env python3
"""
Test the transport API endpoints
"""

import requests
import json

def test_transport_api():
    """Test the transport API for HAL002"""
    base_url = "http://localhost:8000/api/v1"
    
    print("🧪 Testing Transport API for HAL002")
    print("=" * 50)
    
    # Test 1: Login as transport user HAL002
    print("\n1. Login as transport user HAL002...")
    login_response = requests.post(f"{base_url}/auth/login", json={
        'employee_id': 'HAL002',
        'password': 'transport123'
    })
    
    if login_response.status_code != 200:
        print(f"❌ Transport login failed: {login_response.status_code}")
        print(f"Response: {login_response.text}")
        return False
    
    token = login_response.json()['access_token']
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    print("✅ Transport login successful")
    
    # Test 2: Get assigned trips
    print("\n2. Get assigned trips...")
    trips_response = requests.get(f"{base_url}/transport/assigned-trips", headers=headers)
    
    if trips_response.status_code != 200:
        print(f"❌ Failed to get assigned trips: {trips_response.status_code}")
        print(f"Response: {trips_response.text}")
        return False
    
    trips_data = trips_response.json()
    print(f"✅ Retrieved assigned trips successfully")
    print(f"   - Driver: {trips_data['driver']['name']} ({trips_data['driver']['employee_id']})")
    print(f"   - Available: {trips_data['driver']['is_available']}")
    print(f"   - Assigned trips count: {trips_data['count']}")
    
    if trips_data['count'] > 0:
        print("   - Assigned trips:")
        for trip in trips_data['assigned_trips']:
            print(f"     * {trip['origin']} → {trip['destination']}")
            print(f"       Date: {trip['request_date']}, Time: {trip['request_time']}")
            print(f"       Status: {trip['status']}, Passengers: {trip['passenger_count']}")
    else:
        print("   - No assigned trips found")
    
    # Test 3: Get driver schedule
    print("\n3. Get driver schedule...")
    schedule_response = requests.get(f"{base_url}/transport/schedule", headers=headers)
    
    if schedule_response.status_code != 200:
        print(f"❌ Failed to get schedule: {schedule_response.status_code}")
        print(f"Response: {schedule_response.text}")
        return False
    
    schedule_data = schedule_response.json()
    print(f"✅ Retrieved schedule successfully")
    print(f"   - Schedule count: {schedule_data['count']}")
    print(f"   - Date range: {schedule_data['date_range']['from']} to {schedule_data['date_range']['to']}")
    
    if schedule_data['count'] > 0:
        print("   - Schedule items:")
        for item in schedule_data['schedule']:
            print(f"     * {item['date']} {item['time']}: {item['origin']} → {item['destination']}")
            print(f"       Status: {item['status']}, Vehicle: {item['vehicle']['number'] if item['vehicle'] else 'None'}")
    
    print("\n🎉 Transport API test completed successfully!")
    return True

if __name__ == "__main__":
    success = test_transport_api()
    if success:
        print("\n✅ All transport API tests passed!")
    else:
        print("\n❌ Some transport API tests failed.")
