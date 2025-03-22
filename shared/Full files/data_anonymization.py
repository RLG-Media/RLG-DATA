# data_anonymization.py

import logging
import pandas as pd
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

class DataAnonymization:
    """
    Class to handle data anonymization techniques including 
    data masking, encryption, and de-identification.
    """

    def __init__(self, encryption_key=None):
        self.encryption_key = encryption_key or Fernet.generate_key()
        self.fernet = Fernet(self.encryption_key)

    def mask_data(self, df, columns_to_mask):
        """
        Masks sensitive data in specified columns using random strings.
        """
        try:
            logger.info("Masking sensitive data.")
            masked_df = df.copy()
            for column in columns_to_mask:
                if column in masked_df.columns:
                    masked_df[column] = masked_df[column].apply(lambda x: f"MASKED_{hash(x)}")
            return masked_df
        except Exception as e:
            logger.error(f"Error masking data: {e}")
            raise

    def encode_categorical_data(self, df, columns_to_encode):
        """
        Encodes categorical data using Label Encoding.
        """
        try:
            logger.info("Encoding categorical data.")
            encoded_df = df.copy()
            for column in columns_to_encode:
                if column in encoded_df.columns:
                    le = LabelEncoder()
                    encoded_df[column] = le.fit_transform(encoded_df[column])
            return encoded_df
        except Exception as e:
            logger.error(f"Error encoding categorical data: {e}")
            raise

    def scale_numerical_data(self, df, columns_to_scale):
        """
        Scales numerical data using Min-Max Scaling.
        """
        try:
            logger.info("Scaling numerical data.")
            scaled_df = df.copy()
            scaler = MinMaxScaler()
            for column in columns_to_scale:
                if column in scaled_df.columns:
                    scaled_df[column] = scaler.fit_transform(scaled_df[[column]])
            return scaled_df
        except Exception as e:
            logger.error(f"Error scaling numerical data: {e}")
            raise

    def encrypt_data(self, df, columns_to_encrypt):
        """
        Encrypts specified columns using Fernet encryption.
        """
        try:
            logger.info("Encrypting data.")
            encrypted_df = df.copy()
            for column in columns_to_encrypt:
                if column in encrypted_df.columns:
                    encrypted_df[column] = encrypted_df[column].apply(lambda x: self.fernet.encrypt(x.encode()).decode())
            return encrypted_df
        except Exception as e:
            logger.error(f"Error encrypting data: {e}")
            raise

    def decrypt_data(self, df, columns_to_decrypt):
        """
        Decrypts encrypted columns using Fernet encryption.
        """
        try:
            logger.info("Decrypting data.")
            decrypted_df = df.copy()
            for column in columns_to_decrypt:
                if column in decrypted_df.columns:
                    decrypted_df[column] = decrypted_df[column].apply(lambda x: self.fernet.decrypt(x.encode()).decode())
            return decrypted_df
        except Exception as e:
            logger.error(f"Error decrypting data: {e}")
            raise

# Example Usage
"""
import pandas as pd

# Sample data
data = {
    'Name': ['Alice', 'Bob', 'Charlie'],
    'Email': ['alice@example.com', 'bob@example.com', 'charlie@example.com'],
    'Age': [25, 30, 35],
    'Salary': [50000, 60000, 70000]
}

df = pd.DataFrame(data)

anonymizer = DataAnonymization()

# Masking sensitive columns
masked_data = anonymizer.mask_data(df, ['Email'])

# Encoding categorical columns
encoded_data = anonymizer.encode_categorical_data(df, ['Name'])

# Scaling numerical columns
scaled_data = anonymizer.scale_numerical_data(df, ['Age', 'Salary'])

# Encrypting sensitive columns
encrypted_data = anonymizer.encrypt_data(df, ['Email'])

# Decrypting sensitive columns (for verification)
decrypted_data = anonymizer.decrypt_data(encrypted_data, ['Email'])

print("Masked Data:")
print(masked_data)

print("\nEncoded Data:")
print(encoded_data)

print("\nScaled Data:")
print(scaled_data)

print("\nEncrypted Data:")
print(encrypted_data)

print("\nDecrypted Data:")
print(decrypted_data)
"""
