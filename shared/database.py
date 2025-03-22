# database.py
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
from sqlalchemy.exc import SQLAlchemyError
import os
import logging

# Logger setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Constants for environment configurations
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/rlg_data")

# Database engine and session configuration
engine = create_engine(DATABASE_URL, pool_size=10, max_overflow=20, pool_timeout=30, echo=True)
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

# Base declarative class for ORM
Base = declarative_base()

# Initialize metadata
metadata = MetaData(bind=engine)

# Connect to the database
def init_db():
    """Initialize and create all tables based on ORM models."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully.")
    except SQLAlchemyError as e:
        logger.error(f"Database initialization error: {str(e)}")
        raise

# Dependency for database session management in FastAPI
def get_db():
    """Yield database session for requests and handle cleanup."""
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        logger.error(f"Database session error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

# Utility functions for CRUD operations

def add_record(db_session, record):
    """Add a new record to the database."""
    try:
        db_session.add(record)
        db_session.commit()
        db_session.refresh(record)
        logger.info(f"Record added successfully: {record}")
        return record
    except SQLAlchemyError as e:
        db_session.rollback()
        logger.error(f"Error adding record: {str(e)}")
        raise

def get_record(db_session, model, record_id):
    """Retrieve a single record by ID."""
    try:
        record = db_session.query(model).get(record_id)
        if not record:
            logger.warning(f"Record with ID {record_id} not found in {model.__name__}")
        return record
    except SQLAlchemyError as e:
        logger.error(f"Error fetching record {record_id} from {model.__name__}: {str(e)}")
        raise

def delete_record(db_session, model, record_id):
    """Delete a single record by ID."""
    try:
        record = db_session.query(model).get(record_id)
        if record:
            db_session.delete(record)
            db_session.commit()
            logger.info(f"Record deleted successfully: ID {record_id} from {model.__name__}")
        else:
            logger.warning(f"Record with ID {record_id} not found in {model.__name__}")
    except SQLAlchemyError as e:
        db_session.rollback()
        logger.error(f"Error deleting record {record_id} from {model.__name__}: {str(e)}")
        raise

def update_record(db_session, model, record_id, updates):
    """Update fields of a single record by ID with given updates."""
    try:
        record = db_session.query(model).get(record_id)
        if not record:
            logger.warning(f"Record with ID {record_id} not found in {model.__name__}")
            return None
        for key, value in updates.items():
            setattr(record, key, value)
        db_session.commit()
        db_session.refresh(record)
        logger.info(f"Record updated successfully: ID {record_id} in {model.__name__}")
        return record
    except SQLAlchemyError as e:
        db_session.rollback()
        logger.error(f"Error updating record {record_id} in {model.__name__}: {str(e)}")
        raise
