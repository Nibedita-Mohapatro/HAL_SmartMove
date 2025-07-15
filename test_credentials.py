#!/usr/bin/env python3
"""
Test script to verify all HAL Transport Management System credentials are working
"""

import requests
import json

def test_login(employee_id, password, expected_role):
    """Test login for a specific user"""
    try:
        response = requests.post(
            'http://localhost:8000/api/v1/auth/login',
            json={'employee_id': employee_id, 'password': password},
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            user = data['user']
            print(f"✅ {employee_id}: SUCCESS")
            print(f"   Name: {user['first_name']} {user['last_name']}")
            print(f"   Role: {user['role']}")
            print(f"   Department: {user['department']}")
            print(f"   Token expires in: {data['expires_in']} seconds")
            return True
        else:
            print(f"❌ {employee_id}: FAILED")
            print(f"   Status: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ {employee_id}: ERROR - {e}")
        return False

def main():
    print("🚀 Testing HAL Transport Management System Credentials")
    print("=" * 60)
    
    # Test API health first
    try:
        health_response = requests.get('http://localhost:8000/')
        if health_response.status_code == 200:
            print("✅ API Server: RUNNING")
            data = health_response.json()
            print(f"   Message: {data['message']}")
            print(f"   Version: {data['version']}")
        else:
            print("❌ API Server: NOT RESPONDING")
            return
    except Exception as e:
        print(f"❌ API Server: ERROR - {e}")
        return
    
    print("\n🔑 Testing Demo Credentials:")
    print("-" * 40)
    
    # Test all credentials
    credentials = [
        ("HAL001", "admin123", "super_admin"),
        ("HAL002", "transport123", "admin"),
        ("HAL003", "employee123", "employee")
    ]
    
    success_count = 0
    for employee_id, password, expected_role in credentials:
        if test_login(employee_id, password, expected_role):
            success_count += 1
        print()
    
    print("📊 Test Results:")
    print(f"   Successful logins: {success_count}/3")
    print(f"   Success rate: {(success_count/3)*100:.0f}%")
    
    if success_count == 3:
        print("\n🎉 ALL CREDENTIALS ARE WORKING!")
        print("\n📱 Frontend: http://localhost:3000")
        print("🔧 Backend API: http://localhost:8000")
        print("📚 API Docs: http://localhost:8000/docs")
        print("\n💡 You can now login to the frontend with any of these credentials!")
    else:
        print("\n⚠️  Some credentials are not working. Please check the backend server.")

if __name__ == "__main__":
    main()
