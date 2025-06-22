from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, Session
from typing import List
from app.db.database import get_session
from app.models.tournament import Tournament
from app.models.player import Player
from app.models.tournament_participation import TournamentParticipantLink

router = APIRouter(prefix="/participation", tags=["Teilnahmen"])

@router.post("/assign/{tournament_id}", response_model=List[int])
def assign_players_to_tournament(tournament_id: int, player_ids: List[int], session: Session = Depends(get_session)):
    tournament = session.get(Tournament, tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Turnier nicht gefunden")

    players = session.exec(select(Player).where(Player.id.in_(player_ids))).all()
    if not players:
        raise HTTPException(status_code=404, detail="Keine gültigen Spieler gefunden")

    tournament.players = players
    session.add(tournament)
    session.commit()
    return [p.id for p in players]

@router.get("/{tournament_id}", response_model=List[int])
def get_players_in_tournament(tournament_id: int, session: Session = Depends(get_session)):
    tournament = session.get(Tournament, tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Turnier nicht gefunden")
    return [p.id for p in tournament.players]

@router.delete("/remove/{tournament_id}/{player_id}")
def remove_player_from_tournament(tournament_id: int, player_id: int, session: Session = Depends(get_session)):
    tournament = session.get(Tournament, tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Turnier nicht gefunden")

    tournament.players = [p for p in tournament.players if p.id != player_id]
    session.add(tournament)
    session.commit()
    return {"detail": f"Spieler {player_id} entfernt"}
