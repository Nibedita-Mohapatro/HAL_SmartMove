#!/usr/bin/env python3
"""
Database setup script for HAL Transport Management System
"""

import sys
import os
from datetime import date

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import engine, SessionLocal, init_db
from app.models.user import User, UserRole
from app.models.vehicle import Vehicle, VehicleType, FuelType
from app.models.driver import Driver
from app.auth import get_password_hash


def create_initial_users(db: Session):
    """Create initial users for the system"""
    
    # Check if users already exist
    existing_users = db.query(User).count()
    if existing_users > 0:
        print("Users already exist, skipping user creation...")
        return
    
    # Create super admin
    super_admin = User(
        employee_id="HAL001",
        email="admin@hal.co.in",
        password_hash=get_password_hash("admin123"),
        first_name="System",
        last_name="Administrator",
        phone="+91-9876543210",
        department="IT",
        designation="System Administrator",
        role=UserRole.SUPER_ADMIN
    )
    
    # Create transport admin
    transport_admin = User(
        employee_id="HAL002",
        email="transport@hal.co.in",
        password_hash=get_password_hash("transport123"),
        first_name="Transport",
        last_name="Manager",
        phone="+91-9876543211",
        department="Transport",
        designation="Transport Manager",
        role=UserRole.ADMIN
    )
    
    # Create sample employee
    employee = User(
        employee_id="HAL003",
        email="john.doe@hal.co.in",
        password_hash=get_password_hash("employee123"),
        first_name="John",
        last_name="Doe",
        phone="+91-9876543212",
        department="Engineering",
        designation="Senior Engineer",
        role=UserRole.EMPLOYEE
    )
    
    db.add_all([super_admin, transport_admin, employee])
    db.commit()
    
    print("✅ Initial users created successfully!")
    print("Super Admin: HAL001 / admin123")
    print("Transport Admin: HAL002 / transport123")
    print("Employee: HAL003 / employee123")


def create_initial_vehicles(db: Session):
    """Create initial vehicles for the system"""
    
    # Check if vehicles already exist
    existing_vehicles = db.query(Vehicle).count()
    if existing_vehicles > 0:
        print("Vehicles already exist, skipping vehicle creation...")
        return
    
    vehicles = [
        Vehicle(
            vehicle_number="KA01AB1234",
            vehicle_type=VehicleType.BUS,
            capacity=40,
            fuel_type=FuelType.DIESEL,
            model="Tata Starbus",
            year_of_manufacture=2020,
            insurance_expiry=date(2024, 12, 31),
            fitness_certificate_expiry=date(2024, 6, 30),
            current_location="HAL Main Gate"
        ),
        Vehicle(
            vehicle_number="KA01CD5678",
            vehicle_type=VehicleType.CAR,
            capacity=4,
            fuel_type=FuelType.PETROL,
            model="Maruti Suzuki Dzire",
            year_of_manufacture=2021,
            insurance_expiry=date(2024, 10, 15),
            fitness_certificate_expiry=date(2024, 4, 15),
            current_location="HAL Parking"
        ),
        Vehicle(
            vehicle_number="KA01EF9012",
            vehicle_type=VehicleType.VAN,
            capacity=12,
            fuel_type=FuelType.DIESEL,
            model="Mahindra Bolero",
            year_of_manufacture=2019,
            insurance_expiry=date(2024, 8, 20),
            fitness_certificate_expiry=date(2024, 2, 20),
            current_location="HAL Workshop"
        )
    ]
    
    db.add_all(vehicles)
    db.commit()
    
    print("✅ Initial vehicles created successfully!")


def create_initial_drivers(db: Session):
    """Create initial drivers for the system"""
    
    # Check if drivers already exist
    existing_drivers = db.query(Driver).count()
    if existing_drivers > 0:
        print("Drivers already exist, skipping driver creation...")
        return
    
    drivers = [
        Driver(
            employee_id="DRV001",
            license_number="KA0120230001",
            license_expiry=date(2025, 12, 31),
            phone="+91-9876543220",
            first_name="Ravi",
            last_name="Kumar",
            experience_years=10
        ),
        Driver(
            employee_id="DRV002",
            license_number="KA0120230002",
            license_expiry=date(2025, 8, 15),
            phone="+91-9876543221",
            first_name="Suresh",
            last_name="Singh",
            experience_years=8
        ),
        Driver(
            employee_id="DRV003",
            license_number="KA0120230003",
            license_expiry=date(2025, 10, 30),
            phone="+91-9876543222",
            first_name="Prakash",
            last_name="Sharma",
            experience_years=12
        )
    ]
    
    db.add_all(drivers)
    db.commit()
    
    print("✅ Initial drivers created successfully!")


def main():
    """Main setup function"""
    print("🚀 Setting up HAL Transport Management System Database...")
    
    try:
        # Initialize database tables
        print("📊 Creating database tables...")
        init_db()
        print("✅ Database tables created successfully!")
        
        # Create database session
        db = SessionLocal()
        
        try:
            # Create initial data
            create_initial_users(db)
            create_initial_vehicles(db)
            create_initial_drivers(db)
            
            print("\n🎉 Database setup completed successfully!")
            print("\n📋 You can now:")
            print("1. Start the backend server: python main.py")
            print("2. Access API docs: http://localhost:8000/docs")
            print("3. Login with the credentials shown above")
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
