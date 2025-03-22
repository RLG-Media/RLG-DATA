from cryptography.fernet import Fernet
import logging
from typing import Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("data_encryption_services.log"),
        logging.StreamHandler()
    ]
)

class DataEncryptionService:
    """
    Service for encrypting and decrypting sensitive data used in RLG Data and RLG Fans.
    Ensures secure storage and transmission of information across all supported platforms.
    """

    def __init__(self, encryption_key: Union[str, None] = None):
        """
        Initialize the encryption service.

        Args:
            encryption_key (str): Base64 encoded encryption key. Generates a new one if not provided.
        """
        if encryption_key:
            self.key = encryption_key.encode()
            logging.info("Encryption key loaded successfully.")
        else:
            self.key = Fernet.generate_key()
            logging.warning("No encryption key provided. A new key has been generated.")
        
        self.cipher = Fernet(self.key)

    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt a plaintext string.

        Args:
            plaintext (str): The text to encrypt.

        Returns:
            str: The encrypted text in Base64 format.
        """
        try:
            encrypted_text = self.cipher.encrypt(plaintext.encode()).decode()
            logging.info("Data encrypted successfully.")
            return encrypted_text
        except Exception as e:
            logging.error(f"Error encrypting data: {e}")
            raise

    def decrypt(self, encrypted_text: str) -> str:
        """
        Decrypt an encrypted string.

        Args:
            encrypted_text (str): The Base64 encoded encrypted text.

        Returns:
            str: The decrypted plaintext.
        """
        try:
            decrypted_text = self.cipher.decrypt(encrypted_text.encode()).decode()
            logging.info("Data decrypted successfully.")
            return decrypted_text
        except Exception as e:
            logging.error(f"Error decrypting data: {e}")
            raise

    def rotate_key(self):
        """
        Rotate the encryption key and reinitialize the cipher.
        """
        self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)
        logging.info("Encryption key rotated successfully.")

# Example Usage
if __name__ == "__main__":
    # Initialize the encryption service (provide a key or let it generate one)
    service = DataEncryptionService()

    # Example sensitive data
    sensitive_data = "user_password123"

    # Encrypt the data
    encrypted = service.encrypt(sensitive_data)
    print(f"Encrypted: {encrypted}")

    # Decrypt the data
    decrypted = service.decrypt(encrypted)
    print(f"Decrypted: {decrypted}")

    # Rotate the encryption key
    service.rotate_key()
    logging.info("Key rotated. Previously encrypted data cannot be decrypted with the new key.")
