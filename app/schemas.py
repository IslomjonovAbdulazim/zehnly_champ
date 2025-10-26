from pydantic import BaseModel, validator
from datetime import datetime
from typing import Optional


class AdminLogin(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class ChampionshipCreate(BaseModel):
    name: str
    start_date: Optional[datetime] = None


class UserCreate(BaseModel):
    external_id: str
    fullname: str
    photo_url: str = None


class GeneratePairings(BaseModel):
    user_ids: list[int]


class GameResult(BaseModel):
    external_id: str
    winner_external_id: str


class GameStart(BaseModel):
    id: int
    external_id: str


class ChampionshipStatusUpdate(BaseModel):
    status: str
    
    @validator('status')
    def validate_status(cls, v):
        if v not in ['active', 'inactive']:
            raise ValueError('Status must be either "active" or "inactive"')
        return v