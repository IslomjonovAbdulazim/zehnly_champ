from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import User, Championship, UserChampionship, Pairing, Game

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/{user_id}")
async def get_user(user_id: str, db: Session = Depends(get_db)):
    """Get user details"""
    pass


@router.get("/{user_id}/tournaments")
async def get_user_tournaments(user_id: str, db: Session = Depends(get_db)):
    """Get user tournament status"""
    # Find user by external_id
    user = db.query(User).filter(User.external_id == user_id).first()
    if not user:
        return None
    
    # Get active championship
    active_championship = db.query(Championship).filter(Championship.status == "active").first()
    if not active_championship:
        return None
    
    # Check if user is in this championship
    user_championship = db.query(UserChampionship).filter(
        UserChampionship.user_id == user.id,
        UserChampionship.championship_id == active_championship.id
    ).first()
    
    # If user is not in championship, return championship info without opponent
    if not user_championship:
        return {
            "user": {
                "id": user.id,
                "external_id": user.external_id
            },
            "championship": {
                "id": active_championship.id,
                "name": active_championship.name,
                "status": active_championship.status
            },
            "user_status": None,
            "wins": 0,
            "losses": 0
        }
    
    # User is in championship, get opponent and stats
    # Find pairing for this user
    pairing = db.query(Pairing).filter(
        Pairing.championship_id == active_championship.id,
        ((Pairing.player1_id == user.id) | (Pairing.player2_id == user.id))
    ).first()
    
    # Get current round number - use pairing-specific max round if pairing exists
    if pairing:
        current_round = db.query(func.max(Game.round_number)).filter(
            Game.pairing_id == pairing.id
        ).scalar() or 1
    else:
        # Fallback to championship-wide max round if no pairing
        current_round = db.query(func.max(Game.round_number)).filter(
            Game.pairing_id.in_(
                db.query(Pairing.id).filter(Pairing.championship_id == active_championship.id)
            )
        ).scalar() or 1
    
    # Debug logging
    print(f"🔍 User {user.id} in championship {active_championship.id}")
    print(f"🔍 Current round for user: {current_round}")
    if pairing:
        print(f"🔍 Found pairing {pairing.id}: player1={pairing.player1_id}, player2={pairing.player2_id}")
        print(f"🔍 Pairing wins: player1_wins={pairing.player1_wins}, player2_wins={pairing.player2_wins}")
    else:
        print(f"❌ No pairing found for user {user.id} in championship {active_championship.id}")
    
    result = {
        "user": {
            "id": user.id,
            "external_id": user.external_id
        },
        "championship": {
            "id": active_championship.id,
            "name": active_championship.name,
            "status": active_championship.status
        },
        "user_status": user_championship.status,
        "current_round": current_round,
        "wins": 0,
        "losses": 0
    }
    
    # Add opponent and win/loss stats if pairing exists
    if pairing:
        # Determine opponent
        if pairing.player1_id == user.id:
            opponent = pairing.player2
            result["wins"] = pairing.player1_wins
            result["losses"] = pairing.player2_wins
        else:
            opponent = pairing.player1
            result["wins"] = pairing.player2_wins
            result["losses"] = pairing.player1_wins
        
        # Add opponent info
        result["opponent"] = {
            "id": opponent.id,
            "external_id": opponent.external_id,
            "fullname": opponent.fullname,
            "photo_url": opponent.photo_url
        }
        
        # Get current game status
        current_game = db.query(Game).filter(
            Game.pairing_id == pairing.id,
            Game.round_number == current_round
        ).first()
        
        if current_game:
            result["game_status"] = "finished" if current_game.is_finished else "pending"
            result["game_id"] = current_game.id
        else:
            result["game_status"] = "not_started"
            result["game_id"] = None
    
    return result


@router.get("/{user_id}/games")
async def get_user_games(user_id: str, db: Session = Depends(get_db)):
    """Get user game history"""
    pass