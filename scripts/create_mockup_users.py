#!/usr/bin/env python3
"""
Script to create 10 mockup users for testing the tournament system.
Run this script manually when you need test data.

Usage: python scripts/create_mockup_users.py
"""

import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database import SessionLocal
from app.models import User


def create_mockup_users():
    """Create 10 mockup users for testing"""
    db = SessionLocal()
    
    mockup_users = [
        {"external_id": "player_001", "fullname": "John Smith", "photo_url": "https://i.pravatar.cc/150?u=1"},
        {"external_id": "player_002", "fullname": "Sarah Johnson", "photo_url": "https://i.pravatar.cc/150?u=2"},
        {"external_id": "player_003", "fullname": "Mike Chen", "photo_url": "https://i.pravatar.cc/150?u=3"},
        {"external_id": "player_004", "fullname": "Emma Wilson", "photo_url": "https://i.pravatar.cc/150?u=4"},
        {"external_id": "player_005", "fullname": "David Brown", "photo_url": "https://i.pravatar.cc/150?u=5"},
        {"external_id": "player_006", "fullname": "Lisa Garcia", "photo_url": "https://i.pravatar.cc/150?u=6"},
        {"external_id": "player_007", "fullname": "Alex Rodriguez", "photo_url": "https://i.pravatar.cc/150?u=7"},
        {"external_id": "player_008", "fullname": "Maya Patel", "photo_url": "https://i.pravatar.cc/150?u=8"},
        {"external_id": "player_009", "fullname": "Ryan Murphy", "photo_url": "https://i.pravatar.cc/150?u=9"},
        {"external_id": "player_010", "fullname": "Sophie Kim", "photo_url": "https://i.pravatar.cc/150?u=10"},
    ]
    
    try:
        created_count = 0
        skipped_count = 0
        
        for user_data in mockup_users:
            # Check if user already exists
            existing_user = db.query(User).filter(User.external_id == user_data["external_id"]).first()
            if not existing_user:
                user = User(
                    external_id=user_data["external_id"],
                    fullname=user_data["fullname"],
                    photo_url=user_data["photo_url"]
                )
                db.add(user)
                created_count += 1
                print(f"✅ Created user: {user_data['fullname']} ({user_data['external_id']})")
            else:
                skipped_count += 1
                print(f"⏭️  Skipped existing user: {user_data['fullname']} ({user_data['external_id']})")
        
        db.commit()
        print(f"\n🎉 Mockup users script completed!")
        print(f"   Created: {created_count} users")
        print(f"   Skipped: {skipped_count} users (already existed)")
        print(f"   Total: {len(mockup_users)} users processed")
        
    except Exception as e:
        print(f"❌ Error creating mockup users: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    print("🚀 Creating mockup users for tournament system...")
    create_mockup_users()