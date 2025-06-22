from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import select, Session
from typing import List
from app.models.tournament import Tournament, TournamentCreate, TournamentRead
from app.db.database import get_session

router = APIRouter(prefix="/tournaments", tags=["Turniere"])

@router.post("/", response_model=TournamentRead)
def create_tournament(tournament: TournamentCreate, session: Session = Depends(get_session)):
    new_tournament = Tournament(**tournament.dict())
    session.add(new_tournament)
    session.commit()
    session.refresh(new_tournament)
    return new_tournament

@router.get("/", response_model=List[TournamentRead])
def read_tournaments(session: Session = Depends(get_session)):
    return session.exec(select(Tournament)).all()

@router.get("/all", response_model=List[Tournament])
def get_all_tournaments(session: Session = Depends(get_session)):
    return session.exec(select(Tournament)).all()

@router.get("/{tournament_id}", response_model=TournamentRead)
def read_tournament(tournament_id: int, session: Session = Depends(get_session)):
    tournament = session.get(Tournament, tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Turnier nicht gefunden")
    return tournament

@router.put("/{tournament_id}", response_model=TournamentRead)
def update_tournament(tournament_id: int, updated: TournamentCreate, session: Session = Depends(get_session)):
    tournament = session.get(Tournament, tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Turnier nicht gefunden")
    for key, value in updated.dict().items():
        setattr(tournament, key, value)
    session.commit()
    session.refresh(tournament)
    return tournament

@router.delete("/{tournament_id}")
def delete_tournament(tournament_id: int, session: Session = Depends(get_session)):
    tournament = session.get(Tournament, tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Turnier nicht gefunden")
    session.delete(tournament)
    session.commit()
    return {"detail": "Turnier gelöscht"}
