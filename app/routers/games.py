from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import GameResult, GameStart
from app.models import Game, User, Pairing

router = APIRouter(prefix="/games", tags=["games"])


@router.post("/start")
async def start_game(game_start: GameStart, db: Session = Depends(get_db)):
    """Start a new game/match - called by external backend"""
    # Find game by id
    game = db.query(Game).filter(Game.id == game_start.id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    # Check if external_id is already set with proper MongoDB ObjectId (24 chars)
    if game.external_id and len(game.external_id) >= 24:
        raise HTTPException(status_code=400, detail="Game already has external_id")
    
    # Update external_id
    game.external_id = game_start.external_id
    
    db.commit()
    db.refresh(game)
    
    return {
        "id": game.id,
        "external_id": game.external_id,
        "pairing_id": game.pairing_id,
        "round_number": game.round_number,
        "winner_id": game.winner_id,
        "is_finished": game.is_finished
    }


@router.post("/result")
async def receive_game_result(game_result: GameResult, db: Session = Depends(get_db)):
    """Receive match result from external backend"""
    print(f"🎮 Game Result Request: external_id={game_result.external_id}, winner_external_id={game_result.winner_external_id}")
    
    # Find game by external_id
    game = db.query(Game).filter(Game.external_id == game_result.external_id).first()
    if not game:
        print(f"❌ Game not found: {game_result.external_id}")
        raise HTTPException(status_code=404, detail="Game not found")
    
    # Check if game is already finished
    if game.is_finished:
        print(f"❌ Game already finished: {game_result.external_id}")
        raise HTTPException(status_code=400, detail="Game already finished")
    
    # Find winner by external_id
    winner = db.query(User).filter(User.external_id == game_result.winner_external_id).first()
    if not winner:
        print(f"❌ Winner not found: {game_result.winner_external_id}")
        raise HTTPException(status_code=404, detail="Winner not found")
    
    # Get the pairing
    pairing = game.pairing
    print(f"🔍 Pairing players: player1_id={pairing.player1_id}, player2_id={pairing.player2_id}")
    print(f"🔍 Winner: id={winner.id}, external_id={winner.external_id}")
    
    # Verify winner is part of this pairing
    if winner.id not in [pairing.player1_id, pairing.player2_id]:
        print(f"❌ Winner {winner.id} not in pairing [{pairing.player1_id}, {pairing.player2_id}]")
        raise HTTPException(status_code=400, detail="Winner is not part of this game")
    
    # Update game
    game.winner_id = winner.id
    game.is_finished = True
    
    # Update pairing win counts
    if winner.id == pairing.player1_id:
        pairing.player1_wins += 1
    else:
        pairing.player2_wins += 1
    
    db.commit()
    db.refresh(game)
    db.refresh(pairing)
    
    result = {
        "id": game.id,
        "external_id": game.external_id,
        "pairing_id": game.pairing_id,
        "round_number": game.round_number,
        "winner_id": game.winner_id,
        "is_finished": game.is_finished,
        "pairing_updated": {
            "player1_wins": pairing.player1_wins,
            "player2_wins": pairing.player2_wins
        }
    }
    
    print(f"✅ Game result success: {result}")
    return result


@router.get("/{game_id}")
async def get_game(game_id: int, db: Session = Depends(get_db)):
    """Get game details"""
    pass


@router.get("/external/{external_id}")
async def get_game_by_external_id(external_id: str, db: Session = Depends(get_db)):
    """Get game by external ID"""
    pass