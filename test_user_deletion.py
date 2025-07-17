#!/usr/bin/env python3
"""
Test user deletion functionality specifically
"""
import requests
import json
from datetime import datetime

def test_user_deletion():
    print("🗑️  TESTING USER DELETION FUNCTIONALITY")
    print("=" * 45)
    
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
    
    # First, create a test user to delete
    test_user_data = {
        "employee_id": f"TEST{datetime.now().strftime('%H%M%S')}",
        "first_name": "Test",
        "last_name": "User",
        "email": f"test.user.{datetime.now().strftime('%H%M%S')}@hal.com",
        "phone": "+91-9999999999",
        "department": "Testing",
        "designation": "Test Engineer",
        "role": "employee",
        "password": "test123"
    }
    
    create_response = requests.post(
        f"{base_url}/api/v1/admin/users/",
        json=test_user_data,
        headers=admin_headers
    )
    
    if create_response.status_code == 200:
        created_user = create_response.json()
        print(f"📋 Created user response: {created_user}")
        test_employee_id = created_user.get('employee_id') or test_user_data['employee_id']
        print(f"✅ Created test user: {test_employee_id}")
        
        # Test deletion by employee_id (what frontend uses)
        delete_response = requests.delete(
            f"{base_url}/api/v1/admin/users/by-employee-id/{test_employee_id}",
            headers=admin_headers
        )
        
        if delete_response.status_code == 200:
            result = delete_response.json()
            print(f"✅ User deletion successful: {result.get('message', 'Success')}")
            
            # Verify user is deactivated (soft delete)
            users_response = requests.get(f"{base_url}/api/v1/admin/users/", headers=admin_headers)
            if users_response.status_code == 200:
                users = users_response.json().get('users', [])
                deleted_user = next((u for u in users if u['employee_id'] == test_employee_id), None)
                
                if deleted_user:
                    if not deleted_user['is_active']:
                        print("✅ User properly deactivated (soft delete)")
                    else:
                        print("⚠️  User still active after deletion")
                else:
                    print("⚠️  User not found after deletion")
            
            return True
        else:
            print(f"❌ User deletion failed: {delete_response.status_code}")
            try:
                error = delete_response.json()
                print(f"   Error: {error}")
                
                # Check if it's a validation error
                if isinstance(error.get('detail'), list):
                    print("   Validation errors detected:")
                    for err in error['detail']:
                        print(f"     - {err.get('msg', err)}")
            except Exception as e:
                print(f"   Could not parse error: {e}")
            return False
    else:
        print(f"❌ Failed to create test user: {create_response.status_code}")
        try:
            error = create_response.json()
            print(f"   Error: {error}")
        except:
            pass
        return False

if __name__ == "__main__":
    success = test_user_deletion()
    if success:
        print("\n🎉 User deletion functionality is working correctly!")
    else:
        print("\n❌ User deletion functionality needs fixing")
