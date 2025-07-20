#!/usr/bin/env python3
"""
Test login functionality for default users
"""
import requests
import json

def test_login(employee_id, password):
    """Test login for a user"""
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/auth/login",
            json={
                "employee_id": employee_id,
                "password": password
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Login successful for {employee_id}")
            print(f"   Token: {data.get('access_token', 'N/A')[:50]}...")
            print(f"   User: {data.get('user', {}).get('full_name', 'N/A')}")
            print(f"   Role: {data.get('user', {}).get('role', 'N/A')}")
            return True
        else:
            print(f"❌ Login failed for {employee_id}")
            print(f"   Status: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing login for {employee_id}: {e}")
        return False

def main():
    """Test all default users"""
    print("🔐 Testing Login for Default Users")
    print("=" * 50)
    
    test_users = [
        ("HAL001", "admin123", "Super Admin"),
        ("HAL002", "transport123", "Transport Manager"),
        ("HAL003", "employee123", "Employee")
    ]
    
    success_count = 0
    for employee_id, password, role in test_users:
        print(f"\n🧪 Testing {role} ({employee_id}):")
        if test_login(employee_id, password):
            success_count += 1
    
    print(f"\n📊 Results: {success_count}/{len(test_users)} logins successful")
    
    if success_count == len(test_users):
        print("🎉 All default users can login successfully!")
        print("\n🌐 You can now access the application:")
        print("   Frontend: http://localhost:3000")
        print("   Backend API: http://localhost:8000")
        print("   API Docs: http://localhost:8000/docs")
    else:
        print("⚠️  Some login tests failed. Please check the issues above.")

if __name__ == "__main__":
    main()
