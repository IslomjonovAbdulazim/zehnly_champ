from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db

router = APIRouter(prefix="/championships", tags=["championships"])


@router.get("/")
async def list_championships(db: Session = Depends(get_db)):
    """Get all championships"""
    pass


@router.get("/{championship_id}")
async def get_championship(championship_id: int, db: Session = Depends(get_db)):
    """Get championship details"""
    pass