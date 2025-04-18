import hashlib
import hmac
import urllib.parse
from typing import Dict
from flask import current_app as app

class PayFastPayment:
    """
    Handles PayFast payment gateway integration for both RLG Data and RLG Fans platforms.
    """

    def __init__(self, merchant_id: str, merchant_key: str, passphrase: str = "", testing: bool = True):
        """
        Initializes the PayFastPayment instance.

        :param merchant_id: Your PayFast Merchant ID.
        :param merchant_key: Your PayFast Merchant Key.
        :param passphrase: Optional passphrase for signature generation.
        :param testing: Whether to use the sandbox environment.
        """
        self.merchant_id = merchant_id
        self.merchant_key = merchant_key
        self.passphrase = passphrase
        self.base_url = (
            "https://sandbox.payfast.co.za/eng/process" if testing else "https://www.payfast.co.za/eng/process"
        )

    def generate_payment_url(self, data: Dict[str, str]) -> str:
        """
        Generates a secure payment URL for the user to complete the payment.

        :param data: A dictionary containing payment details, such as amount, item name, and user details.
        :return: A complete payment URL to redirect the user to PayFast for payment.
        """
        # Add merchant credentials
        data["merchant_id"] = self.merchant_id
        data["merchant_key"] = self.merchant_key

        # Generate the signature for security
        data["signature"] = self._generate_signature(data)

        # Encode URL parameters
        query_string = urllib.parse.urlencode(data)

        # Log the payment URL for debugging purposes (only in testing mode)
        if app.config.get("DEBUG", False):
            app.logger.debug(f"Generated PayFast URL: {self.base_url}?{query_string}")

        return f"{self.base_url}?{query_string}"

    def _generate_signature(self, data: Dict[str, str]) -> str:
        """
        Generates a security signature for the request to PayFast.

        :param data: A dictionary containing payment details.
        :return: A secure signature string, used for validation on PayFast's side.
        """
        # Sort data alphabetically by keys
        sorted_data = {key: value for key, value in sorted(data.items())}

        # Concatenate the data into a query string
        query_string = urllib.parse.urlencode(sorted_data)

        # Add passphrase if available for additional security
        if self.passphrase:
            query_string += f"&passphrase={self.passphrase}"

        # Generate the signature using MD5 hash
        return hashlib.md5(query_string.encode("utf-8")).hexdigest()

    def validate_ipn(self, ipn_data: Dict[str, str], ipn_signature: str) -> bool:
        """
        Validates the Instant Payment Notification (IPN) received from PayFast.

        :param ipn_data: The received IPN data as a dictionary.
        :param ipn_signature: The received IPN signature to validate.
        :return: True if the IPN is valid (signature matches), False otherwise.
        """
        try:
            # Generate a signature from the received IPN data
            generated_signature = self._generate_signature(ipn_data)

            # Validate the signature using hmac comparison to prevent tampering
            return hmac.compare_digest(generated_signature, ipn_signature)
        except Exception as e:
            # Log the exception for debugging purposes
            app.logger.error(f"Error validating IPN: {e}")
            return False

    def log_ipn_data(self, ipn_data: Dict[str, str]):
        """
        Logs the received IPN data for troubleshooting or audit purposes.

        :param ipn_data: The IPN data received from PayFast.
        """
        if app.config.get("DEBUG", False):
            app.logger.debug(f"Received PayFast IPN data: {ipn_data}")

    def handle_payment_status(self, ipn_data: Dict[str, str]):
        """
        Handles the processing of payment status updates from PayFast via IPN.

        :param ipn_data: The received IPN data from PayFast, including the payment status.
        """
        self.log_ipn_data(ipn_data)

        # Handle the status of the payment based on the IPN data
        payment_status = ipn_data.get("payment_status", "").lower()
        payment_id = ipn_data.get("pf_payment_id", "")

        if payment_status == "complete":
            self._process_successful_payment(payment_id, ipn_data)
        elif payment_status == "failed":
            self._process_failed_payment(payment_id, ipn_data)
        else:
            app.logger.warning(f"Unknown payment status for payment {payment_id}: {payment_status}")

    def _process_successful_payment(self, payment_id: str, ipn_data: Dict[str, str]):
        """
        Processes a successful payment and updates user accounts or services accordingly.

        :param payment_id: The PayFast payment ID for this transaction.
        :param ipn_data: The IPN data received from PayFast containing payment details.
        """
        try:
            # Example: Update user account or grant access to paid features (RLG Data/RLG Fans integration)
            user_id = ipn_data.get("custom_str1", "")  # You can use custom fields to associate with your system

            if user_id:
                # Example: Update payment status in the database
                user = User.query.filter_by(id=user_id).first()
                if user:
                    user.payment_status = "completed"
                    user.payment_id = payment_id
                    user.save()  # Assuming you have a method to save updates in the database
                    app.logger.info(f"Payment {payment_id} completed successfully for user {user_id}")
                else:
                    app.logger.warning(f"User {user_id} not found for payment {payment_id}")
        except Exception as e:
            app.logger.error(f"Error processing successful payment {payment_id}: {e}")

    def _process_failed_payment(self, payment_id: str, ipn_data: Dict[str, str]):
        """
        Handles a failed payment and performs any necessary clean-up.

        :param payment_id: The PayFast payment ID for this transaction.
        :param ipn_data: The IPN data received from PayFast.
        """
        try:
            # Example: Update payment status to failed and notify user
            user_id = ipn_data.get("custom_str1", "")  # You can use custom fields to associate with your system

            if user_id:
                user = User.query.filter_by(id=user_id).first()
                if user:
                    user.payment_status = "failed"
                    user.payment_id = payment_id
                    user.save()  # Assuming you have a method to save updates in the database
                    app.logger.info(f"Payment {payment_id} failed for user {user_id}")
                else:
                    app.logger.warning(f"User {user_id} not found for failed payment {payment_id}")
        except Exception as e:
            app.logger.error(f"Error processing failed payment {payment_id}: {e}")

