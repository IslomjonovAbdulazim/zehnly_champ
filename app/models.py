from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint, CheckConstraint, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from datetime import datetime

Base = declarative_base()


class ChampionshipStatus(PyEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class PairingStatus(PyEnum):
    ACTIVE = "active"
    ELIMINATED = "eliminated"


class Championship(Base):
    __tablename__ = "championships"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    status = Column(String, nullable=False, default=ChampionshipStatus.ACTIVE.value)
    start_date = Column(DateTime, nullable=True, default=datetime(2025, 10, 29, 19, 0))
    
    # Relationships
    pairings = relationship("Pairing", back_populates="championship", cascade="all, delete-orphan")
    user_championships = relationship("UserChampionship", back_populates="championship", cascade="all, delete-orphan")
    
    __table_args__ = (
        CheckConstraint("status IN ('active', 'inactive')", name="check_championship_status"),
    )


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, unique=True, nullable=False, index=True)
    fullname = Column(String, nullable=False)
    photo_url = Column(String, nullable=True)
    
    # Relationships
    user_championships = relationship("UserChampionship", back_populates="user")


class UserChampionship(Base):
    __tablename__ = "user_championships"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    championship_id = Column(Integer, ForeignKey("championships.id"), nullable=False)
    status = Column(String, nullable=False, default=PairingStatus.ACTIVE.value)
    
    # Relationships
    user = relationship("User", back_populates="user_championships")
    championship = relationship("Championship", back_populates="user_championships")
    
    __table_args__ = (
        UniqueConstraint("user_id", "championship_id", name="unique_user_championship"),
        CheckConstraint("status IN ('active', 'eliminated')", name="check_user_championship_status"),
    )


class Pairing(Base):
    __tablename__ = "pairings"
    
    id = Column(Integer, primary_key=True, index=True)
    championship_id = Column(Integer, ForeignKey("championships.id"), nullable=False)
    player1_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    player2_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    player1_wins = Column(Integer, default=0)  # Total wins for player1 in this pairing
    player2_wins = Column(Integer, default=0)  # Total wins for player2 in this pairing
    status = Column(String, nullable=False, default=PairingStatus.ACTIVE.value)
    
    # Relationships
    championship = relationship("Championship", back_populates="pairings")
    player1 = relationship("User", foreign_keys=[player1_id])
    player2 = relationship("User", foreign_keys=[player2_id])
    games = relationship("Game", back_populates="pairing", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint("championship_id", "player1_id", "player2_id", name="unique_championship_pairing"),
        CheckConstraint("player1_id != player2_id", name="check_different_players_pairing"),
        CheckConstraint("status IN ('active', 'eliminated')", name="check_pairing_status"),
    )


class Game(Base):
    __tablename__ = "games"
    
    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, unique=True, nullable=False, index=True)
    pairing_id = Column(Integer, ForeignKey("pairings.id"), nullable=False)
    round_number = Column(Integer, nullable=False)
    winner_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Winner of this game (null if not finished)
    is_finished = Column(Boolean, default=False)
    
    # Relationships
    pairing = relationship("Pairing", back_populates="games")
    winner = relationship("User", foreign_keys=[winner_id])
    
    __table_args__ = (
        CheckConstraint("round_number > 0", name="check_positive_round"),
    )