from sqlmodel import Session, SQLModel, create_engine

from app.config import settings

# Import all models to register them with SQLModel
from app.models import *  # noqa: F401, F403

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
    echo=settings.app_debug,
)


def init_db() -> None:
    """Initialize database by creating all tables."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    """Dependency to get database session."""
    with Session(engine) as session:
        yield session

