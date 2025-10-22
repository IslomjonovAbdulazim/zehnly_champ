from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/")
async def create_user(db: Session = Depends(get_db)):
    """Create new user"""
    pass


@router.get("/")
async def list_users(db: Session = Depends(get_db)):
    """Get all users"""
    pass


@router.get("/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user details"""
    pass


@router.put("/{user_id}")
async def update_user(user_id: int, db: Session = Depends(get_db)):
    """Update user"""
    pass


@router.delete("/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Delete user"""
    pass


@router.get("/{user_id}/championships")
async def get_user_championships(user_id: int, db: Session = Depends(get_db)):
    """Get all championships for user"""
    pass


@router.get("/{user_id}/pairings")
async def get_user_pairings(user_id: int, db: Session = Depends(get_db)):
    """Get all pairings for user"""
    pass