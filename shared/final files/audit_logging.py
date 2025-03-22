import logging
from datetime import datetime
from typing import List, Dict, Any
from .database import db_session  # Ensure this provides your database session object
from .models import AuditLog   # Your AuditLog model for storing audit logs
from .exceptions import AuditLoggingError  # Custom exception for audit logging errors

# Configure logging
LOGGING_LEVEL = logging.INFO
LOGGING_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(level=LOGGING_LEVEL, format=LOGGING_FORMAT)
logger = logging.getLogger(__name__)


def log_user_action(user_id: int, action: str, description: str, status: str) -> None:
    """
    Record a user action in the audit log for traceability.

    Args:
        user_id (int): The ID of the user performing the action.
        action (str): A description of the action (e.g., "login", "data update").
        description (str): Detailed description of the action.
        status (str): The outcome of the action (e.g., "success", "failure").

    Raises:
        AuditLoggingError: If logging the action fails.
    """
    try:
        audit_log_entry = AuditLog(
            user_id=user_id,
            action=action,
            description=description,
            status=status,
            timestamp=datetime.utcnow()
        )
        db_session.add(audit_log_entry)
        db_session.commit()
        logger.info("Action logged: User %d performed '%s' with status '%s'.", user_id, action, status)
    except Exception as e:
        logger.error("Error logging user action: %s", str(e))
        raise AuditLoggingError("Error logging user action into the audit log.") from e


def log_system_action(action: str, description: str, status: str) -> None:
    """
    Log a system-level action (such as server start, shutdown, or system failure).

    Args:
        action (str): The system action performed.
        description (str): A detailed description of the system action.
        status (str): The result of the action (e.g., "success", "failure").

    Raises:
        AuditLoggingError: If logging the system action fails.
    """
    try:
        system_log_entry = AuditLog(
            user_id=None,  # No user is associated with system-level actions.
            action=action,
            description=description,
            status=status,
            timestamp=datetime.utcnow()
        )
        db_session.add(system_log_entry)
        db_session.commit()
        logger.info("System action logged: %s with status '%s'.", action, status)
    except Exception as e:
        logger.error("Error logging system action: %s", str(e))
        raise AuditLoggingError("Error logging system action into the audit log.") from e


def get_recent_audit_logs(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Retrieve the most recent audit logs from the database.

    Args:
        limit (int): Maximum number of logs to retrieve (default is 10).

    Returns:
        List[Dict[str, Any]]: A list of recent audit logs in a readable dictionary format.

    Raises:
        AuditLoggingError: If retrieval of audit logs fails.
    """
    try:
        logs = db_session.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit).all()
        recent_logs = [{
            "user_id": log.user_id,
            "action": log.action,
            "description": log.description,
            "status": log.status,
            "timestamp": log.timestamp.isoformat()
        } for log in logs]
        return recent_logs
    except Exception as e:
        logger.error("Error retrieving recent audit logs: %s", str(e))
        raise AuditLoggingError("Error retrieving recent audit logs.") from e


def log_authentication_attempt(user_id: int, success: bool, ip_address: str) -> None:
    """
    Log an authentication attempt (login or failure) for a user.

    Args:
        user_id (int): The ID of the user attempting authentication.
        success (bool): True if the authentication was successful; False otherwise.
        ip_address (str): The IP address from which the authentication attempt was made.
    """
    action = "Login" if success else "Login Failure"
    description = f"IP Address: {ip_address}"
    status = "Success" if success else "Failure"
    log_user_action(user_id, action, description, status)


def log_error_event(error_message: str, traceback: str = None) -> None:
    """
    Log an error or failure event for system monitoring.

    Args:
        error_message (str): The error message.
        traceback (str, optional): The traceback information if available.
    """
    try:
        action = "Error"
        description = f"Error Message: {error_message}" + (f", Traceback: {traceback}" if traceback else "")
        status = "Failure"
        log_system_action(action, description, status)
        logger.error("Error occurred: %s, Traceback: %s", error_message, traceback)
    except Exception as e:
        logger.error("Error logging system error event: %s", str(e))
        raise AuditLoggingError("Error logging system error event.") from e


def log_application_shutdown_or_restart(event_type: str) -> None:
    """
    Log an application shutdown or restart event.

    Args:
        event_type (str): The type of event (either "shutdown" or "restart").
    """
    action = f"Application {event_type.capitalize()}"
    description = f"The application has been {event_type}."
    status = "Success"
    log_system_action(action, description, status)


def get_user_audit_logs(user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Retrieve audit logs for a specific user.

    Args:
        user_id (int): The ID of the user.
        limit (int): Maximum number of logs to retrieve (default is 10).

    Returns:
        List[Dict[str, Any]]: A list of audit logs for the specified user.

    Raises:
        AuditLoggingError: If retrieval fails.
    """
    try:
        user_logs = db_session.query(AuditLog).filter(AuditLog.user_id == user_id)\
            .order_by(AuditLog.timestamp.desc()).limit(limit).all()
        user_audit_logs = [{
            "action": log.action,
            "description": log.description,
            "status": log.status,
            "timestamp": log.timestamp.isoformat()
        } for log in user_logs]
        return user_audit_logs
    except Exception as e:
        logger.error("Error retrieving audit logs for user %d: %s", user_id, str(e))
        raise AuditLoggingError(f"Error retrieving audit logs for user {user_id}.") from e

# -------------------------------
# Example Usage (for testing purposes)
# -------------------------------
if __name__ == "__main__":
    try:
        # Example: Log a user action
        log_user_action(user_id=101, action="Login", description="User logged in from web portal", status="Success")
        
        # Example: Log a system action
        log_system_action(action="Server Start", description="Application server started successfully.", status="Success")
        
        # Example: Log an authentication attempt
        log_authentication_attempt(user_id=101, success=True, ip_address="192.168.1.100")
        
        # Example: Log an error event
        log_error_event("Database connection failed", traceback="Traceback details here")
        
        # Example: Log application shutdown event
        log_application_shutdown_or_restart(event_type="shutdown")
        
        # Example: Retrieve recent audit logs
        recent_logs = get_recent_audit_logs(limit=5)
        print("Recent Audit Logs:", recent_logs)
        
        # Example: Retrieve audit logs for a specific user
        user_logs = get_user_audit_logs(user_id=101, limit=5)
        print("Audit Logs for User 101:", user_logs)
        
    except Exception as ex:
        print("An error occurred during audit logging:", ex)
