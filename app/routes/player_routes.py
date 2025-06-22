from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import select, Session
from typing import List
from app.models.player import Player
from app.db.database import get_session

router = APIRouter(prefix="/players", tags=["Spieler"])

@router.post("/", response_model=Player)
def create_player(player: Player, session: Session = Depends(get_session)):
    session.add(player)
    session.commit()
    session.refresh(player)
    return player

@router.get("/", response_model=List[Player])
def read_players(session: Session = Depends(get_session)):
    return session.exec(select(Player)).all()

@router.get("/all", response_model=List[Player])
def get_all_players(session: Session = Depends(get_session)):
    return session.exec(select(Player)).all()

@router.get("/{player_id}", response_model=Player)
def read_player(player_id: int, session: Session = Depends(get_session)):
    player = session.get(Player, player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Spieler nicht gefunden")
    return player

@router.put("/{player_id}", response_model=Player)
def update_player(player_id: int, updated_player: Player, session: Session = Depends(get_session)):
    player = session.get(Player, player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Spieler nicht gefunden")
    player.name = updated_player.name
    player.nickname = updated_player.nickname
    player.active = updated_player.active
    session.commit()
    session.refresh(player)
    return player

@router.delete("/{player_id}")
def delete_player(player_id: int, session: Session = Depends(get_session)):
    player = session.get(Player, player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Spieler nicht gefunden")
    session.delete(player)
    session.commit()
    return {"detail": "Spieler gelöscht"}
