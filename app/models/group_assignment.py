from sqlmodel import SQLModel, Field
from typing import Optional, List

class GroupAssignment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tournament_id: int = Field(foreign_key="tournament.id")
    player_id: int = Field(foreign_key="player.id")
    group: str  # "A", "B", "C", "D"

class GroupAssignmentInput(SQLModel):
    A: List[int] = []
    B: List[int] = []
    C: List[int] = []
    D: List[int] = []
