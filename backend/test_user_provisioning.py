#!/usr/bin/env python3
"""
Test script for automatic user provisioning in HAL SmartMove system.
Tests both employee and driver creation with immediate login access.
"""

import requests
import json
import time
from datetime import date, timedelta

BASE_URL = "http://localhost:8000/api/v1"

def login_admin():
    """Login as admin to get access token"""
    login_data = {
        "employee_id": "HAL001",
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Admin login failed: {response.status_code} - {response.text}")
        return None

def test_employee_creation_and_login():
    """Test creating an employee and immediate login access"""
    print("\n🧪 Testing Employee Creation and Login Access...")
    
    # Get admin token
    admin_token = login_admin()
    if not admin_token:
        return False
    
    # Generate unique employee data
    timestamp = str(int(time.time()))
    employee_data = {
        "employee_id": f"EMP{timestamp}",
        "email": f"emp{timestamp}@hal.co.in",
        "first_name": "Test",
        "last_name": "Employee",
        "password": "testpass123",
        "phone": "9876543210",
        "department": "IT",
        "designation": "Software Engineer",
        "role": "employee"
    }
    
    # Create employee via admin
    headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }
    
    print(f"📝 Creating employee: {employee_data['employee_id']}")
    response = requests.post(f"{BASE_URL}/admin/users/", json=employee_data, headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Employee creation failed: {response.status_code} - {response.text}")
        return False
    
    result = response.json()
    print(f"✅ Employee created successfully: {result['user']['employee_id']}")
    
    # Test immediate login
    print(f"🔐 Testing immediate login for employee: {employee_data['employee_id']}")
    login_data = {
        "employee_id": employee_data["employee_id"],
        "password": employee_data["password"]
    }
    
    login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    
    if login_response.status_code == 200:
        login_result = login_response.json()
        print(f"✅ Employee login successful!")
        print(f"   - Employee ID: {login_result['user']['employee_id']}")
        print(f"   - Role: {login_result['user']['role']}")
        print(f"   - Access Token: {login_result['access_token'][:20]}...")
        
        # Test accessing employee dashboard (create a transport request)
        employee_token = login_result["access_token"]
        test_request_data = {
            "origin": "HAL Office",
            "destination": "Airport",
            "request_date": str(date.today() + timedelta(days=1)),
            "request_time": "09:00:00",
            "passenger_count": 1,
            "purpose": "Business Travel"
        }
        
        employee_headers = {
            "Authorization": f"Bearer {employee_token}",
            "Content-Type": "application/json"
        }
        
        print(f"📋 Testing employee dashboard access (creating transport request)...")
        request_response = requests.post(f"{BASE_URL}/requests/", json=test_request_data, headers=employee_headers)
        
        if request_response.status_code == 200:
            print(f"✅ Employee can access dashboard and create requests!")
            return True
        else:
            print(f"❌ Employee dashboard access failed: {request_response.status_code}")
            return False
    else:
        print(f"❌ Employee login failed: {login_response.status_code} - {login_response.text}")
        return False

def test_driver_creation_and_login():
    """Test creating a driver with user account and immediate login access"""
    print("\n🧪 Testing Driver Creation with User Account and Login Access...")
    
    # Get admin token
    admin_token = login_admin()
    if not admin_token:
        return False
    
    # Generate unique driver data
    timestamp = str(int(time.time()))
    driver_data = {
        "employee_id": f"DRV{timestamp}",
        "first_name": "Test",
        "last_name": "Driver",
        "phone": "9876543211",
        "license_number": f"KA012023{timestamp}",
        "license_expiry": str(date.today() + timedelta(days=365)),
        "experience_years": 5,
        "email": f"drv{timestamp}@hal.co.in",
        "password": "driverpass123",
        "create_user_account": True
    }
    
    # Create driver via admin
    headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }
    
    print(f"📝 Creating driver with user account: {driver_data['employee_id']}")
    response = requests.post(f"{BASE_URL}/drivers/", json=driver_data, headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Driver creation failed: {response.status_code} - {response.text}")
        return False
    
    result = response.json()
    print(f"✅ Driver created successfully: {result['driver']['employee_id']}")
    
    if result.get('user_account_created'):
        print(f"✅ User account created for driver!")
        print(f"   - Employee ID: {result['user_account']['employee_id']}")
        print(f"   - Email: {result['user_account']['email']}")
        print(f"   - Role: {result['user_account']['role']}")
    else:
        print(f"❌ User account was not created for driver")
        return False
    
    # Test immediate login
    print(f"🔐 Testing immediate login for driver: {driver_data['employee_id']}")
    login_data = {
        "employee_id": driver_data["employee_id"],
        "password": driver_data["password"]
    }
    
    login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    
    if login_response.status_code == 200:
        login_result = login_response.json()
        print(f"✅ Driver login successful!")
        print(f"   - Employee ID: {login_result['user']['employee_id']}")
        print(f"   - Role: {login_result['user']['role']}")
        print(f"   - Access Token: {login_result['access_token'][:20]}...")
        
        # Test accessing transport dashboard (get assignments)
        driver_token = login_result["access_token"]
        driver_headers = {
            "Authorization": f"Bearer {driver_token}",
            "Content-Type": "application/json"
        }
        
        print(f"🚛 Testing driver dashboard access (getting assignments)...")
        assignments_response = requests.get(f"{BASE_URL}/transport/assigned-trips", headers=driver_headers)
        
        if assignments_response.status_code == 200:
            print(f"✅ Driver can access transport dashboard!")
            return True
        else:
            print(f"❌ Driver dashboard access failed: {assignments_response.status_code}")
            return False
    else:
        print(f"❌ Driver login failed: {login_response.status_code} - {login_response.text}")
        return False

def main():
    """Run all user provisioning tests"""
    print("🚀 HAL SmartMove - User Provisioning Test Suite")
    print("=" * 60)
    
    # Test employee creation and login
    employee_test_passed = test_employee_creation_and_login()
    
    # Test driver creation and login
    driver_test_passed = test_driver_creation_and_login()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"Employee Creation & Login: {'✅ PASSED' if employee_test_passed else '❌ FAILED'}")
    print(f"Driver Creation & Login:   {'✅ PASSED' if driver_test_passed else '❌ FAILED'}")
    
    if employee_test_passed and driver_test_passed:
        print("\n🎉 ALL TESTS PASSED! Automatic user provisioning is working correctly.")
        return True
    else:
        print("\n❌ SOME TESTS FAILED! Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
