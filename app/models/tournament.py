from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import date
from app.models.tournament_participation import TournamentParticipantLink

class TournamentBase(SQLModel):
    name: str
    date: date
    location: Optional[str] = None
    num_groups: Optional[int] = 4
    is_finished: bool = False

class Tournament(TournamentBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    players: List["Player"] = Relationship(
        back_populates="tournaments",
        link_model=TournamentParticipantLink
    )

class TournamentRead(TournamentBase):
    id: int
    players: List[int] = []

class TournamentCreate(TournamentBase):
    players: List[int] = []
