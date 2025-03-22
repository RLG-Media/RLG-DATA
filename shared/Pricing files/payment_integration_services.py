import requests
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from shared.config import (
    PAYMENT_GATEWAY_API_URL,
    PAYMENT_GATEWAY_API_KEY,
    PAYFAST_MERCHANT_ID,
    PAYFAST_MERCHANT_KEY,
    PAYFAST_PASSPHRASE
)
from shared.utils import log_info, log_error, validate_api_response

# Configure logging (if not already configured globally)
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class PaymentIntegrationService:
    """
    Service class for integrating payment processing, refunds, status checks, and invoice generation.
    This service supports both a generic payment gateway and additional PayFast-specific parameters.
    Designed for use in RLG Data and RLG Fans.
    """

    def __init__(self) -> None:
        """
        Initialize the PaymentIntegrationService using configuration values from shared settings.
        
        Raises:
            ValueError: If critical configuration values are missing.
        """
        # Ensure required configuration values are provided.
        if not PAYMENT_GATEWAY_API_URL or not PAYMENT_GATEWAY_API_KEY:
            raise ValueError("Payment gateway API URL and API key must be provided in the configuration.")
        if not PAYFAST_MERCHANT_ID or not PAYFAST_MERCHANT_KEY or not PAYFAST_PASSPHRASE:
            raise ValueError("PayFast credentials (merchant ID, merchant key, passphrase) must be provided.")

        self.api_url: str = PAYMENT_GATEWAY_API_URL
        self.api_key: str = PAYMENT_GATEWAY_API_KEY
        self.payfast_merchant_id: str = PAYFAST_MERCHANT_ID
        self.payfast_merchant_key: str = PAYFAST_MERCHANT_KEY
        self.payfast_passphrase: str = PAYFAST_PASSPHRASE
        logger.info("PaymentIntegrationService initialized successfully.")

    def _get_headers(self) -> Dict[str, str]:
        """
        Construct the HTTP headers for payment gateway requests.
        
        Returns:
            Dict[str, str]: Headers including Authorization.
        """
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def process_payment(self, amount: float, currency: str, customer: Dict[str, Any],
                        region: Optional[str] = None, country: Optional[str] = None,
                        city: Optional[str] = None, town: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Process a payment through the payment gateway, including PayFast-specific parameters.
        
        Args:
            amount (float): The total amount to charge.
            currency (str): The currency code (e.g., 'USD').
            customer (Dict[str, Any]): Customer details (e.g., name, email).
            region (Optional[str]): Geographic region.
            country (Optional[str]): Country code.
            city (Optional[str]): City name.
            town (Optional[str]): Town name.
        
        Returns:
            Optional[Dict[str, Any]]: API response with payment details, or None if an error occurs.
        """
        url = f"{self.api_url}/payments"
        headers = self._get_headers()
        
        # Build the payload with both generic and PayFast-specific parameters.
        payload = {
            "amount": amount,
            "currency": currency,
            "customer": customer,
            "timestamp": datetime.utcnow().isoformat(),
            # Optional geographic filters:
            "region": region,
            "country": country,
            "city": city,
            "town": town,
            # PayFast-specific parameters:
            "payfast": {
                "merchant_id": self.payfast_merchant_id,
                "merchant_key": self.payfast_merchant_key,
                "passphrase": self.payfast_passphrase
            }
        }
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            response.raise_for_status()
            if validate_api_response(response):
                log_info("Payment processed successfully for amount: %s %s", amount, currency)
                return response.json()
            else:
                log_error("Invalid API response during payment processing.")
                return None
        except requests.RequestException as e:
            log_error(f"Error processing payment: {e}")
            return None

    def refund_payment(self, payment_id: str, refund_amount: float) -> Optional[Dict[str, Any]]:
        """
        Process a refund for a given payment.
        
        Args:
            payment_id (str): Unique identifier of the payment.
            refund_amount (float): The amount to refund.
        
        Returns:
            Optional[Dict[str, Any]]: API response with refund details, or None if an error occurs.
        """
        url = f"{self.api_url}/payments/{payment_id}/refund"
        headers = self._get_headers()
        payload = {"refund_amount": refund_amount}

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            response.raise_for_status()
            if validate_api_response(response):
                log_info("Refund processed successfully for payment ID: %s", payment_id)
                return response.json()
            else:
                log_error("Invalid API response during refund processing.")
                return None
        except requests.RequestException as e:
            log_error(f"Error processing refund for payment ID {payment_id}: {e}")
            return None

    def get_payment_status(self, payment_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve the status of a specific payment.
        
        Args:
            payment_id (str): The unique identifier of the payment.
        
        Returns:
            Optional[Dict[str, Any]]: Payment status information or None if an error occurs.
        """
        url = f"{self.api_url}/payments/{payment_id}/status"
        headers = self._get_headers()

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            log_info("Retrieved status for payment ID: %s", payment_id)
            return response.json()
        except requests.RequestException as e:
            log_error(f"Error retrieving payment status for payment ID {payment_id}: {e}")
            return None

    def generate_invoice(self, payment_details: Dict[str, Any]) -> Optional[bytes]:
        """
        Generate an invoice for a payment.
        
        Args:
            payment_details (Dict[str, Any]): Details about the payment (e.g., customer info, amount, date).
        
        Returns:
            Optional[bytes]: The generated invoice as a PDF in bytes, or None if an error occurs.
        """
        # For this example, we'll simulate generating a PDF invoice.
        # In production, you might integrate with a PDF generation library (like ReportLab) or a microservice.
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
            import io

            buffer = io.BytesIO()
            pdf = canvas.Canvas(buffer, pagesize=letter)
            pdf.setTitle("Invoice")
            pdf.setFont("Helvetica-Bold", 16)
            pdf.drawString(100, 750, "Invoice")
            pdf.setFont("Helvetica", 12)
            pdf.drawString(100, 720, f"Customer: {payment_details.get('customer', {}).get('name', 'N/A')}")
            pdf.drawString(100, 700, f"Amount: {payment_details.get('amount', 'N/A')} {payment_details.get('currency', '')}")
            pdf.drawString(100, 680, f"Date: {payment_details.get('date', datetime.utcnow().isoformat())}")
            pdf.showPage()
            pdf.save()
            buffer.seek(0)
            log_info("Invoice generated successfully.")
            return buffer.getvalue()
        except Exception as e:
            log_error(f"Error generating invoice: {e}")
            return None

# -------------------------------
# Example Usage (for testing purposes)
# -------------------------------
if __name__ == "__main__":
    # Initialize PaymentIntegrationService with configuration from shared settings.
    payment_service = PaymentIntegrationService()

    # Example: Process a payment.
    payment_response = payment_service.process_payment(
        amount=100.0,
        currency="USD",
        customer={"name": "John Doe", "email": "john@example.com"},
        region="North America",
        country="USA",
        city="New York",
        town="Manhattan"
    )
    if payment_response:
        print("Payment Response:", payment_response)
    else:
        print("Payment processing failed.")

    # Example: Refund a payment.
    refund_response = payment_service.refund_payment(payment_id="pay_123456", refund_amount=50.0)
    if refund_response:
        print("Refund Response:", refund_response)
    else:
        print("Refund processing failed.")

    # Example: Get payment status.
    status_response = payment_service.get_payment_status(payment_id="pay_123456")
    if status_response:
        print("Payment Status:", status_response)
    else:
        print("Failed to retrieve payment status.")

    # Example: Generate an invoice.
    invoice_bytes = payment_service.generate_invoice({
        "customer": {"name": "John Doe"},
        "amount": 100.0,
        "currency": "USD",
        "date": "2024-01-01"
    })
    if invoice_bytes:
        with open("invoice.pdf", "wb") as f:
            f.write(invoice_bytes)
        print("Invoice generated and saved as 'invoice.pdf'.")
    else:
        print("Invoice generation failed.")
