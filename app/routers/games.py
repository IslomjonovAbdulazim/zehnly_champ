from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db

router = APIRouter(prefix="/games", tags=["games"])


@router.post("/start")
async def start_game(db: Session = Depends(get_db)):
    """Start a new game/match - called by external backend"""
    pass


@router.post("/result")
async def receive_game_result(db: Session = Depends(get_db)):
    """Receive match result from external backend"""
    pass


@router.get("/{game_id}")
async def get_game(game_id: int, db: Session = Depends(get_db)):
    """Get game details"""
    pass


@router.get("/external/{external_id}")
async def get_game_by_external_id(external_id: str, db: Session = Depends(get_db)):
    """Get game by external ID"""
    pass