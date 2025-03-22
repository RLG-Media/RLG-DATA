import os
import hashlib
import hmac
import base64
from cryptography.fernet import Fernet
from datetime import datetime, timedelta

# Secret Key for cryptography and secure hashing
SECRET_KEY = os.getenv('SECRET_KEY', Fernet.generate_key().decode())

# HMAC-SHA256 Hashing Function
def generate_hmac(data, key=SECRET_KEY):
    return hmac.new(key.encode(), data.encode(), hashlib.sha256).hexdigest()

# Password Hashing using PBKDF2 (Password-Based Key Derivation Function)
def hash_password(password, salt=None, iterations=100000):
    if salt is None:
        salt = os.urandom(16)
    hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, iterations)
    return base64.b64encode(salt + hashed_password).decode()

# Password Verification
def verify_password(stored_password, provided_password):
    stored_password_bytes = base64.b64decode(stored_password)
    salt = stored_password_bytes[:16]
    iterations = 100000
    hash_to_check = hashlib.pbkdf2_hmac('sha256', provided_password.encode(), salt, iterations)
    return hmac.compare_digest(stored_password_bytes[16:], hash_to_check)

# JWT Token Generation
def generate_jwt(payload, secret_key=SECRET_KEY, expiration=3600):
    # Create JWT token with payload and expiration
    header = {
        "alg": "HS256",
        "typ": "JWT"
    }
    now = datetime.utcnow()
    exp = now + timedelta(seconds=expiration)

    payload.update({
        "iat": now,
        "exp": exp,
    })

    encoded_header = base64.urlsafe_b64encode(str(header).encode()).rstrip(b'=')
    encoded_payload = base64.urlsafe_b64encode(str(payload).encode()).rstrip(b'=')

    signature = hmac.new(secret_key.encode(), encoded_header + b"." + encoded_payload, hashlib.sha256).digest()
    encoded_signature = base64.urlsafe_b64encode(signature).rstrip(b'=')

    jwt_token = encoded_header + b"." + encoded_payload + b"." + encoded_signature
    return jwt_token.decode()

# JWT Token Decoding
def decode_jwt(jwt_token, secret_key=SECRET_KEY):
    try:
        encoded_header, encoded_payload, encoded_signature = jwt_token.split('.')

        header = eval(base64.urlsafe_b64decode(encoded_header + '=' * (4 - len(encoded_header) % 4)).decode())
        payload = eval(base64.urlsafe_b64decode(encoded_payload + '=' * (4 - len(encoded_payload) % 4)).decode())

        signature = base64.urlsafe_b64decode(encoded_signature + '=' * (4 - len(encoded_signature) % 4))

        # Verify signature
        expected_signature = hmac.new(secret_key.encode(), encoded_header.encode() + b"." + encoded_payload.encode(), hashlib.sha256).digest()
        if not hmac.compare_digest(signature, expected_signature):
            raise ValueError("Invalid token")

        return payload
    except Exception as e:
        raise ValueError("Invalid token") from e

# Two-Factor Authentication (Example using TOTP)
import pyotp

def generate_totp(secret):
    totp = pyotp.TOTP(secret)
    return totp.now()

def verify_totp(secret, token):
    totp = pyotp.TOTP(secret)
    return totp.verify(token)

# Password Reset Token (Example with expiration)
def generate_password_reset_token(user_id, secret_key=SECRET_KEY, expiration=3600):
    now = datetime.utcnow()
    exp = now + timedelta(seconds=expiration)
    data = f"{user_id}-{exp.isoformat()}"
    return hmac.new(secret_key.encode(), data.encode(), hashlib.sha256).hexdigest()

def verify_password_reset_token(token, user_id, secret_key=SECRET_KEY):
    try:
        decoded_data = hmac.new(secret_key.encode(), token.encode(), hashlib.sha256).hexdigest()
        decoded_user_id, exp_iso = decoded_data.split('-')
        exp = datetime.fromisoformat(exp_iso)
        if decoded_user_id == user_id and exp > datetime.utcnow():
            return True
    except Exception as e:
        return False
    return False

# Token expiration handling
def is_token_expired(expiration_time):
    return datetime.utcnow() > expiration_time

# Encrypt and Decrypt using Fernet (symmetric encryption)
def encrypt_data(data):
    fernet = Fernet(SECRET_KEY)
    encrypted_data = fernet.encrypt(data.encode())
    return encrypted_data

def decrypt_data(encrypted_data):
    fernet = Fernet(SECRET_KEY)
    decrypted_data = fernet.decrypt(encrypted_data).decode()
    return decrypted_data

# Secure Storage Example: Example of securely storing sensitive data
def secure_store(data, key):
    encrypted_data = encrypt_data(data)
    # Store encrypted_data securely (e.g., database, secure cloud storage)
    return encrypted_data

def secure_retrieve(encrypted_data, key):
    return decrypt_data(encrypted_data)
