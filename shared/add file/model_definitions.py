# model_definitions.py - Database Models for RLG Data and RLG Fans

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Float,
    DateTime,
    ForeignKey,
    Text,
    UniqueConstraint,
    JSON,
)
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    """
    Represents a user in the system for both RLG Data and RLG Fans.
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    profiles = relationship("UserProfile", back_populates="user", cascade="all, delete-orphan")
    tokens = relationship("AuthToken", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"


class UserProfile(Base):
    """
    Represents additional profile information for users.
    """
    __tablename__ = 'user_profiles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    display_name = Column(String(100), nullable=False)
    bio = Column(Text, nullable=True)
    profile_picture_url = Column(String(255), nullable=True)
    preferences = Column(JSON, nullable=True)

    user = relationship("User", back_populates="profiles")

    def __repr__(self):
        return f"<UserProfile(id={self.id}, user_id={self.user_id}, display_name={self.display_name})>"


class AuthToken(Base):
    """
    Represents authentication tokens for user sessions.
    """
    __tablename__ = 'auth_tokens'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    token = Column(String(255), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="tokens")

    def __repr__(self):
        return f"<AuthToken(id={self.id}, user_id={self.user_id})>"


class PlatformIntegration(Base):
    """
    Represents platform integrations for both RLG Data and RLG Fans.
    """
    __tablename__ = 'platform_integrations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    platform_name = Column(String(50), nullable=False)
    access_token = Column(String(255), nullable=False)
    refresh_token = Column(String(255), nullable=True)
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="platform_integrations")

    __table_args__ = (
        UniqueConstraint('user_id', 'platform_name', name='_user_platform_uc'),
    )

    def __repr__(self):
        return f"<PlatformIntegration(id={self.id}, user_id={self.user_id}, platform_name={self.platform_name})>"


class LogEntry(Base):
    """
    Represents a log entry for system activities and events.
    """
    __tablename__ = 'log_entries'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)  # Nullable for system logs
    action = Column(String(255), nullable=False)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="log_entries")

    def __repr__(self):
        return f"<LogEntry(id={self.id}, user_id={self.user_id}, action={self.action})>"


class Notification(Base):
    """
    Represents notifications for users.
    """
    __tablename__ = 'notifications'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String(100), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="notifications")

    def __repr__(self):
        return f"<Notification(id={self.id}, user_id={self.user_id}, title={self.title})>"


class DataReport(Base):
    """
    Represents generated data reports for RLG Data and RLG Fans.
    """
    __tablename__ = 'data_reports'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    report_type = Column(String(50), nullable=False)
    data = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="data_reports")

    def __repr__(self):
        return f"<DataReport(id={self.id}, user_id={self.user_id}, report_type={self.report_type})>"

# Relationships back-populated
User.log_entries = relationship("LogEntry", back_populates="user", cascade="all, delete-orphan")
User.notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
User.platform_integrations = relationship("PlatformIntegration", back_populates="user", cascade="all, delete-orphan")
User.data_reports = relationship("DataReport", back_populates="user", cascade="all, delete-orphan")

# Utility Function
def initialize_database(engine):
    """
    Initialize the database by creating all tables.

    Args:
        engine: SQLAlchemy engine connected to the database.
    """
    Base.metadata.create_all(engine)
    print("Database initialized successfully.")
