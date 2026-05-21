import os
from typing import Generator

from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, Session, create_engine

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./admin_agent.db",
)

engine_kwargs = {
    "echo": False,
    "pool_pre_ping": True,
}

if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    engine_kwargs["pool_size"] = 10
    engine_kwargs["max_overflow"] = 20

engine = create_engine(DATABASE_URL, **engine_kwargs)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=Session,
)


def create_db_and_tables() -> None:
    import app.models  # noqa: F401

    SQLModel.metadata.create_all(engine)


def init_db() -> None:
    create_db_and_tables()


def get_session() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session


def get_db() -> Generator[Session, None, None]:
    yield from get_session()
