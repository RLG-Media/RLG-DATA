import uuid
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
from utils import Logger, DatabaseConnection
from exceptions import SessionError


class SessionManager:
    """
    Manages user sessions, including creation, validation, expiration, and termination.
    """

    def __init__(self, db_connection: DatabaseConnection, secret_key: str, session_timeout: int = 3600):
        """
        Initialize the SessionManager.
        Args:
            db_connection (DatabaseConnection): A database connection instance.
            secret_key (str): Secret key for encrypting session data.
            session_timeout (int): Session timeout duration in seconds (default: 1 hour).
        """
        self.db = db_connection
        self.secret_key = secret_key
        self.cipher = Fernet(secret_key)
        self.session_timeout = session_timeout
        self.logger = Logger("SessionManager")

    def create_session(self, user_id: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new session for the given user.
        Args:
            user_id (str): The user's unique identifier.
            metadata (dict, optional): Additional metadata to associate with the session.
        Returns:
            str: The session token.
        """
        session_id = str(uuid.uuid4())
        expiration_time = datetime.utcnow() + timedelta(seconds=self.session_timeout)
        session_data = {
            "user_id": user_id,
            "session_id": session_id,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": expiration_time.isoformat(),
            "metadata": metadata or {},
        }
        encrypted_data = self.cipher.encrypt(str(session_data).encode()).decode()

        # Store session in the database
        try:
            self.db.execute_query(
                """
                INSERT INTO user_sessions (session_id, user_id, session_data, expires_at)
                VALUES (%s, %s, %s, %s)
                """,
                (session_id, user_id, encrypted_data, expiration_time),
            )
            self.logger.info(f"Session created for user {user_id}.")
        except Exception as e:
            self.logger.error(f"Failed to create session for user {user_id}: {e}")
            raise SessionError("Failed to create session.")

        return session_id

    def validate_session(self, session_id: str) -> Dict[str, Any]:
        """
        Validate a session and retrieve its data.
        Args:
            session_id (str): The session token to validate.
        Returns:
            dict: Session data if valid.
        Raises:
            SessionError: If the session is invalid or expired.
        """
        try:
            # Fetch session from the database
            session_record = self.db.execute_query(
                """
                SELECT session_data, expires_at FROM user_sessions WHERE session_id = %s
                """,
                (session_id,),
            )

            if not session_record:
                raise SessionError("Invalid session ID.")

            session_data_encrypted = session_record[0]["session_data"]
            expiration_time = session_record[0]["expires_at"]

            # Check expiration
            if datetime.utcnow() > expiration_time:
                self.terminate_session(session_id)
                raise SessionError("Session has expired.")

            # Decrypt session data
            session_data = eval(self.cipher.decrypt(session_data_encrypted.encode()).decode())
            self.logger.info(f"Session {session_id} validated successfully.")
            return session_data

        except Exception as e:
            self.logger.error(f"Failed to validate session {session_id}: {e}")
            raise SessionError("Failed to validate session.")

    def terminate_session(self, session_id: str) -> None:
        """
        Terminate a session by removing it from the database.
        Args:
            session_id (str): The session token to terminate.
        """
        try:
            self.db.execute_query(
                """
                DELETE FROM user_sessions WHERE session_id = %s
                """,
                (session_id,),
            )
            self.logger.info(f"Session {session_id} terminated.")
        except Exception as e:
            self.logger.error(f"Failed to terminate session {session_id}: {e}")
            raise SessionError("Failed to terminate session.")

    def clean_expired_sessions(self) -> None:
        """
        Remove all expired sessions from the database.
        """
        try:
            self.db.execute_query(
                """
                DELETE FROM user_sessions WHERE expires_at < %s
                """,
                (datetime.utcnow(),),
            )
            self.logger.info("Expired sessions cleaned up.")
        except Exception as e:
            self.logger.error(f"Failed to clean expired sessions: {e}")
            raise SessionError("Failed to clean expired sessions.")

    def refresh_session(self, session_id: str) -> str:
        """
        Refresh an existing session by extending its expiration time.
        Args:
            session_id (str): The session token to refresh.
        Returns:
            str: The updated session token.
        """
        try:
            # Validate the session
            session_data = self.validate_session(session_id)

            # Update expiration time
            new_expiration_time = datetime.utcnow() + timedelta(seconds=self.session_timeout)
            session_data["expires_at"] = new_expiration_time.isoformat()

            encrypted_data = self.cipher.encrypt(str(session_data).encode()).decode()

            self.db.execute_query(
                """
                UPDATE user_sessions SET session_data = %s, expires_at = %s WHERE session_id = %s
                """,
                (encrypted_data, new_expiration_time, session_id),
            )
            self.logger.info(f"Session {session_id} refreshed.")
            return session_id

        except Exception as e:
            self.logger.error(f"Failed to refresh session {session_id}: {e}")
            raise SessionError("Failed to refresh session.")

# Example usage
if __name__ == "__main__":
    db_conn = DatabaseConnection()
    secret_key = Fernet.generate_key().decode()
    session_manager = SessionManager(db_conn, secret_key)

    try:
        # Create a session
        user_id = "12345"
        metadata = {"ip": "192.168.1.1", "device": "Chrome Browser"}
        session_token = session_manager.create_session(user_id, metadata)
        print(f"Session created: {session_token}")

        # Validate the session
        session_data = session_manager.validate_session(session_token)
        print("Session data:", session_data)

        # Refresh the session
        refreshed_token = session_manager.refresh_session(session_token)
        print(f"Session refreshed: {refreshed_token}")

        # Terminate the session
        session_manager.terminate_session(session_token)
        print("Session terminated.")

        # Clean expired sessions
        session_manager.clean_expired_sessions()
        print("Expired sessions cleaned.")
    except SessionError as e:
        print(f"Session Error: {e}")
    except Exception as ex:
        print(f"Unexpected Error: {ex}")
