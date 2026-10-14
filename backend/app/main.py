"""PayShield API: run with  uvicorn app.main:app --reload  (from the backend folder)."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models  # noqa: F401  (makes sure the tables are known)
from app.config import ALLOWED_ORIGINS
from app.database import Base, engine
from app.routers import feedback, health, predict, scam, stats, transactions


@asynccontextmanager
async def lifespan(app: FastAPI):
    # On startup: create the database tables if they don't exist yet
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="PayShield API", version="1.0.0", lifespan=lifespan)

# CORS: lets the React frontend (a different address) call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(predict.router)
app.include_router(transactions.router)
app.include_router(stats.router)
app.include_router(scam.router)
app.include_router(feedback.router)