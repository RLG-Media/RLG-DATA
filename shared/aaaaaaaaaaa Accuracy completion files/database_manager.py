"""
database_manager.py

This module manages the database connection and operations for both RLG Data and RLG Fans.
It uses SQLAlchemy to define models, create the database engine, manage sessions,
and provide basic CRUD operations.

Models included:
    - RLGData: Represents media-related articles scraped for RLG Data.
    - RLGFans: Represents social posts or fan engagements scraped for RLG Fans.

Ensure you have SQLAlchemy installed:
    pip install sqlalchemy

For production, configure your DB URL securely (e.g., via environment variables).
"""

import os
import logging
from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

# Configure logging
logger = logging.getLogger("DatabaseManager")
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

# Base model for SQLAlchemy
Base = declarative_base()

# -------------------------------
# Model Definitions
# -------------------------------

class RLGData(Base):
    """
    Model for storing media-related articles scraped for RLG Data.
    """
    __tablename__ = "rlg_data"
    id = Column(Integer, primary_key=True)
    title = Column(Text, nullable=False)
    sentiment = Column(String(50), nullable=False, default="neutral")
    region = Column(String(50), nullable=False, default="default")
    scraped_at = Column(DateTime, default=datetime.utcnow)
    # You may add additional fields such as 'url', 'source', 'summary', etc.

    def __repr__(self):
        return f"<RLGData(id={self.id}, title={self.title[:30]}, sentiment={self.sentiment}, region={self.region})>"

class RLGFans(Base):
    """
    Model for storing fan posts or engagement data scraped for RLG Fans.
    """
    __tablename__ = "rlg_fans"
    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    engagement = Column(Float, nullable=False, default=0.0)
    region = Column(String(50), nullable=False, default="default")
    scraped_at = Column(DateTime, default=datetime.utcnow)
    # Additional fields such as 'username', 'post_url', etc., can be added.

    def __repr__(self):
        return f"<RLGFans(id={self.id}, content={self.content[:30]}, engagement={self.engagement}, region={self.region})>"

# -------------------------------
# Database Manager Class
# -------------------------------

