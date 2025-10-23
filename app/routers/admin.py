from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.auth import verify_admin_credentials, create_access_token, get_current_admin
from app.schemas import AdminLogin, Token, ChampionshipCreate, UserCreate, GeneratePairings
from app.models import Championship, User, UserChampionship, Pairing, Game
import random

router = APIRouter(prefix="/admin", tags=["admin"])


# Authentication
@router.post("/login", response_model=Token)
async def admin_login(admin_data: AdminLogin):
    """Admin login endpoint"""
    if not verify_admin_credentials(admin_data.email, admin_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=60)
    access_token = create_access_token(
        data={"sub": admin_data.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# Championship Management
@router.post("/championships")
async def create_championship(
    championship: ChampionshipCreate, 
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Create new championship"""
    db_championship = Championship(name=championship.name)
    db.add(db_championship)
    db.commit()
    db.refresh(db_championship)
    return db_championship


@router.get("/championships")
async def list_championships(
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """List all championships"""
    championships = db.query(Championship).all()
    result = []
    
    for champ in championships:
        # Get current round (max round number from games)
        current_round = db.query(func.max(Game.round_number)).filter(
            Game.pairing_id.in_(
                db.query(Pairing.id).filter(Pairing.championship_id == champ.id)
            )
        ).scalar() or 0
        
        # Count users, pairings, games
        user_count = db.query(UserChampionship).filter(UserChampionship.championship_id == champ.id).count()
        pairing_count = db.query(Pairing).filter(Pairing.championship_id == champ.id).count()
        total_games = db.query(Game).join(Pairing).filter(Pairing.championship_id == champ.id).count()
        finished_games = db.query(Game).join(Pairing).filter(
            Pairing.championship_id == champ.id, 
            Game.is_finished == True
        ).count()
        
        result.append({
            "id": champ.id,
            "name": champ.name,
            "status": champ.status,
            "current_round": current_round,
            "user_count": user_count,
            "pairing_count": pairing_count,
            "total_games": total_games,
            "finished_games": finished_games
        })
    
    return result


# User Management
@router.post("/users")
async def create_user(
    user: UserCreate, 
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Create new user"""
    # Check if external_id already exists
    existing_user = db.query(User).filter(User.external_id == user.external_id).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this external_id already exists")
    
    db_user = User(
        external_id=user.external_id,
        fullname=user.fullname,
        photo_url=user.photo_url
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get("/users")
async def list_users(
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """List all users"""
    return db.query(User).all()


# Pairing Management
@router.post("/championships/{championship_id}/generate-pairings")
async def generate_pairings(
    championship_id: int,
    pairing_data: GeneratePairings,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Generate pairings for championship"""
    # Verify championship exists
    championship = db.query(Championship).filter(Championship.id == championship_id).first()
    if not championship:
        raise HTTPException(status_code=404, detail="Championship not found")
    
    # Get users
    users = db.query(User).filter(User.id.in_(pairing_data.user_ids)).all()
    if len(users) != len(pairing_data.user_ids):
        raise HTTPException(status_code=400, detail="Some users not found")
    
    # Add users to championship
    for user in users:
        existing = db.query(UserChampionship).filter(
            UserChampionship.user_id == user.id,
            UserChampionship.championship_id == championship_id
        ).first()
        if not existing:
            user_champ = UserChampionship(user_id=user.id, championship_id=championship_id)
            db.add(user_champ)
    
    # Generate random pairings
    user_list = list(users)
    random.shuffle(user_list)
    
    generated_pairings = []
    unpaired_users = []
    
    for i in range(0, len(user_list) - 1, 2):
        player1 = user_list[i]
        player2 = user_list[i + 1]
        
        pairing = Pairing(
            championship_id=championship_id,
            player1_id=player1.id,
            player2_id=player2.id
        )
        db.add(pairing)
        db.flush()  # Get the ID
        
        generated_pairings.append({
            "id": pairing.id,
            "championship_id": championship_id,
            "player1": {"id": player1.id, "fullname": player1.fullname},
            "player2": {"id": player2.id, "fullname": player2.fullname},
            "status": pairing.status
        })
    
    # Handle odd number of users
    if len(user_list) % 2 == 1:
        unpaired_user = user_list[-1]
        unpaired_users.append({
            "id": unpaired_user.id,
            "fullname": unpaired_user.fullname,
            "reason": "Odd number of users"
        })
    
    db.commit()
    
    return {
        "generated_pairings": generated_pairings,
        "unpaired_users": unpaired_users
    }


# Pairing Viewing  
@router.get("/championships/{championship_id}/pairings")
async def get_championship_pairings(
    championship_id: int,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Get all pairings with their scores for championship"""
    championship = db.query(Championship).filter(Championship.id == championship_id).first()
    if not championship:
        raise HTTPException(status_code=404, detail="Championship not found")
    
    pairings = db.query(Pairing).filter(Pairing.championship_id == championship_id).all()
    
    result = []
    for pairing in pairings:
        total_games = pairing.player1_wins + pairing.player2_wins
        
        result.append({
            "id": pairing.id,
            "player1": {
                "id": pairing.player1.id,
                "fullname": pairing.player1.fullname,
                "photo_url": pairing.player1.photo_url
            },
            "player2": {
                "id": pairing.player2.id,
                "fullname": pairing.player2.fullname,
                "photo_url": pairing.player2.photo_url
            },
            "player1_wins": pairing.player1_wins,
            "player2_wins": pairing.player2_wins,
            "total_games": total_games,
            "status": pairing.status
        })
    
    return result


# Round Management
@router.post("/championships/{championship_id}/advance-round")
async def advance_round(
    championship_id: int, 
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Advance championship to next round - forfeit pending games, create new round"""
    # Verify championship exists
    championship = db.query(Championship).filter(Championship.id == championship_id).first()
    if not championship:
        raise HTTPException(status_code=404, detail="Championship not found")
    
    # Get current round
    current_round = db.query(func.max(Game.round_number)).filter(
        Game.pairing_id.in_(
            db.query(Pairing.id).filter(Pairing.championship_id == championship_id)
        )
    ).scalar() or 0
    
    next_round = current_round + 1
    
    # Forfeit pending games in current round
    pending_games = db.query(Game).join(Pairing).filter(
        Pairing.championship_id == championship_id,
        Game.round_number == current_round,
        Game.is_finished == False
    ).all()
    
    forfeited_count = 0
    for game in pending_games:
        game.is_finished = True
        game.winner_id = None  # Both players lose
        forfeited_count += 1
    
    # Create new games for next round
    pairings = db.query(Pairing).filter(
        Pairing.championship_id == championship_id,
        Pairing.status == "active"
    ).all()
    
    new_games_count = 0
    for pairing in pairings:
        new_game = Game(
            external_id=f"game_{championship_id}_{pairing.id}_{next_round}",
            pairing_id=pairing.id,
            round_number=next_round
        )
        db.add(new_game)
        new_games_count += 1
    
    db.commit()
    
    return {
        "championship_id": championship_id,
        "previous_round": current_round,
        "current_round": next_round,
        "forfeited_games": forfeited_count,
        "new_games_created": new_games_count,
        "message": f"Advanced to round {next_round}. {forfeited_count} pending games marked as forfeited (both players lose)."
    }


# Statistics
@router.get("/championships/{championship_id}/stats")
async def get_championship_stats(
    championship_id: int, 
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Get championship statistics"""
    championship = db.query(Championship).filter(Championship.id == championship_id).first()
    if not championship:
        raise HTTPException(status_code=404, detail="Championship not found")
    
    # User stats
    total_users = db.query(UserChampionship).filter(UserChampionship.championship_id == championship_id).count()
    active_users = db.query(UserChampionship).filter(
        UserChampionship.championship_id == championship_id,
        UserChampionship.status == "active"
    ).count()
    eliminated_users = total_users - active_users
    
    # Pairing stats
    total_pairings = db.query(Pairing).filter(Pairing.championship_id == championship_id).count()
    active_pairings = db.query(Pairing).filter(
        Pairing.championship_id == championship_id,
        Pairing.status == "active"
    ).count()
    
    # Game stats
    total_games = db.query(Game).join(Pairing).filter(Pairing.championship_id == championship_id).count()
    finished_games = db.query(Game).join(Pairing).filter(
        Pairing.championship_id == championship_id,
        Game.is_finished == True
    ).count()
    pending_games = total_games - finished_games
    
    # Games by round
    games_by_round = {}
    rounds_data = db.query(Game.round_number, func.count(Game.id)).join(Pairing).filter(
        Pairing.championship_id == championship_id
    ).group_by(Game.round_number).all()
    
    for round_num, count in rounds_data:
        games_by_round[str(round_num)] = count
    
    
    return {
        "championship": {
            "id": championship.id,
            "name": championship.name,
            "status": championship.status
        },
        "users": {
            "total": total_users,
            "active": active_users,
            "eliminated": eliminated_users
        },
        "pairings": {
            "total": total_pairings,
            "active": active_pairings,
            "eliminated": total_pairings - active_pairings
        },
        "games": {
            "total": total_games,
            "finished": finished_games,
            "pending": pending_games,
            "by_round": games_by_round
        }
    }