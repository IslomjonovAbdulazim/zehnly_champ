from pydantic import BaseModel, EmailStr


class AdminLogin(BaseModel):
    email: EmailStr
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