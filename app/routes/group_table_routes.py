from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import Dict, List
from app.db.database import get_session
from app.models.group_match import GroupMatch
from app.models.group_assignment import GroupAssignment
from app.models.tournament import Tournament

router = APIRouter(prefix="/group-evaluation", tags=["Gruppenwertung"])

class TableEntry:
    def __init__(self, player_id: int):
        self.player_id = player_id
        self.sets_won = 0
        self.sets_lost = 0
        self.points = 0  # Differenz
        self.matches = []

    def update(self, sets_won: int, sets_lost: int, opponent_id: int):
        self.sets_won += sets_won
        self.sets_lost += sets_lost
        self.points = self.sets_won - self.sets_lost
        self.matches.append((opponent_id, sets_won, sets_lost))

@router.get("/group-table/{tournament_id}")
def get_group_tables(tournament_id: int, session: Session = Depends(get_session)):
    tournament = session.get(Tournament, tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Turnier nicht gefunden.")

    matches = session.exec(
        select(GroupMatch).where(GroupMatch.tournament_id == tournament_id, GroupMatch.completed == True)
    ).all()

    tables: Dict[str, Dict[int, TableEntry]] = {}

    for match in matches:
        g = match.group
        if g not in tables:
            tables[g] = {}
        for pid in [match.player1_id, match.player2_id]:
            if pid not in tables[g]:
                tables[g][pid] = TableEntry(pid)

        tables[g][match.player1_id].update(match.sets_player1, match.sets_player2, match.player2_id)
        tables[g][match.player2_id].update(match.sets_player2, match.sets_player1, match.player1_id)

    result = {}
    for group, players in tables.items():
        # Sortieren nach Punktestand
        sorted_players = sorted(players.values(), key=lambda p: p.points, reverse=True)

        # Gleichstand-Prüfung
        i = 0
        while i < len(sorted_players) - 1:
            group_block = [sorted_players[i]]
            j = i + 1
            while j < len(sorted_players) and sorted_players[j].points == sorted_players[i].points:
                group_block.append(sorted_players[j])
                j += 1

            if len(group_block) == 2:
                # Direktvergleich
                p1, p2 = group_block[0], group_block[1]
                for opp, s1, s2 in p1.matches:
                    if opp == p2.player_id:
                        if s1 < s2:
                            group_block[0], group_block[1] = p2, p1
                        break
            elif len(group_block) > 2:
                # 3er-Tabelle
                mini = {}
                for p in group_block:
                    mini[p.player_id] = {"sets_won": 0, "sets_lost": 0, "diff": 0}
                for p in group_block:
                    for opp, s1, s2 in p.matches:
                        if opp in mini:
                            mini[p.player_id]["sets_won"] += s1
                            mini[p.player_id]["sets_lost"] += s2
                for pid in mini:
                    m = mini[pid]
                    m["diff"] = m["sets_won"] - m["sets_lost"]
                group_block.sort(key=lambda p: mini[p.player_id]["diff"], reverse=True)

            # ersetzen
            sorted_players[i:j] = group_block
            i = j

        result[group] = [
            {"player_id": p.player_id, "points": p.points, "sets_won": p.sets_won, "sets_lost": p.sets_lost}
            for p in sorted_players
        ]
    return result

@router.get("/ko-candidates/{tournament_id}")
def get_ko_candidates(tournament_id: int, session: Session = Depends(get_session)):
    tournament = session.get(Tournament, tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Turnier nicht gefunden.")

    table = get_group_tables(tournament_id, session)
    num_groups = tournament.num_groups
    candidates = []

    for group in table:
        if num_groups == 2:
            candidates.extend([entry["player_id"] for entry in table[group][:4]])
        elif num_groups == 4:
            candidates.extend([entry["player_id"] for entry in table[group][:2]])

    return {"qualified_players": candidates}
