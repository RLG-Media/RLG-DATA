import secrets
import string
from typing import Optional
from datetime import datetime, timedelta
import hashlib
import smtplib
from email.mime.text import MIMEText

class ResetPasswordService:
    """
    Handles password reset functionality, including generating reset tokens,
    validating tokens, and resetting user passwords for RLG Data and RLG Fans.
    """

    def __init__(self, token_expiry_minutes: int = 15):
        """
        Initialize the ResetPasswordService.

        Args:
            token_expiry_minutes (int): The duration (in minutes) before a reset token expires.
        """
        self.token_expiry_minutes = token_expiry_minutes
        self.reset_tokens = {}  # Format: {user_id: {'token': str, 'expires_at': datetime}}

    def generate_reset_token(self, user_id: str) -> str:
        """
        Generate a secure password reset token.

        Args:
            user_id (str): The ID of the user requesting a password reset.

        Returns:
            str: The generated reset token.
        """
        token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
        expires_at = datetime.now() + timedelta(minutes=self.token_expiry_minutes)
        self.reset_tokens[user_id] = {'token': token, 'expires_at': expires_at}

        print(f"[{datetime.now()}] Generated reset token for user {user_id}. Expires at {expires_at}.")
        return token

    def validate_reset_token(self, user_id: str, token: str) -> bool:
        """
        Validate a password reset token.

        Args:
            user_id (str): The ID of the user.
            token (str): The reset token to validate.

        Returns:
            bool: True if the token is valid, False otherwise.
        """
        user_token_info = self.reset_tokens.get(user_id)
        if not user_token_info:
            print(f"[{datetime.now()}] No reset token found for user {user_id}.")
            return False

        if token != user_token_info['token']:
            print(f"[{datetime.now()}] Invalid token for user {user_id}.")
            return False

        if datetime.now() > user_token_info['expires_at']:
            print(f"[{datetime.now()}] Token expired for user {user_id}.")
            return False

        print(f"[{datetime.now()}] Token validated for user {user_id}.")
        return True

    def reset_password(self, user_id: str, new_password: str) -> bool:
        """
        Reset the user's password.

        Args:
            user_id (str): The ID of the user.
            new_password (str): The new password to set.

        Returns:
            bool: True if the password reset is successful, False otherwise.
        """
        if user_id not in self.reset_tokens:
            print(f"[{datetime.now()}] No reset request found for user {user_id}.")
            return False

        # Simulating password hash storage
        hashed_password = self._hash_password(new_password)
        self._update_user_password_in_db(user_id, hashed_password)

        # Remove the used token
        del self.reset_tokens[user_id]
        print(f"[{datetime.now()}] Password reset successfully for user {user_id}.")
        return True

    def send_reset_email(self, user_email: str, token: str, app_name: str = "RLG"):
        """
        Send a password reset email to the user.

        Args:
            user_email (str): The user's email address.
            token (str): The reset token.
            app_name (str): The application name (RLG Data or RLG Fans).
        """
        reset_link = f"https://{app_name.lower()}.com/reset-password?token={token}"
        subject = f"{app_name} Password Reset Request"
        body = f"""
        Hi,

        You have requested to reset your password for {app_name}.
        Please use the link below to reset your password:
        
        {reset_link}
        
        This link will expire in {self.token_expiry_minutes} minutes.

        If you did not request this reset, please ignore this email.

        Thanks,
        {app_name} Team
        """

        try:
            # Replace with your SMTP configuration
            smtp_host = "smtp.example.com"
            smtp_port = 587
            smtp_user = "noreply@example.com"
            smtp_password = "yourpassword"

            msg = MIMEText(body)
            msg["Subject"] = subject
            msg["From"] = smtp_user
            msg["To"] = user_email

            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.sendmail(smtp_user, [user_email], msg.as_string())

            print(f"[{datetime.now()}] Password reset email sent to {user_email}.")
        except Exception as e:
            print(f"[{datetime.now()}] Failed to send email to {user_email}: {e}")

    def _hash_password(self, password: str) -> str:
        """
        Hash the password for secure storage.

        Args:
            password (str): The password to hash.

        Returns:
            str: The hashed password.
        """
        salt = secrets.token_hex(16)
        hashed = hashlib.sha256((salt + password).encode()).hexdigest()
        return f"{salt}${hashed}"

    def _update_user_password_in_db(self, user_id: str, hashed_password: str):
        """
        Simulate updating the user's password in the database.

        Args:
            user_id (str): The ID of the user.
            hashed_password (str): The hashed password to store.
        """
        # Simulated database update logic
        print(f"[{datetime.now()}] Updated password for user {user_id} in database.")

# Example Usage
if __name__ == "__main__":
    reset_service = ResetPasswordService()

    # Simulating a password reset flow
    user_id = "user123"
    user_email = "user@example.com"

    token = reset_service.generate_reset_token(user_id)
    reset_service.send_reset_email(user_email, token, app_name="RLG Data")

    # Simulate validating and resetting the password
    if reset_service.validate_reset_token(user_id, token):
        reset_service.reset_password(user_id, "newSecurePassword123")
