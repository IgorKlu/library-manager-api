import app.db_models
from app.database.connection import engine
from app.database.base import Base

def init_db() -> None:
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()