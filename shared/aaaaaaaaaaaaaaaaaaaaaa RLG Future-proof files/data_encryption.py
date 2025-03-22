import os
import base64
import json
import logging
from hashlib import sha256
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
from config import ENCRYPTION_CONFIG

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load encryption settings
AES_SALT = ENCRYPTION_CONFIG.get("aes_salt", os.urandom(16))
AES_ITERATIONS = ENCRYPTION_CONFIG.get("aes_iterations", 100000)
RSA_KEY_SIZE = ENCRYPTION_CONFIG.get("rsa_key_size", 2048)

class DataEncryption:
    """Implements secure encryption and decryption for RLG Data and RLG Fans."""

    def __init__(self):
        self.rsa_private_key, self.rsa_public_key = self.generate_rsa_keys()

    def generate_aes_key(self, password: str) -> bytes:
        """Generates a 256-bit AES key using PBKDF2."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=AES_SALT,
            iterations=AES_ITERATIONS,
            backend=default_backend()
        )
        return kdf.derive(password.encode())

    def encrypt_data(self, data: dict, password: str) -> dict:
        """Encrypts data using AES-256 with CBC mode and HMAC for integrity verification."""
        aes_key = self.generate_aes_key(password)
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()

        # Serialize and pad data
        json_data = json.dumps(data)
        padded_data = json_data + (16 - len(json_data) % 16) * " "
        encrypted_bytes = encryptor.update(padded_data.encode()) + encryptor.finalize()

        # Generate HMAC for integrity
        hmac = sha256(aes_key + encrypted_bytes).hexdigest()

        return {
            "iv": base64.b64encode(iv).decode(),
            "ciphertext": base64.b64encode(encrypted_bytes).decode(),
            "hmac": hmac
        }

    def decrypt_data(self, encrypted_data: dict, password: str) -> dict:
        """Decrypts AES-256 encrypted data and verifies integrity with HMAC."""
        aes_key = self.generate_aes_key(password)
        iv = base64.b64decode(encrypted_data["iv"])
        ciphertext = base64.b64decode(encrypted_data["ciphertext"])

        # Verify HMAC
        expected_hmac = sha256(aes_key + ciphertext).hexdigest()
        if expected_hmac != encrypted_data["hmac"]:
            raise ValueError("HMAC integrity check failed! Data may be corrupted.")

        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()

        return json.loads(decrypted_data.decode().strip())

    def generate_rsa_keys(self):
        """Generates RSA key pair for hybrid encryption."""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=RSA_KEY_SIZE,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        return private_key, public_key

    def encrypt_aes_key(self, aes_key: bytes) -> str:
        """Encrypts AES key using RSA public key."""
        encrypted_key = self.rsa_public_key.encrypt(
            aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return base64.b64encode(encrypted_key).decode()

    def decrypt_aes_key(self, encrypted_aes_key: str) -> bytes:
        """Decrypts AES key using RSA private key."""
        decrypted_key = self.rsa_private_key.decrypt(
            base64.b64decode(encrypted_aes_key),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return decrypted_key

    def serialize_keys(self):
        """Serializes RSA keys for secure storage."""
        private_pem = self.rsa_private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )
        public_pem = self.rsa_public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return private_pem.decode(), public_pem.decode()


# Initialize Data Encryption Service
encryption_service = DataEncryption()

# Example Usage
if __name__ == "__main__":
    sample_data = {"user_id": 123, "email": "user@example.com", "balance": 5000}
    password = "secure_password"

    # Encrypt Data
    encrypted_payload = encryption_service.encrypt_data(sample_data, password)
    logging.info(f"Encrypted Data: {encrypted_payload}")

    # Decrypt Data
    decrypted_data = encryption_service.decrypt_data(encrypted_payload, password)
    logging.info(f"Decrypted Data: {decrypted_data}")

    # Encrypt AES Key using RSA
    aes_key = encryption_service.generate_aes_key(password)
    encrypted_aes_key = encryption_service.encrypt_aes_key(aes_key)
    logging.info(f"Encrypted AES Key: {encrypted_aes_key}")

    # Decrypt AES Key
    decrypted_aes_key = encryption_service.decrypt_aes_key(encrypted_aes_key)
    logging.info(f"Decrypted AES Key Matches: {aes_key == decrypted_aes_key}")
