from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from itertools import combinations
from app.db.database import get_session
from app.models.group_match import GroupMatch
from app.models.group_assignment import GroupAssignment
from app.models.player import Player
from app.models.tournament import Tournament

router = APIRouter(prefix="/group-matches", tags=["Gruppenspiele"])


@router.post("/", response_model=GroupMatch)
def create_match(match: GroupMatch, session: Session = Depends(get_session)):
    player1 = session.get(Player, match.player1_id)
    player2 = session.get(Player, match.player2_id)
    tournament = session.get(Tournament, match.tournament_id)

    if not player1 or not player2:
        raise HTTPException(status_code=404, detail="Einer der Spieler wurde nicht gefunden.")
    if not tournament:
        raise HTTPException(status_code=404, detail="Turnier nicht gefunden.")

    session.add(match)
    session.commit()
    session.refresh(match)
    return match


@router.get("/tournament/{tournament_id}", response_model=List[GroupMatch])
def list_matches(tournament_id: int, session: Session = Depends(get_session)):
    return session.exec(select(GroupMatch).where(GroupMatch.tournament_id == tournament_id)).all()


@router.put("/{match_id}", response_model=GroupMatch)
def update_match(match_id: int, updated: GroupMatch, session: Session = Depends(get_session)):
    match = session.get(GroupMatch, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Spiel nicht gefunden.")

    match.sets_player1 = updated.sets_player1
    match.sets_player2 = updated.sets_player2
    match.completed = updated.completed
    match.best_of = updated.best_of
    session.commit()
    session.refresh(match)
    return match


@router.delete("/{match_id}")
def delete_match(match_id: int, session: Session = Depends(get_session)):
    match = session.get(GroupMatch, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Spiel nicht gefunden.")
    session.delete(match)
    session.commit()
    return {"detail": "Spiel gelöscht"}


@router.post("/generate/{tournament_id}")
def generate_group_matches(tournament_id: int, session: Session = Depends(get_session)):
    tournament = session.get(Tournament, tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Turnier nicht gefunden.")

    # Gruppenzuweisung lesen
    assignments = session.exec(
        select(GroupAssignment).where(GroupAssignment.tournament_id == tournament_id)
    ).all()

    # Gruppen strukturieren
    grouped: dict[str, List[int]] = {"A": [], "B": [], "C": [], "D": []}
    for a in assignments:
        if a.group in grouped:
            grouped[a.group].append(a.player_id)

    # Spiele generieren (jeder gegen jeden pro Gruppe)
    match_count = 0
    for group, player_ids in grouped.items():
        for player1_id, player2_id in combinations(player_ids, 2):
            # existiert dieses Match schon?
            existing = session.exec(
                select(GroupMatch).where(
                    (GroupMatch.tournament_id == tournament_id) &
                    (GroupMatch.group == group) &
                    (
                            ((GroupMatch.player1_id == player1_id) & (GroupMatch.player2_id == player2_id)) |
                            ((GroupMatch.player1_id == player2_id) & (GroupMatch.player2_id == player1_id))
                    )
                )
            ).first()
            if existing:
                continue

            new_match = GroupMatch(
                tournament_id=tournament_id,
                group=group,
                player1_id=player1_id,
                player2_id=player2_id,
                best_of=3,
                completed=False,
                sets_player1=0,
                sets_player2=0
            )
            session.add(new_match)
            match_count += 1

    session.commit()
    return {"detail": f"{match_count} Gruppenspiele generiert"}
