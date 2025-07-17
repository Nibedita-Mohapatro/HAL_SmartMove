#!/usr/bin/env python3
"""
Sample Data Generator for HAL Transport Management System
Creates sample users, vehicles, drivers, and requests for testing and demonstration
"""
import requests
import json
from datetime import datetime, date, timedelta
import random

class SampleDataGenerator:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.admin_headers = None
        
    def authenticate_admin(self):
        """Authenticate as admin to create sample data"""
        print("🔐 Authenticating as admin...")
        
        response = requests.post(f"{self.base_url}/api/v1/auth/login", json={
            "employee_id": "HAL001",
            "password": "admin123"
        })
        
        if response.status_code == 200:
            token = response.json()["access_token"]
            self.admin_headers = {"Authorization": f"Bearer {token}"}
            print("✅ Admin authentication successful")
            return True
        else:
            print("❌ Admin authentication failed")
            return False
    
    def create_sample_users(self):
        """Create sample users for different departments"""
        print("\n👥 Creating sample users...")
        
        sample_users = [
            {
                "employee_id": "HAL101",
                "first_name": "Rajesh",
                "last_name": "Kumar",
                "email": "rajesh.kumar@hal.com",
                "phone": "+91-9876543210",
                "department": "Engineering",
                "designation": "Senior Engineer",
                "role": "employee",
                "password": "employee123"
            },
            {
                "employee_id": "HAL102",
                "first_name": "Priya",
                "last_name": "Sharma",
                "email": "priya.sharma@hal.com",
                "phone": "+91-9876543211",
                "department": "Human Resources",
                "designation": "HR Manager",
                "role": "employee",
                "password": "employee123"
            },
            {
                "employee_id": "HAL103",
                "first_name": "Amit",
                "last_name": "Singh",
                "email": "amit.singh@hal.com",
                "phone": "+91-9876543212",
                "department": "Finance",
                "designation": "Financial Analyst",
                "role": "employee",
                "password": "employee123"
            },
            {
                "employee_id": "HAL104",
                "first_name": "Sunita",
                "last_name": "Patel",
                "email": "sunita.patel@hal.com",
                "phone": "+91-9876543213",
                "department": "Quality Assurance",
                "designation": "QA Lead",
                "role": "employee",
                "password": "employee123"
            },
            {
                "employee_id": "HAL105",
                "first_name": "Vikram",
                "last_name": "Reddy",
                "email": "vikram.reddy@hal.com",
                "phone": "+91-9876543214",
                "department": "Research & Development",
                "designation": "Research Scientist",
                "role": "employee",
                "password": "employee123"
            },
            {
                "employee_id": "HAL201",
                "first_name": "Ravi",
                "last_name": "Gupta",
                "email": "ravi.gupta@hal.com",
                "phone": "+91-9876543215",
                "department": "Transport",
                "designation": "Senior Driver",
                "role": "transport",
                "password": "transport123"
            },
            {
                "employee_id": "HAL202",
                "first_name": "Suresh",
                "last_name": "Yadav",
                "email": "suresh.yadav@hal.com",
                "phone": "+91-9876543216",
                "department": "Transport",
                "designation": "Driver",
                "role": "transport",
                "password": "transport123"
            }
        ]
        
        created_count = 0
        for user_data in sample_users:
            response = requests.post(
                f"{self.base_url}/api/v1/admin/users/",
                json=user_data,
                headers=self.admin_headers
            )
            
            if response.status_code == 200:
                print(f"✅ Created user: {user_data['employee_id']} - {user_data['first_name']} {user_data['last_name']}")
                created_count += 1
            else:
                print(f"⚠️  User {user_data['employee_id']} might already exist")
        
        print(f"📊 Created {created_count} new users")
        return True
    
    def create_sample_requests(self):
        """Create sample transport requests"""
        print("\n📋 Creating sample transport requests...")
        
        # Get employee tokens for creating requests
        employees = ["HAL101", "HAL102", "HAL103", "HAL104", "HAL105"]
        
        sample_requests = [
            {
                "employee_id": "HAL101",
                "origin": "HAL Bangalore Office",
                "destination": "Kempegowda International Airport",
                "request_date": (date.today() + timedelta(days=1)).isoformat(),
                "request_time": "09:00",
                "purpose": "Official travel to Delhi for project meeting",
                "priority": "high",
                "passenger_count": 1
            },
            {
                "employee_id": "HAL102",
                "origin": "HAL Bangalore Office",
                "destination": "Bangalore Railway Station",
                "request_date": (date.today() + timedelta(days=2)).isoformat(),
                "request_time": "14:30",
                "purpose": "Personal travel",
                "priority": "medium",
                "passenger_count": 2
            },
            {
                "employee_id": "HAL103",
                "origin": "Whitefield",
                "destination": "HAL Bangalore Office",
                "request_date": (date.today() + timedelta(days=3)).isoformat(),
                "request_time": "08:00",
                "purpose": "Daily commute - special request",
                "priority": "low",
                "passenger_count": 1
            },
            {
                "employee_id": "HAL104",
                "origin": "HAL Bangalore Office",
                "destination": "Bangalore Medical College",
                "request_date": (date.today() + timedelta(days=4)).isoformat(),
                "request_time": "11:00",
                "purpose": "Medical appointment",
                "priority": "high",
                "passenger_count": 1
            },
            {
                "employee_id": "HAL105",
                "origin": "Electronic City",
                "destination": "HAL Bangalore Office",
                "request_date": (date.today() + timedelta(days=5)).isoformat(),
                "request_time": "07:30",
                "purpose": "Early morning meeting",
                "priority": "medium",
                "passenger_count": 1
            }
        ]
        
        created_count = 0
        for req_data in sample_requests:
            # Login as the employee
            employee_id = req_data.pop("employee_id")
            
            login_response = requests.post(f"{self.base_url}/api/v1/auth/login", json={
                "employee_id": employee_id,
                "password": "employee123"
            })
            
            if login_response.status_code == 200:
                employee_token = login_response.json()["access_token"]
                employee_headers = {"Authorization": f"Bearer {employee_token}"}
                
                # Create request
                response = requests.post(
                    f"{self.base_url}/api/v1/requests/",
                    json=req_data,
                    headers=employee_headers
                )
                
                if response.status_code == 200:
                    request_id = response.json()['id']
                    print(f"✅ Created request: ID {request_id} by {employee_id}")
                    created_count += 1
                else:
                    print(f"⚠️  Failed to create request for {employee_id}")
            else:
                print(f"⚠️  Failed to authenticate {employee_id}")
        
        print(f"📊 Created {created_count} sample requests")
        return True
    
    def create_sample_vehicles_and_drivers(self):
        """Create sample vehicles and drivers"""
        print("\n🚗 Creating sample vehicles and drivers...")
        
        # Note: This would require additional API endpoints for vehicles and drivers
        # For now, we'll just print what would be created
        
        sample_vehicles = [
            {
                "make": "Tata",
                "model": "Sumo",
                "year": 2020,
                "license_plate": "KA01AB1234",
                "capacity": 7,
                "fuel_type": "Diesel",
                "is_active": True
            },
            {
                "make": "Mahindra",
                "model": "Bolero",
                "year": 2019,
                "license_plate": "KA02CD5678",
                "capacity": 8,
                "fuel_type": "Diesel",
                "is_active": True
            },
            {
                "make": "Toyota",
                "model": "Innova",
                "year": 2021,
                "license_plate": "KA03EF9012",
                "capacity": 7,
                "fuel_type": "Diesel",
                "is_active": True
            }
        ]
        
        sample_drivers = [
            {
                "employee_id": "HAL201",
                "license_number": "DL123456789",
                "license_expiry": "2025-12-31",
                "experience_years": 10,
                "is_available": True
            },
            {
                "employee_id": "HAL202",
                "license_number": "DL987654321",
                "license_expiry": "2026-06-30",
                "experience_years": 8,
                "is_available": True
            }
        ]
        
        print("📋 Sample vehicles that would be created:")
        for vehicle in sample_vehicles:
            print(f"   🚗 {vehicle['make']} {vehicle['model']} ({vehicle['license_plate']})")
        
        print("📋 Sample drivers that would be created:")
        for driver in sample_drivers:
            print(f"   👨‍✈️ {driver['employee_id']} (License: {driver['license_number']})")
        
        print("ℹ️  Vehicle and driver creation requires additional API endpoints")
        return True
    
    def generate_all_sample_data(self):
        """Generate all sample data"""
        print("🎯 HAL TRANSPORT MANAGEMENT SYSTEM - SAMPLE DATA GENERATOR")
        print("=" * 70)
        print(f"📅 Generation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        if not self.authenticate_admin():
            return False
        
        # Create sample data
        self.create_sample_users()
        self.create_sample_requests()
        self.create_sample_vehicles_and_drivers()
        
        print("\n🎉 SAMPLE DATA GENERATION COMPLETE!")
        print("=" * 50)
        print()
        print("📊 Summary:")
        print("   👥 Sample users created for different departments")
        print("   📋 Sample transport requests created")
        print("   🚗 Sample vehicles and drivers documented")
        print()
        print("🔐 Login Credentials:")
        print("   Admin: HAL001 / admin123")
        print("   Employees: HAL101-HAL105 / employee123")
        print("   Drivers: HAL201-HAL202 / transport123")
        print()
        print("🌐 Access the application:")
        print("   Frontend: http://localhost:3000")
        print("   Backend: http://localhost:8000")
        print("   API Docs: http://localhost:8000/docs")
        print()
        
        return True

def main():
    generator = SampleDataGenerator()
    return generator.generate_all_sample_data()

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
