#!/usr/bin/env python3
"""
Create default users for HAL Transport Management System
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from passlib.context import CryptContext
from app.models.user import User, UserRole
from app.database import Base
import os
from decouple import config

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def create_default_users():
    """Create default users for the system"""
    
    # Database setup
    DATABASE_URL = config("DATABASE_URL", default="sqlite:///./hal_transport_system.db")
    engine = create_engine(DATABASE_URL)
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check if users already exist
        existing_users = db.query(User).count()
        if existing_users > 0:
            print(f"Database already has {existing_users} users. Skipping creation.")
            return
        
        # Default users to create
        default_users = [
            {
                "employee_id": "HAL001",
                "email": "admin@hal.com",
                "password": "admin123",
                "first_name": "System",
                "last_name": "Administrator",
                "phone": "+91-9999999999",
                "department": "IT",
                "designation": "System Admin",
                "role": UserRole.SUPER_ADMIN
            },
            {
                "employee_id": "HAL002",
                "email": "transport@hal.com",
                "password": "transport123",
                "first_name": "Transport",
                "last_name": "Manager",
                "phone": "+91-9999999998",
                "department": "Transport",
                "designation": "Transport Manager",
                "role": UserRole.TRANSPORT
            },
            {
                "employee_id": "HAL003",
                "email": "employee@hal.com",
                "password": "employee123",
                "first_name": "Test",
                "last_name": "Employee",
                "phone": "+91-9999999997",
                "department": "General",
                "designation": "Employee",
                "role": UserRole.EMPLOYEE
            }
        ]
        
        created_count = 0
        for user_data in default_users:
            # Hash the password
            hashed_password = hash_password(user_data.pop("password"))
            
            # Create user
            user = User(
                employee_id=user_data["employee_id"],
                email=user_data["email"],
                password_hash=hashed_password,
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                phone=user_data["phone"],
                department=user_data["department"],
                designation=user_data["designation"],
                role=user_data["role"],
                is_active=True
            )
            
            db.add(user)
            created_count += 1
            print(f"✅ Created user: {user_data['employee_id']} - {user_data['first_name']} {user_data['last_name']} ({user_data['role'].value})")
        
        # Commit all users
        db.commit()
        print(f"\n🎉 Successfully created {created_count} default users!")
        
        print("\n🔐 Default Login Credentials:")
        print("   Super Admin: HAL001 / admin123")
        print("   Transport Manager: HAL002 / transport123")
        print("   Employee: HAL003 / employee123")
        
    except Exception as e:
        print(f"❌ Error creating users: {e}")
        db.rollback()
        return False
    finally:
        db.close()
    
    return True

if __name__ == "__main__":
    success = create_default_users()
    exit(0 if success else 1)
