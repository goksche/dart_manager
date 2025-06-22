from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, Session
from typing import List
from app.db.database import get_session
from app.models.ko_match import KoMatch
from app.models.tournament import Tournament
from app.routes.group_table_routes import get_ko_candidates

router = APIRouter(prefix="/ko-matches", tags=["KO-Phase"])

@router.post("/generate/{tournament_id}")
def generate_ko_matches(tournament_id: int, session: Session = Depends(get_session)):
    tournament = session.get(Tournament, tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Turnier nicht gefunden")

    ko_result = get_ko_candidates(tournament_id, session)
    players = ko_result["qualified_players"]
    if len(players) != 8:
        raise HTTPException(status_code=400, detail="Es werden genau 8 KO-Spieler benötigt")

    # KO-Schema nach Vorgabe
    aa = players[:4]
    bb = players[4:]

    # Viertelfinale
    viertel = [
        ("C1", aa[0], bb[3]),
        ("C2", bb[0], aa[3]),
        ("C3", aa[1], bb[2]),
        ("C4", bb[1], aa[2])
    ]
    for label, p1, p2 in viertel:
        match = KoMatch(
            tournament_id=tournament_id,
            round="Viertelfinale",
            label=label,
            player1_id=p1,
            player2_id=p2,
            best_of=5,
            completed=False
        )
        session.add(match)

    # Platzhalter Halbfinale, Finale, kleines Finale
    halbfinale = [
        ("D1", None, None),  # Sieger C1 vs Sieger C4
        ("D2", None, None),  # Sieger C2 vs Sieger C3
    ]
    for label, p1, p2 in halbfinale:
        match = KoMatch(
            tournament_id=tournament_id,
            round="Halbfinale",
            label=label,
            player1_id=p1,
            player2_id=p2,
            best_of=7,
            completed=False
        )
        session.add(match)

    session.add(KoMatch(
        tournament_id=tournament_id,
        round="Finale",
        label="F",
        player1_id=None,
        player2_id=None,
        best_of=9,
        completed=False
    ))

    session.add(KoMatch(
        tournament_id=tournament_id,
        round="Kleines Finale",
        label="K",
        player1_id=None,
        player2_id=None,
        best_of=5,
        completed=False
    ))

    session.commit()
    return {"detail": "KO-Spielplan generiert"}
