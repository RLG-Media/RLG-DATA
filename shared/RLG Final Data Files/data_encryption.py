import os
import base64
import logging
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.keywrap import aes_key_wrap, aes_key_unwrap
from cryptography.hazmat.primitives.hmac import HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import (
    load_pem_private_key,
    load_pem_public_key,
    Encoding,
    PrivateFormat,
    PublicFormat,
    NoEncryption,
)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class DataEncryptionManager:
    """
    Manages encryption and decryption for RLG Data and RLG Fans.
    Supports symmetric, asymmetric, and hybrid encryption.
    """

    def __init__(self, key_length: int = 256):
        """
        Initializes the encryption manager.
        :param key_length: Length of the symmetric key in bits (default: 256).
        """
        self.key_length = key_length // 8  # Convert bits to bytes
        self.backend = default_backend()

    # --- Symmetric Encryption (AES) ---
    def generate_symmetric_key(self):
        """
        Generates a symmetric AES key.
        :return: The generated AES key.
        """
        key = os.urandom(self.key_length)
        logging.info("Symmetric AES key generated.")
        return key

    def encrypt_symmetric(self, data: bytes, key: bytes):
        """
        Encrypts data using AES symmetric encryption.
        :param data: Data to be encrypted.
        :param key: Symmetric AES key.
        :return: Encrypted data with IV prepended.
        """
        iv = os.urandom(16)  # 16-byte IV for AES
        cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=self.backend)
        encryptor = cipher.encryptor()
        encrypted_data = encryptor.update(data) + encryptor.finalize()
        return iv + encrypted_data  # Prepend IV for decryption

    def decrypt_symmetric(self, encrypted_data: bytes, key: bytes):
        """
        Decrypts data encrypted with AES symmetric encryption.
        :param encrypted_data: Encrypted data with IV prepended.
        :param key: Symmetric AES key.
        :return: Decrypted data.
        """
        iv = encrypted_data[:16]  # Extract IV
        encrypted_payload = encrypted_data[16:]
        cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=self.backend)
        decryptor = cipher.decryptor()
        return decryptor.update(encrypted_payload) + decryptor.finalize()

    # --- Asymmetric Encryption (RSA) ---
    def generate_rsa_key_pair(self):
        """
        Generates an RSA public/private key pair.
        :return: A tuple of (private_key, public_key).
        """
        private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=2048, backend=self.backend
        )
        public_key = private_key.public_key()
        logging.info("RSA key pair generated.")
        return private_key, public_key

    def encrypt_asymmetric(self, data: bytes, public_key):
        """
        Encrypts data using RSA public key encryption.
        :param data: Data to be encrypted.
        :param public_key: RSA public key.
        :return: Encrypted data.
        """
        encrypted_data = public_key.encrypt(
            data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        logging.info("Data encrypted with RSA public key.")
        return encrypted_data

    def decrypt_asymmetric(self, encrypted_data: bytes, private_key):
        """
        Decrypts data encrypted with RSA public key encryption.
        :param encrypted_data: Encrypted data.
        :param private_key: RSA private key.
        :return: Decrypted data.
        """
        decrypted_data = private_key.decrypt(
            encrypted_data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        logging.info("Data decrypted with RSA private key.")
        return decrypted_data

    # --- Hybrid Encryption ---
    def hybrid_encrypt(self, data: bytes, public_key):
        """
        Encrypts data using a hybrid approach (AES + RSA).
        :param data: Data to be encrypted.
        :param public_key: RSA public key for wrapping the AES key.
        :return: A dictionary with 'encrypted_key' and 'encrypted_data'.
        """
        aes_key = self.generate_symmetric_key()
        encrypted_data = self.encrypt_symmetric(data, aes_key)
        encrypted_key = self.encrypt_asymmetric(aes_key, public_key)
        logging.info("Data encrypted using hybrid encryption.")
        return {"encrypted_key": encrypted_key, "encrypted_data": encrypted_data}

    def hybrid_decrypt(self, encrypted_package: dict, private_key):
        """
        Decrypts data encrypted with a hybrid approach (AES + RSA).
        :param encrypted_package: Dictionary with 'encrypted_key' and 'encrypted_data'.
        :param private_key: RSA private key for unwrapping the AES key.
        :return: Decrypted data.
        """
        aes_key = self.decrypt_asymmetric(encrypted_package["encrypted_key"], private_key)
        decrypted_data = self.decrypt_symmetric(encrypted_package["encrypted_data"], aes_key)
        logging.info("Data decrypted using hybrid encryption.")
        return decrypted_data

    # --- File Encryption ---
    def encrypt_file(self, file_path: str, key: bytes):
        """
        Encrypts a file using AES symmetric encryption.
        :param file_path: Path to the file to be encrypted.
        :param key: Symmetric AES key.
        :return: Path to the encrypted file.
        """
        with open(file_path, "rb") as file:
            data = file.read()
        encrypted_data = self.encrypt_symmetric(data, key)
        encrypted_file_path = f"{file_path}.enc"
        with open(encrypted_file_path, "wb") as encrypted_file:
            encrypted_file.write(encrypted_data)
        logging.info(f"File encrypted: {encrypted_file_path}")
        return encrypted_file_path

    def decrypt_file(self, encrypted_file_path: str, key: bytes):
        """
        Decrypts a file encrypted with AES symmetric encryption.
        :param encrypted_file_path: Path to the encrypted file.
        :param key: Symmetric AES key.
        :return: Path to the decrypted file.
        """
        with open(encrypted_file_path, "rb") as encrypted_file:
            encrypted_data = encrypted_file.read()
        decrypted_data = self.decrypt_symmetric(encrypted_data, key)
        decrypted_file_path = encrypted_file_path.rstrip(".enc")
        with open(decrypted_file_path, "wb") as decrypted_file:
            decrypted_file.write(decrypted_data)
        logging.info(f"File decrypted: {decrypted_file_path}")
        return decrypted_file_path


# Example Usage
if __name__ == "__main__":
    manager = DataEncryptionManager()

    # Symmetric Encryption Example
    aes_key = manager.generate_symmetric_key()
    data = b"Sensitive data for encryption"
    encrypted = manager.encrypt_symmetric(data, aes_key)
    decrypted = manager.decrypt_symmetric(encrypted, aes_key)

    print("Original Data:", data)
    print("Decrypted Data:", decrypted)
