#!/usr/bin/env python3
"""
Create driver profile for transport user HAL002
"""
import requests
import json
from datetime import date, timedelta

def create_driver_profile():
    base_url = "http://localhost:8000"
    
    # Login as admin
    admin_login = {
        "employee_id": "HAL001",
        "password": "admin123"
    }
    
    response = requests.post(f"{base_url}/api/v1/auth/login", json=admin_login)
    if response.status_code != 200:
        print("❌ Failed to login as admin")
        return False
    
    admin_token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Check if driver profile already exists for HAL002
    drivers_response = requests.get(f"{base_url}/api/v1/drivers/", headers=headers)
    if drivers_response.status_code == 200:
        drivers = drivers_response.json().get('drivers', [])
        for driver in drivers:
            if driver.get('employee_id') == 'HAL002':
                print("✅ Driver profile already exists for HAL002")
                return True
    
    # Create driver profile for HAL002
    driver_data = {
        "employee_id": "HAL002",
        "first_name": "Transport",
        "last_name": "Driver",
        "phone": "+91-9876543212",
        "license_number": "DL002HAL",
        "license_expiry": (date.today() + timedelta(days=365)).isoformat(),
        "experience_years": 8
    }
    
    create_response = requests.post(f"{base_url}/api/v1/drivers/", json=driver_data, headers=headers)
    
    if create_response.status_code == 200:
        driver_result = create_response.json()
        print(f"✅ Driver profile created for HAL002 (ID: {driver_result.get('id')})")
        return True
    else:
        print(f"❌ Failed to create driver profile: {create_response.status_code}")
        try:
            error = create_response.json()
            print(f"   Error: {error}")
        except:
            pass
        return False

if __name__ == "__main__":
    print("🚗 Creating driver profile for transport user...")
    success = create_driver_profile()
    if success:
        print("✅ Driver profile setup complete")
    else:
        print("❌ Driver profile setup failed")
