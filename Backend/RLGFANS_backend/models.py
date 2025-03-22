# database.py - Database configuration and helper functions for RLG Fans

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import SQLAlchemyError
from config import Config

# Initialize SQLAlchemy base and session
Base = declarative_base()

def get_engine():
    """
    Create and return a new SQLAlchemy engine based on the database URL.
    """
    return create_engine(Config.SQLALCHEMY_DATABASE_URI, echo=False, pool_pre_ping=True)

def get_session_factory():
    """
    Set up a session factory for scoped sessions, ensuring thread safety.
    """
    engine = get_engine()
    session_factory = sessionmaker(bind=engine)
    return scoped_session(session_factory)

# Scoped session for use in database interactions
Session = get_session_factory()

# Helper functions for managing database transactions and setup
def init_db():
    """
    Initialize the database by creating all tables as defined in the ORM models.
    """
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    print("Database initialized.")

def shutdown_session(exception=None):
    """
    Clean up the session to remove it after each request, ensuring no lingering sessions.
    """
    Session.remove()

def commit_session():
    """
    Commit the session, handling any exceptions that occur and rolling back if needed.
    """
    try:
        Session.commit()
    except SQLAlchemyError as e:
        print(f"Error committing session: {e}")
        Session.rollback()
        raise

# To be imported in other modules, such as models
__all__ = ["Base", "Session", "init_db", "shutdown_session", "commit_session"]
