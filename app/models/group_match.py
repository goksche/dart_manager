from sqlmodel import SQLModel, Field
from typing import Optional

class GroupMatch(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tournament_id: int = Field(foreign_key="tournament.id")
    group: str = Field(index=True)  # "A", "B", "C", "D"
    player1_id: int = Field(foreign_key="player.id")
    player2_id: int = Field(foreign_key="player.id")
    sets_player1: Optional[int] = 0
    sets_player2: Optional[int] = 0
    best_of: int = 3  # z. B. 3, 5, 7 oder 11
    completed: bool = False
