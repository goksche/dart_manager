from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List, Dict
from random import shuffle
from app.db.database import get_session
from app.models.group_assignment import GroupAssignment, GroupAssignmentInput
from app.models.player import Player
from app.models.tournament import Tournament

router = APIRouter(prefix="/groups", tags=["Gruppenzuordnung"])

@router.post("/assign/{tournament_id}")
def assign_groups(
    tournament_id: int,
    assignments: GroupAssignmentInput,
    session: Session = Depends(get_session)
):
    tournament = session.get(Tournament, tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Turnier nicht gefunden")

    input_dict = assignments.dict()

    for group, player_ids in input_dict.items():
        for player_id in player_ids:
            player = session.get(Player, player_id)
            if not player:
                raise HTTPException(status_code=404, detail=f"Spieler {player_id} nicht gefunden")
            already = session.exec(
                select(GroupAssignment).where(
                    (GroupAssignment.tournament_id == tournament_id) &
                    (GroupAssignment.player_id == player_id)
                )
            ).first()
            if not already:
                entry = GroupAssignment(
                    tournament_id=tournament_id,
                    player_id=player_id,
                    group=group
                )
                session.add(entry)

    session.commit()
    return {"detail": "Spieler wurden Gruppen zugewiesen."}

@router.post("/randomize/{tournament_id}")
def randomize_remaining_players(tournament_id: int, session: Session = Depends(get_session)):
    tournament = session.get(Tournament, tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Turnier nicht gefunden")

    num_groups = tournament.num_groups
    group_names = ["A", "B", "C", "D"][:num_groups]

    # Bereits zugewiesene Spieler herausfinden
    assigned = session.exec(
        select(GroupAssignment.player_id).where(GroupAssignment.tournament_id == tournament_id)
    ).all()
    assigned_ids = set(assigned)

    # Alle zugewiesenen Teilnehmer laut Turniermodell
    all_participants = [p.id for p in tournament.players]
    unassigned_ids = [pid for pid in all_participants if pid not in assigned_ids]

    shuffle(unassigned_ids)

    # aktuelle Gruppenzuordnung lesen
    current_distribution: Dict[str, List[int]] = {g: [] for g in group_names}
    existing = session.exec(
        select(GroupAssignment).where(GroupAssignment.tournament_id == tournament_id)
    ).all()
    for e in existing:
        if e.group in current_distribution:
            current_distribution[e.group].append(e.player_id)

    # gleichmäßig auffüllen
    for pid in unassigned_ids:
        min_group = min(current_distribution, key=lambda g: len(current_distribution[g]))
        entry = GroupAssignment(
            tournament_id=tournament_id,
            player_id=pid,
            group=min_group
        )
        current_distribution[min_group].append(pid)
        session.add(entry)

    session.commit()
    return {
        "detail": "Nicht zugewiesene Spieler wurden zufällig auf Gruppen verteilt.",
        "final_groups": current_distribution
    }

@router.get("/{tournament_id}", response_model=Dict[str, List[int]])
def get_group_assignments(tournament_id: int, session: Session = Depends(get_session)):
    groups = {"A": [], "B": [], "C": [], "D": []}
    results = session.exec(
        select(GroupAssignment).where(GroupAssignment.tournament_id == tournament_id)
    ).all()
    for entry in results:
        groups[entry.group].append(entry.player_id)
    return groups
