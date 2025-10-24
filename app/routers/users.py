from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/{user_id}")
async def get_user(user_id: str, db: Session = Depends(get_db)):
    """Get user details"""
    pass


@router.get("/{user_id}/tournaments")
async def get_user_tournaments(user_id: str, db: Session = Depends(get_db)):
    """Get user tournament status"""
    pass


@router.get("/{user_id}/games")
async def get_user_games(user_id: str, db: Session = Depends(get_db)):
    """Get user game history"""
    pass