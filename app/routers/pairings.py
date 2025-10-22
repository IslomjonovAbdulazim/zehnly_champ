from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db

router = APIRouter(prefix="/pairings", tags=["pairings"])


@router.get("/{pairing_id}")
async def get_pairing(pairing_id: int, db: Session = Depends(get_db)):
    """Get specific pairing details"""
    pass