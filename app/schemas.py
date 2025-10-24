from pydantic import BaseModel


class AdminLogin(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class ChampionshipCreate(BaseModel):
    name: str


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