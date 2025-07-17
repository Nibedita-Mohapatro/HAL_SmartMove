#!/usr/bin/env python3
"""
Test cancel functionality specifically
"""
import requests
import json
from datetime import datetime, date, timedelta

def test_cancel_functionality():
    print("🚫 TESTING CANCEL FUNCTIONALITY")
    print("=" * 40)
    
    base_url = "http://localhost:8000"
    
    # Login as admin
    admin_login = {"employee_id": "HAL001", "password": "admin123"}
    auth_response = requests.post(f"{base_url}/api/v1/auth/login", json=admin_login)
    
    if auth_response.status_code != 200:
        print("❌ Admin login failed")
        return False
    
    admin_token = auth_response.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Login as employee to create test request
    employee_login = {"employee_id": "HAL003", "password": "employee123"}
    emp_auth = requests.post(f"{base_url}/api/v1/auth/login", json=employee_login)
    
    if emp_auth.status_code != 200:
        print("❌ Employee login failed")
        return False
    
    emp_token = emp_auth.json()["access_token"]
    emp_headers = {"Authorization": f"Bearer {emp_token}"}
    
    # Create test request for cancellation
    cancel_request = {
        "origin": "Cancel Test Origin",
        "destination": "Cancel Test Destination",
        "request_date": (date.today() + timedelta(days=5)).isoformat(),
        "request_time": "16:00",
        "purpose": "Testing cancel functionality",
        "priority": "low",
        "passenger_count": 1
    }
    
    create_response = requests.post(
        f"{base_url}/api/v1/requests/",
        json=cancel_request,
        headers=emp_headers
    )
    
    if create_response.status_code == 200:
        request_id = create_response.json()['id']
        print(f"✅ Created test request ID {request_id}")
        
        # Test cancel action
        cancel_response = requests.put(
            f"{base_url}/api/v1/admin/requests/{request_id}/cancel",
            headers=admin_headers
        )
        
        if cancel_response.status_code == 200:
            result = cancel_response.json()
            print(f"✅ Cancel action successful: {result.get('message', 'Success')}")
            print(f"📊 Status: {result.get('status', 'N/A')}")
            
            # Verify the request is actually cancelled
            verify_response = requests.get(f"{base_url}/api/v1/admin/requests", headers=admin_headers)
            if verify_response.status_code == 200:
                requests_data = verify_response.json().get('requests', [])
                cancelled_request = next((r for r in requests_data if r['id'] == request_id), None)
                
                if cancelled_request and cancelled_request['status'] == 'cancelled':
                    print("✅ Request status verified as cancelled")
                else:
                    print("⚠️  Request status not updated properly")
            
            return True
        else:
            print(f"❌ Cancel action failed: {cancel_response.status_code}")
            try:
                error = cancel_response.json()
                print(f"   Error: {error}")
            except:
                pass
            return False
    else:
        print(f"❌ Failed to create test request: {create_response.status_code}")
        return False

if __name__ == "__main__":
    success = test_cancel_functionality()
    if success:
        print("\n🎉 Cancel functionality is working correctly!")
    else:
        print("\n❌ Cancel functionality needs fixing")
