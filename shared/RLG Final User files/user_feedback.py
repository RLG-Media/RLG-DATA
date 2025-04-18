import logging
from typing import Any, Dict, Optional
from flask import request, jsonify, current_app

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class UserFeedback:
    """
    Service class for handling user feedback operations.
    
    This class provides methods to submit, retrieve, and delete user feedback.
    It integrates with a database (passed as a dependency) to store feedback data.
    """

    def __init__(self, db: Any) -> None:
        """
        Initialize the UserFeedback service with a database connection.
        
        Args:
            db (Any): A database object that provides methods like insert, query, and delete.
        """
        self.db = db

    def submit_feedback(self) -> Any:
        """
        Submit user feedback received via a POST request.
        
        Expects a JSON payload with 'user_id' and 'feedback'. Optionally, 'created_at' can be provided;
        if not, the current UTC time is used.
        
        Returns:
            A Flask JSON response indicating success or failure.
        """
        try:
            feedback_data: Dict[str, Any] = request.get_json()
            if not feedback_data or 'user_id' not in feedback_data or 'feedback' not in feedback_data:
                return jsonify({'status': 'error', 'message': 'Invalid feedback data'}), 400

            # Use current UTC time if 'created_at' is not provided.
            feedback_entry = {
                'user_id': feedback_data['user_id'],
                'feedback': feedback_data['feedback'],
                'created_at': feedback_data.get('created_at') or current_app.config.get('CURRENT_TIME') or None
            }

            # Insert the feedback into the database (replace with your actual insert logic)
            self.db.insert('user_feedback', feedback_entry)

            return jsonify({'status': 'success', 'message': 'Feedback submitted successfully'}), 201

        except Exception as e:
            logger.error(f"Error while submitting feedback for user {feedback_data.get('user_id', 'N/A')}: {e}")
            return jsonify({'status': 'error', 'message': 'An error occurred while submitting feedback'}), 500

    def get_feedback(self, user_id: Optional[str] = None) -> Any:
        """
        Retrieve user feedback. Optionally filter by user_id.
        
        Args:
            user_id (Optional[str]): The user ID to filter feedback; if not provided, retrieves all feedback.
        
        Returns:
            A Flask JSON response with the list of feedback entries, or an error message if retrieval fails.
        """
        try:
            query = "SELECT * FROM user_feedback"
            params: Dict[str, Any] = {}

            if user_id:
                query += " WHERE user_id = :user_id"
                params['user_id'] = user_id

            # Retrieve feedback from the database (replace with your actual query logic)
            feedback_list = self.db.query(query, params)

            if feedback_list:
                return jsonify({'status': 'success', 'feedback': feedback_list}), 200
            else:
                return jsonify({'status': 'error', 'message': 'No feedback found'}), 404

        except Exception as e:
            logger.error(f"Error while retrieving feedback for user {user_id}: {e}")
            return jsonify({'status': 'error', 'message': 'An error occurred while retrieving feedback'}), 500

    def delete_feedback(self, feedback_id: int) -> Any:
        """
        Delete a feedback entry by its ID.
        
        Args:
            feedback_id (int): The ID of the feedback to delete.
        
        Returns:
            A Flask JSON response indicating success or failure of the deletion.
        """
        try:
            # Retrieve the feedback entry to verify it exists (replace with your actual DB logic)
            feedback_entry = self.db.query("SELECT * FROM user_feedback WHERE id = :id", {'id': feedback_id})
            if feedback_entry:
                self.db.delete('user_feedback', {'id': feedback_id})
                return jsonify({'status': 'success', 'message': f'Feedback for ID {feedback_id} has been deleted'}), 200
            else:
                return jsonify({'status': 'error', 'message': 'Feedback not found'}), 404

        except Exception as e:
            logger.error(f"Error while deleting feedback with ID {feedback_id}: {e}")
            return jsonify({'status': 'error', 'message': 'An error occurred while deleting feedback'}), 500

# Example usage:
# Assuming you have a database instance 'db_instance' that implements 'insert', 'query', and 'delete' methods,
# you can initialize and use the UserFeedback service as follows:
#
# from your_database_module import db_instance
# feedback_handler = UserFeedback(db_instance)
#
# Then, in your Flask routes, you might call:
#   - feedback_handler.submit_feedback()
#   - feedback_handler.get_feedback(user_id="user123")
#   - feedback_handler.delete_feedback(feedback_id=1)
