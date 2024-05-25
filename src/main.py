from fastapi import FastAPI
from src.user.api import router as user_router
# from src.competition.api import router as competition_router
# from src.entry.api import router as entry_router
from uvicorn import run

app = FastAPI()

app.include_router(user_router, prefix="/users", tags=["users"])
# app.include_router(competition_router, prefix="/competitions", tags=["competitions"])
# app.include_router(entry_router, prefix="/entries", tags=["entries"])

if __name__ == "__main__":
    run(app, port=8000)