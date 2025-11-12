from sqlmodel import SQLModel, create_engine, Session
from .config import settings

engine = create_engine(settings.DATABASE_URL, echo=False, future=True)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    return Session(engine)
