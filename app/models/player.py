from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from app.models.tournament_participation import TournamentParticipantLink

class Player(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    nickname: Optional[str] = None
    active: bool = True
    tournaments: List["Tournament"] = Relationship(
        back_populates="players",
        link_model=TournamentParticipantLink
    )
