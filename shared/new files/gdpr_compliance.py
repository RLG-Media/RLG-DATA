import json
import logging
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("gdpr_compliance.log"),
        logging.StreamHandler()
    ]
)


class GDPRComplianceManager:
    """
    A comprehensive GDPR compliance manager for handling user data requests, consent management, and compliance processes.
    """

    def __init__(self, database: str = "user_data.json"):
        """
        Initialize the GDPR compliance manager.
        :param database: Path to the JSON file simulating a database.
        """
        self.database = database
        self._initialize_database()
        logging.info("GDPR Compliance Manager initialized.")

    def _initialize_database(self):
        """Ensures the database file exists and initializes it if empty."""
        try:
            with open(self.database, "r") as db:
                json.load(db)
        except (FileNotFoundError, json.JSONDecodeError):
            with open(self.database, "w") as db:
                json.dump([], db)
            logging.info(f"Database initialized at {self.database}.")

    def get_user_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a user's data.
        :param user_id: The user's unique identifier.
        :return: The user's data, or None if not found.
        """
        data = self._read_database()
        user_data = next((user for user in data if user["user_id"] == user_id), None)
        if user_data:
            logging.info(f"User data retrieved for user_id: {user_id}.")
        else:
            logging.warning(f"User data not found for user_id: {user_id}.")
        return user_data

    def request_data_access(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Handles a user's data access request.
        :param user_id: The user's unique identifier.
        :return: The user's data or None if not found.
        """
        return self.get_user_data(user_id)

    def request_data_erasure(self, user_id: str) -> bool:
        """
        Handles a user's data erasure request.
        :param user_id: The user's unique identifier.
        :return: True if the data was erased, False otherwise.
        """
        data = self._read_database()
        updated_data = [user for user in data if user["user_id"] != user_id]

        if len(data) != len(updated_data):
            self._write_database(updated_data)
            logging.info(f"Data erased for user_id: {user_id}.")
            return True
        else:
            logging.warning(f"No data found to erase for user_id: {user_id}.")
            return False

    def update_user_consent(self, user_id: str, consent_status: bool) -> bool:
        """
        Updates a user's consent status.
        :param user_id: The user's unique identifier.
        :param consent_status: The updated consent status (True for consented, False otherwise).
        :return: True if the update was successful, False otherwise.
        """
        data = self._read_database()
        for user in data:
            if user["user_id"] == user_id:
                user["consent_status"] = consent_status
                self._write_database(data)
                logging.info(f"Consent status updated for user_id: {user_id}.")
                return True
        logging.warning(f"User not found for consent update: {user_id}.")
        return False

    def export_user_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Exports a user's data in a machine-readable format (JSON).
        :param user_id: The user's unique identifier.
        :return: A dictionary of the user's data or None if not found.
        """
        user_data = self.get_user_data(user_id)
        if user_data:
            export_path = f"{user_id}_data_export.json"
            with open(export_path, "w") as file:
                json.dump(user_data, file, indent=4)
            logging.info(f"Data exported for user_id: {user_id} to {export_path}.")
            return user_data
        return None

    def _read_database(self) -> List[Dict[str, Any]]:
        """Reads the database from the JSON file."""
        with open(self.database, "r") as db:
            return json.load(db)

    def _write_database(self, data: List[Dict[str, Any]]):
        """Writes the database to the JSON file."""
        with open(self.database, "w") as db:
            json.dump(data, db, indent=4)

    def add_user(self, user_data: Dict[str, Any]) -> bool:
        """
        Adds a new user to the database.
        :param user_data: A dictionary of user data.
        :return: True if the user was added successfully.
        """
        data = self._read_database()
        if any(user["user_id"] == user_data["user_id"] for user in data):
            logging.warning(f"User with user_id {user_data['user_id']} already exists.")
            return False

        data.append(user_data)
        self._write_database(data)
        logging.info(f"User added with user_id: {user_data['user_id']}.")
        return True

# --- Example Usage ---
if __name__ == "__main__":
    gdpr_manager = GDPRComplianceManager()

    # Example user data
    example_user = {
        "user_id": "12345",
        "name": "John Doe",
        "email": "john.doe@example.com",
        "consent_status": True,
        "data": {
            "preferences": {"theme": "dark", "notifications": True},
            "activity": {"last_login": "2025-01-03"}
        }
    }

    # Add user
    gdpr_manager.add_user(example_user)

    # Access user data
    user_data = gdpr_manager.request_data_access("12345")
    print("User Data Access:", user_data)

    # Update consent
    gdpr_manager.update_user_consent("12345", False)

    # Export user data
    gdpr_manager.export_user_data("12345")

    # Erase user data
    gdpr_manager.request_data_erasure("12345")
