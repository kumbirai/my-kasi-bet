"""
Script to create initial admin user.

This script creates an admin user in the database with hashed password.
Usage: python scripts/create_admin.py
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.models.admin import AdminRole, AdminUser
from app.utils.security import get_password_hash


def create_admin_user(
    email: str,
    password: str,
    full_name: str,
    role: AdminRole = AdminRole.ADMIN,
) -> None:
    """
    Create a new admin user.

    Args:
        email: Admin email address
        password: Plain text password (will be hashed)
        full_name: Full name of admin
        role: Admin role (default: ADMIN)

    Raises:
        Exception: If creation fails
    """
    db = SessionLocal()

    try:
        # Check if user already exists
        existing = db.query(AdminUser).filter(AdminUser.email == email).first()
        if existing:
            print(f"❌ Admin user with email {email} already exists")
            return

        # Create new admin user
        admin = AdminUser(
            email=email,
            hashed_password=get_password_hash(password),
            full_name=full_name,
            role=role,
            is_active=True,
        )

        db.add(admin)
        db.commit()
        db.refresh(admin)

        print(f"✅ Admin user created successfully")
        print(f"   Email: {email}")
        print(f"   Name: {full_name}")
        print(f"   Role: {role.value}")
        print(f"   ID: {admin.id}")

    except Exception as e:
        db.rollback()
        print(f"❌ Error creating admin user: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("Creating initial admin user...")
    create_admin_user(
        email="admin@mykasibets.com",
        password="Password123@",  # Change this!
        full_name="Super Admin",
        role=AdminRole.SUPER_ADMIN,
    )
