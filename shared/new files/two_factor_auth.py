import random
import string
import hashlib
import hmac
import base64
import pyotp
from datetime import datetime, timedelta
from typing import Dict, Optional
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class TwoFactorAuth:
    """Class for managing two-factor authentication (2FA)."""

    def __init__(self):
        self.user_2fa_data: Dict[str, Dict] = {}  # Store user-specific 2FA details
        self.temp_otp_store: Dict[str, Dict] = {}  # Temporary storage for OTP validation
        self.totp_interval = 30  # Default interval for time-based OTP (TOTP)

    def generate_email_otp(self, user_id: str) -> str:
        """
        Generates a 6-digit OTP for email-based 2FA.
        Args:
            user_id (str): User's unique identifier.
        Returns:
            str: The generated OTP.
        """
        otp = ''.join(random.choices(string.digits, k=6))
        self.temp_otp_store[user_id] = {
            "otp": otp,
            "expiry": datetime.now() + timedelta(minutes=10),
        }
        logging.info(f"Generated email OTP for user {user_id}: {otp}")
        return otp

    def validate_email_otp(self, user_id: str, otp: str) -> bool:
        """
        Validates the provided OTP for email-based 2FA.
        Args:
            user_id (str): User's unique identifier.
            otp (str): The OTP provided by the user.
        Returns:
            bool: True if the OTP is valid, False otherwise.
        """
        if user_id not in self.temp_otp_store:
            logging.warning(f"No OTP found for user {user_id}.")
            return False

        otp_data = self.temp_otp_store[user_id]
        if datetime.now() > otp_data["expiry"]:
            logging.warning(f"OTP for user {user_id} has expired.")
            return False

        if hmac.compare_digest(otp_data["otp"], otp):
            logging.info(f"Valid email OTP for user {user_id}.")
            del self.temp_otp_store[user_id]  # Clear OTP after successful validation
            return True

        logging.warning(f"Invalid OTP provided by user {user_id}.")
        return False

    def generate_sms_otp(self, user_id: str) -> str:
        """
        Generates a 6-digit OTP for SMS-based 2FA.
        Args:
            user_id (str): User's unique identifier.
        Returns:
            str: The generated OTP.
        """
        return self.generate_email_otp(user_id)  # SMS OTP logic is similar to email OTP

    def validate_sms_otp(self, user_id: str, otp: str) -> bool:
        """
        Validates the provided OTP for SMS-based 2FA.
        Args:
            user_id (str): User's unique identifier.
            otp (str): The OTP provided by the user.
        Returns:
            bool: True if the OTP is valid, False otherwise.
        """
        return self.validate_email_otp(user_id, otp)  # SMS OTP validation is similar to email OTP

    def setup_totp(self, user_id: str) -> str:
        """
        Sets up time-based one-time password (TOTP) for a user.
        Args:
            user_id (str): User's unique identifier.
        Returns:
            str: The TOTP provisioning URI for QR code generation.
        """
        secret = pyotp.random_base32()
        self.user_2fa_data[user_id] = {"totp_secret": secret}
        provisioning_uri = pyotp.TOTP(secret).provisioning_uri(
            name=f"user_{user_id}@example.com", issuer_name="RLG Platform"
        )
        logging.info(f"TOTP setup for user {user_id}: {provisioning_uri}")
        return provisioning_uri

    def validate_totp(self, user_id: str, otp: str) -> bool:
        """
        Validates the provided OTP for time-based one-time password (TOTP).
        Args:
            user_id (str): User's unique identifier.
            otp (str): The OTP provided by the user.
        Returns:
            bool: True if the OTP is valid, False otherwise.
        """
        if user_id not in self.user_2fa_data:
            logging.warning(f"TOTP not set up for user {user_id}.")
            return False

        secret = self.user_2fa_data[user_id]["totp_secret"]
        totp = pyotp.TOTP(secret, interval=self.totp_interval)

        if totp.verify(otp):
            logging.info(f"Valid TOTP for user {user_id}.")
            return True

        logging.warning(f"Invalid TOTP for user {user_id}.")
        return False

    def enforce_2fa(self, user_id: str, method: str, otp: str) -> bool:
        """
        Enforces 2FA by validating the provided OTP using the specified method.
        Args:
            user_id (str): User's unique identifier.
            method (str): The 2FA method ('email', 'sms', 'totp').
            otp (str): The OTP provided by the user.
        Returns:
            bool: True if the OTP is valid, False otherwise.
        """
        if method == "email":
            return self.validate_email_otp(user_id, otp)
        elif method == "sms":
            return self.validate_sms_otp(user_id, otp)
        elif method == "totp":
            return self.validate_totp(user_id, otp)
        else:
            logging.error(f"Invalid 2FA method: {method}.")
            raise ValueError(f"Unsupported 2FA method: {method}")

    def revoke_2fa(self, user_id: str) -> None:
        """
        Revokes 2FA setup for a user.
        Args:
            user_id (str): User's unique identifier.
        """
        if user_id in self.user_2fa_data:
            del self.user_2fa_data[user_id]
            logging.info(f"2FA revoked for user {user_id}.")
        else:
            logging.warning(f"No 2FA setup found for user {user_id}.")
