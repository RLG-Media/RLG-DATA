import os
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import padding
from base64 import b64encode, b64decode
import logging

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Constants
SALT_SIZE = 16  # Size of the salt in bytes
KEY_SIZE = 32  # Size of the encryption key (256 bits)
IV_SIZE = 16  # Size of the initialization vector (128 bits)
RSA_KEY_SIZE = 2048  # Size of RSA key for asymmetric encryption
PBKDF2_ITERATIONS = 100000  # Number of iterations for PBKDF2

# Utility functions for encryption/decryption


def generate_salt():
    """Generate a random salt."""
    salt = os.urandom(SALT_SIZE)
    logger.debug(f"Generated salt: {b64encode(salt).decode()}")
    return salt


def derive_key(password: str, salt: bytes) -> bytes:
    """Derive a key using PBKDF2 with the given password and salt."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_SIZE,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
        backend=default_backend()
    )
    key = kdf.derive(password.encode())
    logger.debug(f"Derived key: {b64encode(key).decode()}")
    return key


def encrypt_data(key: bytes, data: str) -> dict:
    """Encrypt data using AES (GCM mode)."""
    # Generate a random IV (Initialization Vector)
    iv = os.urandom(IV_SIZE)
    # Padding the data to ensure it's a multiple of the block size
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data.encode()) + padder.finalize()

    cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    tag = encryptor.tag

    logger.debug(f"Encrypted data: {b64encode(encrypted_data).decode()}")
    return {
        "iv": b64encode(iv).decode(),
        "encrypted_data": b64encode(encrypted_data).decode(),
        "tag": b64encode(tag).decode()
    }


def decrypt_data(key: bytes, encrypted_data: dict) -> str:
    """Decrypt data using AES (GCM mode)."""
    iv = b64decode(encrypted_data["iv"])
    encrypted_data_bytes = b64decode(encrypted_data["encrypted_data"])
    tag = b64decode(encrypted_data["tag"])

    cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_padded_data = decryptor.update(encrypted_data_bytes) + decryptor.finalize()

    # Unpad the decrypted data
    unpadder = padding.PKCS7(128).unpadder()
    decrypted_data = unpadder.update(decrypted_padded_data) + unpadder.finalize()

    logger.debug(f"Decrypted data: {decrypted_data.decode()}")
    return decrypted_data.decode()


def generate_rsa_keys() -> dict:
    """Generate RSA private and public keys."""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=RSA_KEY_SIZE,
        backend=default_backend()
    )

    public_key = private_key.public_key()

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )

    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    logger.debug(f"Generated RSA public key: {b64encode(public_pem).decode()}")
    logger.debug(f"Generated RSA private key: {b64encode(private_pem).decode()}")
    return {
        "private_key": private_pem,
        "public_key": public_pem
    }


def encrypt_with_rsa(public_key_pem: bytes, data: str) -> str:
    """Encrypt data using RSA public key."""
    public_key = serialization.load_pem_public_key(public_key_pem, backend=default_backend())
    encrypted_data = public_key.encrypt(
        data.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    encrypted_b64 = b64encode(encrypted_data).decode()
    logger.debug(f"Encrypted data with RSA: {encrypted_b64}")
    return encrypted_b64


def decrypt_with_rsa(private_key_pem: bytes, encrypted_data: str) -> str:
    """Decrypt data using RSA private key."""
    private_key = serialization.load_pem_private_key(private_key_pem, password=None, backend=default_backend())
    encrypted_data_bytes = b64decode(encrypted_data)
    decrypted_data = private_key.decrypt(
        encrypted_data_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    logger.debug(f"Decrypted data with RSA: {decrypted_data.decode()}")
    return decrypted_data.decode()


def store_encrypted_data(data: dict, storage_path: str) -> None:
    """Store encrypted data to a file."""
    try:
        with open(storage_path, "w") as file:
            file.write(str(data))
        logger.info(f"Encrypted data stored at {storage_path}")
    except Exception as e:
        logger.error(f"Error storing encrypted data: {str(e)}")


def load_encrypted_data(storage_path: str) -> dict:
    """Load encrypted data from a file."""
    try:
        with open(storage_path, "r") as file:
            data = file.read()
        logger.info(f"Encrypted data loaded from {storage_path}")
        return eval(data)
    except Exception as e:
        logger.error(f"Error loading encrypted data: {str(e)}")
        return {}


if __name__ == "__main__":
    # Example usage
    password = "strongpassword123"
    salt = generate_salt()
    key = derive_key(password, salt)

    # Encrypt and decrypt a string
    data_to_encrypt = "Sensitive data to be encrypted"
    encrypted = encrypt_data(key, data_to_encrypt)
    decrypted = decrypt_data(key, encrypted)

    logger.info(f"Decrypted data: {decrypted}")
    
    # Generate RSA keys and perform encryption/decryption
    rsa_keys = generate_rsa_keys()
    rsa_encrypted = encrypt_with_rsa(rsa_keys["public_key"], data_to_encrypt)
    rsa_decrypted = decrypt_with_rsa(rsa_keys["private_key"], rsa_encrypted)
    
    logger.info(f"RSA Decrypted data: {rsa_decrypted}")
