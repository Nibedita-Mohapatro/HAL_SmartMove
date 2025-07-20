#!/usr/bin/env python3
"""
Test script for driver deletion functionality
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def login_as_admin():
    """Login as admin and return token"""
    login_data = {
        "employee_id": "HAL001",
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Login failed: {response.status_code} - {response.text}")
        return None

def get_drivers(token):
    """Get all active drivers"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/drivers/?is_active=true", headers=headers)
    
    if response.status_code == 200:
        return response.json()["drivers"]
    else:
        print(f"Failed to get drivers: {response.status_code} - {response.text}")
        return []

def create_test_driver(token):
    """Create a test driver for deletion"""
    driver_data = {
        "employee_id": "TEST001",
        "first_name": "Test",
        "last_name": "Driver",
        "phone": "9999999999",
        "license_number": "TEST123456",
        "license_expiry": "2025-12-31",
        "experience_years": 5
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(f"{BASE_URL}/drivers/", json=driver_data, headers=headers)
    
    if response.status_code == 201:
        driver = response.json()["driver"]
        print(f"✅ Created test driver: {driver['first_name']} {driver['last_name']} (ID: {driver['id']})")
        return driver
    else:
        print(f"❌ Failed to create test driver: {response.status_code} - {response.text}")
        return None

def delete_driver(token, driver_id):
    """Delete a driver"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(f"{BASE_URL}/drivers/{driver_id}", headers=headers)
    
    print(f"\n🗑️ Deleting driver ID: {driver_id}")
    print(f"Response Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Success: {result['message']}")
        if 'type' in result:
            print(f"Delete Type: {result['type']}")
        return True
    else:
        print(f"❌ Failed: {response.text}")
        return False

def main():
    print("🧪 Testing Driver Deletion Functionality")
    print("=" * 50)
    
    # Login as admin
    print("\n1. Logging in as admin...")
    token = login_as_admin()
    if not token:
        return
    print("✅ Login successful")
    
    # Get current drivers
    print("\n2. Getting current active drivers...")
    drivers_before = get_drivers(token)
    print(f"Active drivers before test: {len(drivers_before)}")
    
    # Create a test driver
    print("\n3. Creating test driver...")
    test_driver = create_test_driver(token)
    if not test_driver:
        return
    
    # Verify driver was created
    print("\n4. Verifying driver was created...")
    drivers_after_create = get_drivers(token)
    print(f"Active drivers after creation: {len(drivers_after_create)}")
    
    # Test deletion
    print("\n5. Testing driver deletion...")
    success = delete_driver(token, test_driver["id"])
    
    # Verify driver was deleted
    print("\n6. Verifying driver was deleted...")
    drivers_after_delete = get_drivers(token)
    print(f"Active drivers after deletion: {len(drivers_after_delete)}")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    print(f"Drivers before test: {len(drivers_before)}")
    print(f"Drivers after creation: {len(drivers_after_create)}")
    print(f"Drivers after deletion: {len(drivers_after_delete)}")
    
    if success and len(drivers_after_delete) == len(drivers_before):
        print("✅ DRIVER DELETION TEST PASSED!")
        print("   - Driver was successfully created")
        print("   - Driver was successfully deleted")
        print("   - Driver no longer appears in active drivers list")
    else:
        print("❌ DRIVER DELETION TEST FAILED!")
        if not success:
            print("   - Deletion API call failed")
        if len(drivers_after_delete) != len(drivers_before):
            print("   - Driver count mismatch after deletion")

if __name__ == "__main__":
    main()
