import hashlib
import random
import string
import json
from datetime import datetime
from cryptography.fernet import Fernet
from .config import ANONYMIZATION_KEY, DATA_FIELDS_TO_ANONYMIZE, HASH_SALT

# Initialize Fernet key for encryption/decryption
fernet = Fernet(ANONYMIZATION_KEY)

# List of fields to anonymize (e.g., email, phone number, IP address, etc.)
# This can be adjusted based on the data model used in both RLG Data and RLG Fans.
# Example: fields such as email, phone_number, and address might be included.
FIELDS_TO_ANONYMIZE = DATA_FIELDS_TO_ANONYMIZE if DATA_FIELDS_TO_ANONYMIZE else ['email', 'phone_number', 'address', 'name']

def generate_random_string(length=16):
    """
    Generate a random string to replace sensitive data (for anonymization purposes).
    """
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))

def hash_value(value: str):
    """
    Hash the value to anonymize sensitive data using SHA-256 with a salt for extra security.
    """
    value_with_salt = value + HASH_SALT
    hashed_value = hashlib.sha256(value_with_salt.encode('utf-8')).hexdigest()
    return hashed_value

def encrypt_value(value: str):
    """
    Encrypt a value using the Fernet symmetric encryption.
    """
    encrypted_value = fernet.encrypt(value.encode('utf-8'))
    return encrypted_value.decode('utf-8')

def anonymize_field(field_name: str, field_value: str):
    """
    Anonymize the value of a field based on the field name. Different strategies can be applied for different fields.
    """
    if field_name in FIELDS_TO_ANONYMIZE:
        if field_name == 'email':
            # Example: Anonymizing email by generating a random string and hashing it
            return hash_value(field_value)
        elif field_name == 'phone_number':
            # Example: Anonymizing phone numbers by encrypting them
            return encrypt_value(field_value)
        elif field_name == 'name':
            # Anonymizing names by replacing them with random strings
            return generate_random_string()
        else:
            # Default strategy for other fields is to hash the value
            return hash_value(field_value)
    else:
        # If field is not in the anonymization list, return the original value
        return field_value

def anonymize_data(data: dict):
    """
    Anonymize all sensitive fields in the provided data.
    """
    anonymized_data = {}
    for field_name, field_value in data.items():
        anonymized_data[field_name] = anonymize_field(field_name, field_value)
    return anonymized_data

def anonymize_user_data(user_data: dict):
    """
    Anonymize user data fields to ensure privacy while retaining some data structure for processing.
    """
    anonymized_data = anonymize_data(user_data)
    return anonymized_data

def anonymize_log_data(log_data: list):
    """
    Anonymize sensitive fields in a list of log data.
    """
    anonymized_logs = []
    for log_entry in log_data:
        anonymized_log_entry = anonymize_data(log_entry)
        anonymized_logs.append(anonymized_log_entry)
    return anonymized_logs

def anonymize_database_records(database_records: list):
    """
    Anonymize all sensitive data in database records.
    """
    anonymized_records = []
    for record in database_records:
        anonymized_record = anonymize_data(record)
        anonymized_records.append(anonymized_record)
    return anonymized_records

def anonymize_data_from_file(file_path: str):
    """
    Anonymize user data from a file (e.g., JSON or CSV).
    """
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        anonymized_data = anonymize_data(data)
        return anonymized_data
    except Exception as e:
        raise ValueError(f"Error reading or anonymizing data from file {file_path}: {e}")

# Utility to check anonymized data consistency (for auditing purposes)
def check_anonymization_consistency(original_data: dict, anonymized_data: dict):
    """
    Check whether the anonymized data is consistent in structure and that sensitive data is properly anonymized.
    """
    if len(original_data) != len(anonymized_data):
        raise ValueError("Anonymized data does not match the original data structure.")
    
    for field_name in original_data:
        if field_name in FIELDS_TO_ANONYMIZE:
            if original_data[field_name] == anonymized_data[field_name]:
                raise ValueError(f"Field '{field_name}' was not properly anonymized.")
    return True

def log_anonymization_process(user_data: dict, anonymized_data: dict, file_name: str):
    """
    Log the anonymization process for auditing and troubleshooting.
    """
    try:
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = {
            'timestamp': timestamp,
            'original_data': user_data,
            'anonymized_data': anonymized_data,
            'file': file_name
        }
        log_file_path = '/var/log/rlg_data_fans_anonymization.log'  # Change this to your desired log file path
        with open(log_file_path, 'a') as log_file:
            log_file.write(json.dumps(log_entry) + "\n")
        print(f"Anonymization process logged to {log_file_path}.")
    except Exception as e:
        print(f"Error logging anonymization process: {e}")

def anonymize_and_log(user_data: dict, file_name: str):
    """
    Anonymize user data and log the process for auditing purposes.
    """
    anonymized_data = anonymize_user_data(user_data)
    log_anonymization_process(user_data, anonymized_data, file_name)
    return anonymized_data

# Example Usage:
if __name__ == "__main__":
    # Example user data
    user_data_example = {
        'email': 'user@example.com',
        'phone_number': '1234567890',
        'name': 'John Doe',
        'address': '123 Main St, Anytown, USA'
    }

    # Perform anonymization and logging
    anonymized_data = anonymize_and_log(user_data_example, 'user_data_example.json')
    print("Anonymized Data:", anonymized_data)
