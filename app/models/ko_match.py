from sqlmodel import SQLModel, Field
from typing import Optional

class KoMatch(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tournament_id: int = Field(foreign_key="tournament.id")
    round: str  # e.g. "Viertelfinale", "Halbfinale", "Finale", "Kleines Finale"
    label: str  # z.B. "C1", "D2", "F", "K"
    player1_id: Optional[int] = Field(foreign_key="player.id")
    player2_id: Optional[int] = Field(foreign_key="player.id")
    sets_player1: Optional[int] = 0
    sets_player2: Optional[int] = 0
    best_of: int = 5
    completed: bool = False