class DatabaseManager:
    def __init__(self, db_url=None):
        """
        Initializes the DatabaseManager.

        Parameters:
            db_url (str): Database connection string.
                          Defaults to an SQLite database in the local directory.
                          In production, supply a more robust database URL.
        """
        # Load DB URL from parameter or environment variable, default to SQLite.
        self.db_url = db_url or os.getenv("DATABASE_URL", "sqlite:///rlg_project.db")
        self.engine = create_engine(self.db_url, echo=False, pool_pre_ping=True)
        self.Session = scoped_session(sessionmaker(bind=self.engine))
        logger.info(f"DatabaseManager initialized with DB URL: {self.db_url}")

        # Create tables if they do not exist.
        Base.metadata.create_all(self.engine)
        logger.info("Database tables created (if not already present).")

    def get_session(self):
        """
        Retrieves a new session from the session factory.

        Returns:
            Session: SQLAlchemy session.
        """
        return self.Session()

    def add_rlg_data(self, title, sentiment="neutral", region="default"):
        """
        Adds a new RLGData record to the database.

        Parameters:
            title (str): Title or content of the article.
            sentiment (str): Sentiment of the article (e.g., positive, neutral, negative).
            region (str): Region identifier for the article.

        Returns:
            RLGData: The created RLGData object.
        """
        session = self.get_session()
        try:
            new_record = RLGData(title=title, sentiment=sentiment, region=region)
            session.add(new_record)
            session.commit()
            logger.info(f"Added new RLGData record: {new_record}")
            return new_record
        except Exception as e:
            session.rollback()
            logger.error(f"Error adding RLGData record: {e}")
            raise
        finally:
            session.close()

    def add_rlg_fans(self, content, engagement=0.0, region="default"):
        """
        Adds a new RLGFans record to the database.

        Parameters:
            content (str): Content of the fan post.
            engagement (float): Engagement score for the post.
            region (str): Region identifier for the post.

        Returns:
            RLGFans: The created RLGFans object.
        """
        session = self.get_session()
        try:
            new_record = RLGFans(content=content, engagement=engagement, region=region)
            session.add(new_record)
            session.commit()
            logger.info(f"Added new RLGFans record: {new_record}")
            return new_record
        except Exception as e:
            session.rollback()
            logger.error(f"Error adding RLGFans record: {e}")
            raise
        finally:
            session.close()

    def query_rlg_data(self, region=None):
        """
        Queries RLGData records from the database.

        Parameters:
            region (str, optional): Filter results by region.
        
        Returns:
            list: List of RLGData records.
        """
        session = self.get_session()
        try:
            query = session.query(RLGData)
            if region:
                query = query.filter(RLGData.region == region)
            results = query.all()
            logger.info(f"Queried {len(results)} RLGData records for region: {region}")
            return results
        except Exception as e:
            logger.error(f"Error querying RLGData records: {e}")
            raise
        finally:
            session.close()

    def query_rlg_fans(self, region=None):
        """
        Queries RLGFans records from the database.

        Parameters:
            region (str, optional): Filter results by region.
        
        Returns:
            list: List of RLGFans records.
        """
        session = self.get_session()
        try:
            query = session.query(RLGFans)
            if region:
                query = query.filter(RLGFans.region == region)
            results = query.all()
            logger.info(f"Queried {len(results)} RLGFans records for region: {region}")
            return results
        except Exception as e:
            logger.error(f"Error querying RLGFans records: {e}")
            raise
        finally:
            session.close()

    def update_rlg_data_sentiment(self, record_id, new_sentiment):
        """
        Updates the sentiment field for a specific RLGData record.

        Parameters:
            record_id (int): The primary key of the record to update.
            new_sentiment (str): The new sentiment value.

        Returns:
            RLGData: The updated record.
        """
        session = self.get_session()
        try:
            record = session.query(RLGData).filter(RLGData.id == record_id).one_or_none()
            if record:
                record.sentiment = new_sentiment
                session.commit()
                logger.info(f"Updated RLGData record {record_id} sentiment to {new_sentiment}")
                return record
            else:
                logger.warning(f"RLGData record with id {record_id} not found.")
                return None
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating RLGData record: {e}")
            raise
        finally:
            session.close()

    def delete_rlg_data(self, record_id):
        """
        Deletes a specific RLGData record by its primary key.

        Parameters:
            record_id (int): The primary key of the record to delete.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        session = self.get_session()
        try:
            record = session.query(RLGData).filter(RLGData.id == record_id).one_or_none()
            if record:
                session.delete(record)
                session.commit()
                logger.info(f"Deleted RLGData record with id {record_id}")
                return True
            else:
                logger.warning(f"RLGData record with id {record_id} not found.")
                return False
        except Exception as e:
            session.rollback()
            logger.error(f"Error deleting RLGData record: {e}")
            raise
        finally:
            session.close()

    def delete_rlg_fans(self, record_id):
        """
        Deletes a specific RLGFans record by its primary key.

        Parameters:
            record_id (int): The primary key of the record to delete.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        session = self.get_session()
        try:
            record = session.query(RLGFans).filter(RLGFans.id == record_id).one_or_none()
            if record:
                session.delete(record)
                session.commit()
                logger.info(f"Deleted RLGFans record with id {record_id}")
                return True
            else:
                logger.warning(f"RLGFans record with id {record_id} not found.")
                return False
        except Exception as e:
            session.rollback()
            logger.error(f"Error deleting RLGFans record: {e}")
            raise
        finally:
            session.close()

# -------------------------------
# Additional Recommendations:
# -------------------------------
# 1. **Migrations:** Use Alembic to manage schema changes and migrations over time.
# 2. **Connection Pooling:** Adjust the SQLAlchemy engine configuration for connection pooling in production.
# 3. **Security:** Do not hardcode credentials; load sensitive data via environment variables.
# 4. **Testing:** Implement unit tests for all CRUD operations.
# 5. **Asynchronous Support:** For high concurrency, consider an async database library or session management strategy.

# -------------------------------
# Standalone Testing
# -------------------------------
if __name__ == "__main__":
    db_manager = DatabaseManager()

    # Add sample RLG Data record
    data_record = db_manager.add_rlg_data(
        title="Sample Media Article Title",
        sentiment="positive",
        region="us"
    )
    print("Added RLGData record:", data_record)

    # Add sample RLG Fans record
    fans_record = db_manager.add_rlg_fans(
        content="Sample fan post content.",
        engagement=45.5,
        region="us"
    )
    print("Added RLGFans record:", fans_record)

    # Query and print RLG Data records for region 'us'
    data_records = db_manager.query_rlg_data(region="us")
    print("Queried RLGData records:", data_records)

    # Query and print RLG Fans records for region 'us'
    fans_records = db_manager.query_rlg_fans(region="us")
    print("Queried RLGFans records:", fans_records)

    # Update sentiment for a sample record
    if data_records:
        updated_record = db_manager.update_rlg_data_sentiment(data_records[0].id, "neutral")
        print("Updated record:", updated_record)

    # Delete sample records (uncomment to test deletion)
    # db_manager.delete_rlg_data(data_record.id)
    # db_manager.delete_rlg_fans(fans_record.id)
