"""
Database module for NBA Predictor.
Handles SQLite database connection and schema definition.
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, Date, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from src.config import DATABASE_URL
import os
from pathlib import Path

Base = declarative_base()


class Team(Base):
    __tablename__ = "teams"
    
    team_id = Column(Integer, primary_key=True, autoincrement=True)
    team_name = Column(String(100), nullable=False, unique=True)
    abbreviation = Column(String(10), nullable=False, unique=True)
    
    # Relationships
    home_games = relationship("Game", foreign_keys="Game.home_team_id", back_populates="home_team")
    away_games = relationship("Game", foreign_keys="Game.away_team_id", back_populates="away_team")
    box_scores = relationship("TeamBoxScore", back_populates="team")


class Game(Base):
    __tablename__ = "games"
    
    game_id = Column(String(50), primary_key=True)  # e.g., "2024-01-15-LAL-BOS"
    date = Column(Date, nullable=False, index=True)
    home_team_id = Column(Integer, ForeignKey("teams.team_id"), nullable=False)
    away_team_id = Column(Integer, ForeignKey("teams.team_id"), nullable=False)
    home_score = Column(Integer, nullable=True)
    away_score = Column(Integer, nullable=True)
    season = Column(Integer, nullable=False, index=True)
    game_type = Column(String(20), default="regular")  # regular, playoff
    
    # ELO ratings (pre-game)
    home_team_pregame_elo = Column(Float, nullable=True)
    away_team_pregame_elo = Column(Float, nullable=True)
    
    # Relationships
    home_team = relationship("Team", foreign_keys=[home_team_id], back_populates="home_games")
    away_team = relationship("Team", foreign_keys=[away_team_id], back_populates="away_games")
    box_scores = relationship("TeamBoxScore", back_populates="game")
    odds = relationship("Odds", back_populates="game")


class TeamBoxScore(Base):
    __tablename__ = "team_box_scores"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(String(50), ForeignKey("games.game_id"), nullable=False, index=True)
    team_id = Column(Integer, ForeignKey("teams.team_id"), nullable=False)
    is_home = Column(Boolean, nullable=False)
    
    # Shooting
    fg = Column(Integer, default=0)  # Field goals made
    fga = Column(Integer, default=0)  # Field goals attempted
    fg_pct = Column(Float, default=0.0)  # Field goal percentage
    fg3 = Column(Integer, default=0)  # 3-pointers made
    fg3a = Column(Integer, default=0)  # 3-pointers attempted
    fg3_pct = Column(Float, default=0.0)  # 3-point percentage
    ft = Column(Integer, default=0)  # Free throws made
    fta = Column(Integer, default=0)  # Free throws attempted
    ft_pct = Column(Float, default=0.0)  # Free throw percentage
    
    # Rebounding
    orb = Column(Integer, default=0)  # Offensive rebounds
    drb = Column(Integer, default=0)  # Defensive rebounds
    trb = Column(Integer, default=0)  # Total rebounds
    
    # Other stats
    ast = Column(Integer, default=0)  # Assists
    stl = Column(Integer, default=0)  # Steals
    blk = Column(Integer, default=0)  # Blocks
    tov = Column(Integer, default=0)  # Turnovers
    pf = Column(Integer, default=0)  # Personal fouls
    pts = Column(Integer, default=0)  # Points
    plus_minus = Column(Integer, default=0)  # Plus/minus
    
    # Relationships
    game = relationship("Game", back_populates="box_scores")
    team = relationship("Team", back_populates="box_scores")


class Odds(Base):
    __tablename__ = "odds"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(String(50), ForeignKey("games.game_id"), nullable=False, index=True)
    bookmaker = Column(String(50), nullable=False)
    
    # Spread
    home_team_spread = Column(Float, nullable=True)
    home_team_spread_odds = Column(Integer, nullable=True)  # e.g., -110
    away_team_spread = Column(Float, nullable=True)
    away_team_spread_odds = Column(Integer, nullable=True)
    
    # Moneyline
    home_team_moneyline = Column(Integer, nullable=True)  # e.g., -150
    away_team_moneyline = Column(Integer, nullable=True)  # e.g., +130
    
    # Totals
    over_under_total = Column(Float, nullable=True)
    over_odds = Column(Integer, nullable=True)
    under_odds = Column(Integer, nullable=True)
    
    # Timestamp
    fetched_at = Column(Date, server_default=func.now())
    
    # Relationships
    game = relationship("Game", back_populates="odds")


def get_engine():
    """Create and return SQLAlchemy engine."""
    # Ensure data directory exists
    db_path = DATABASE_URL.replace("sqlite:///", "")
    if db_path.startswith("./"):
        # Resolve relative to project root (3 levels up from this file)
        project_root = Path(__file__).parent.parent.parent
        db_path = project_root / db_path[2:]
    else:
        db_path = Path(db_path)
    
    # Create parent directory if it doesn't exist
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Use absolute path for SQLite
    absolute_db_path = str(db_path.absolute())
    db_url = f"sqlite:///{absolute_db_path}"
    
    engine = create_engine(db_url, echo=False)
    return engine


def get_session():
    """Create and return a database session."""
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()


def init_database():
    """Initialize the database by creating all tables."""
    engine = get_engine()
    Base.metadata.create_all(engine)
    print("Database initialized successfully.")


def get_db_connection():
    """Dependency for FastAPI to get database session."""
    db = get_session()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    init_database()

