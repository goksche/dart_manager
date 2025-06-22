from fastapi import FastAPI
from app.routes import (
    player_routes,
    tournament_routes,
    participation_routes,
    group_routes,
    group_match_routes,
    group_table_routes,
    ko_match_routes
)
from app.db.database import init_db

app = FastAPI(title="Dartclub Turnierverwaltung")

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(player_routes.router)
app.include_router(tournament_routes.router)
app.include_router(participation_routes.router)
app.include_router(group_routes.router)
app.include_router(group_match_routes.router)
app.include_router(group_table_routes.router)
app.include_router(ko_match_routes.router)
