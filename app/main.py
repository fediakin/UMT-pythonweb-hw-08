from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.database import engine, Base
from app.routers import contacts

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title="Contacts REST API",
    description="Домашнє завдання: створення REST API для управління контактами",
    lifespan=lifespan
)

app.include_router(contacts.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Contacts API! Visit /docs for Swagger UI"}