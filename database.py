from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Use SQLite for a simple, file-based database that requires no extra installation.
SQLALCHEMY_DATABASE_URL = "sqlite:///./certificates.db"

# create_engine establishes the connection to the database.
# check_same_thread=False is needed for SQLite when used with FastAPI (which uses multiple threads).
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# SessionLocal is a factory for creating database sessions for each request.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our SQLAlchemy models.
Base = declarative_base()

# Dependency function to get the database session in our API routes.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
