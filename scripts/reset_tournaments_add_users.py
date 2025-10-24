#!/usr/bin/env python3
"""
Script to remove all existing tournaments/championships and keep only three specific users.
This script will:
1. Delete all championships (and related data through cascade)
2. Remove all existing users except the three specified ones
3. Keep only three users: Shoxruxmirzo, abduazim, and Simulator

Usage: python scripts/reset_tournaments_add_users.py
"""

import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database import SessionLocal
from app.models import Championship, User, Game, Pairing, UserChampionship


def reset_tournaments_and_add_users():
    """Remove all tournaments and keep only three specific users"""
    db = SessionLocal()
    
    # Define the three users to keep in the system
    users_to_keep = [
        {"external_id": "68ada2c655294fd9596e9e41", "fullname": "Shoxruxmirzo", "photo_url": None},
        {"external_id": "68f766eb9702adf7d0a0634a", "fullname": "abduazim", "photo_url": None},
        {"external_id": "68e53d2db1e331166a013e92", "fullname": "Simulator", "photo_url": None},
    ]
    
    try:
        print("🗑️  Removing all existing tournaments/championships...")
        
        # Delete in correct order to avoid foreign key violations
        # 1. First delete games
        games_count = db.query(Game).count()
        if games_count > 0:
            db.query(Game).delete()
            print(f"   Deleted {games_count} games")
        
        # 2. Then delete pairings
        pairings_count = db.query(Pairing).count()
        if pairings_count > 0:
            db.query(Pairing).delete()
            print(f"   Deleted {pairings_count} pairings")
        
        # 3. Then delete user championships
        user_championships_count = db.query(UserChampionship).count()
        if user_championships_count > 0:
            db.query(UserChampionship).delete()
            print(f"   Deleted {user_championships_count} user championships")
        
        # 4. Finally delete championships
        championships_count = db.query(Championship).count()
        if championships_count > 0:
            db.query(Championship).delete()
            print(f"   Deleted {championships_count} championships")
        
        if championships_count == 0 and pairings_count == 0 and games_count == 0 and user_championships_count == 0:
            print("   No tournament data found to delete")
        
        print("\n👥 Removing all existing users...")
        
        # Get list of external_ids to keep
        external_ids_to_keep = [user["external_id"] for user in users_to_keep]
        
        # Delete all users except the ones we want to keep
        users_to_delete = db.query(User).filter(~User.external_id.in_(external_ids_to_keep)).all()
        deleted_count = len(users_to_delete)
        
        for user in users_to_delete:
            db.delete(user)
        
        if deleted_count > 0:
            print(f"   Deleted {deleted_count} existing users")
        else:
            print("   No users found to delete")
        
        print("\n👥 Processing required users...")
        
        created_count = 0
        updated_count = 0
        
        for user_data in users_to_keep:
            # Check if user already exists
            existing_user = db.query(User).filter(User.external_id == user_data["external_id"]).first()
            
            if existing_user:
                # Update existing user
                existing_user.fullname = user_data["fullname"]
                existing_user.photo_url = user_data["photo_url"]
                updated_count += 1
                print(f"🔄 Updated existing user: {user_data['fullname']} ({user_data['external_id']})")
            else:
                # Create new user
                user = User(
                    external_id=user_data["external_id"],
                    fullname=user_data["fullname"],
                    photo_url=user_data["photo_url"]
                )
                db.add(user)
                created_count += 1
                print(f"✅ Created new user: {user_data['fullname']} ({user_data['external_id']})")
        
        # Commit all changes
        db.commit()
        
        print(f"\n🎉 Script completed successfully!")
        print(f"   Removed all tournaments/championships")
        print(f"   Removed all other users")
        print(f"   Created: {created_count} new users")
        print(f"   Updated: {updated_count} existing users")
        print(f"   Total users in system: {len(users_to_keep)}")
        
    except Exception as e:
        print(f"❌ Error during operation: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    print("🚀 Starting tournament reset and user setup...")
    reset_tournaments_and_add_users()