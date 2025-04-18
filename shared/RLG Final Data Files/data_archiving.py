import os
import shutil
import zipfile
import gzip
import tarfile
from pathlib import Path
from datetime import datetime
from typing import Optional
from cryptography.fernet import Fernet


class DataArchiver:
    def __init__(self, archive_dir: str = "./archives", encryption_key: Optional[str] = None):
        """
        Initialize the DataArchiver.

        Args:
            archive_dir (str): Directory where archived files will be stored.
            encryption_key (Optional[str]): Key for encrypting archived files. Generates one if not provided.
        """
        self.archive_dir = archive_dir
        os.makedirs(self.archive_dir, exist_ok=True)

        if encryption_key:
            self.encryption_key = encryption_key.encode()
        else:
            self.encryption_key = Fernet.generate_key()
            print(f"Generated new encryption key: {self.encryption_key.decode()}")

        self.fernet = Fernet(self.encryption_key)

    def compress_file(self, file_path: str, compression_format: str = "zip") -> str:
        """
        Compresses a file using the specified format.

        Args:
            file_path (str): Path to the file to compress.
            compression_format (str): Compression format ('zip', 'gzip', or 'tar.gz'). Defaults to 'zip'.

        Returns:
            str: Path to the compressed file.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        file_name = os.path.basename(file_path)
        archive_name = f"{file_name}.{compression_format}"
        archive_path = os.path.join(self.archive_dir, archive_name)

        if compression_format == "zip":
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(file_path, file_name)
        elif compression_format == "gzip":
            with open(file_path, 'rb') as f_in:
                with gzip.open(archive_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
        elif compression_format == "tar.gz":
            with tarfile.open(archive_path, 'w:gz') as tar:
                tar.add(file_path, arcname=file_name)
        else:
            raise ValueError(f"Unsupported compression format: {compression_format}")

        print(f"Compressed file saved at: {archive_path}")
        return archive_path

    def encrypt_file(self, file_path: str) -> str:
        """
        Encrypts a file using Fernet symmetric encryption.

        Args:
            file_path (str): Path to the file to encrypt.

        Returns:
            str: Path to the encrypted file.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        encrypted_file_path = f"{file_path}.enc"

        with open(file_path, 'rb') as file:
            data = file.read()
            encrypted_data = self.fernet.encrypt(data)

        with open(encrypted_file_path, 'wb') as enc_file:
            enc_file.write(encrypted_data)

        print(f"Encrypted file saved at: {encrypted_file_path}")
        return encrypted_file_path

    def archive_directory(self, directory_path: str, compression_format: str = "zip") -> str:
        """
        Archives an entire directory.

        Args:
            directory_path (str): Path to the directory to archive.
            compression_format (str): Compression format ('zip', 'gzip', or 'tar.gz'). Defaults to 'zip'.

        Returns:
            str: Path to the archived directory.
        """
        if not os.path.exists(directory_path):
            raise FileNotFoundError(f"Directory not found: {directory_path}")

        dir_name = os.path.basename(directory_path.rstrip('/'))
        archive_name = f"{dir_name}.{compression_format}"
        archive_path = os.path.join(self.archive_dir, archive_name)

        if compression_format == "zip":
            shutil.make_archive(archive_path.rstrip('.zip'), 'zip', directory_path)
        elif compression_format == "tar.gz":
            with tarfile.open(archive_path, 'w:gz') as tar:
                tar.add(directory_path, arcname=dir_name)
        else:
            raise ValueError(f"Unsupported compression format for directories: {compression_format}")

        print(f"Archived directory saved at: {archive_path}")
        return archive_path

    def archive_and_encrypt(self, file_or_dir: str, is_directory: bool = False, compression_format: str = "zip") -> str:
        """
        Archives and encrypts a file or directory.

        Args:
            file_or_dir (str): Path to the file or directory to archive and encrypt.
            is_directory (bool): Whether the path is a directory. Defaults to False.
            compression_format (str): Compression format ('zip', 'gzip', or 'tar.gz'). Defaults to 'zip'.

        Returns:
            str: Path to the encrypted archive.
        """
        if is_directory:
            archive_path = self.archive_directory(file_or_dir, compression_format)
        else:
            archive_path = self.compress_file(file_or_dir, compression_format)

        encrypted_archive_path = self.encrypt_file(archive_path)
        os.remove(archive_path)  # Remove the unencrypted archive

        print(f"Archived and encrypted file saved at: {encrypted_archive_path}")
        return encrypted_archive_path

    def restore_encrypted_file(self, encrypted_file_path: str, output_path: str) -> None:
        """
        Restores a decrypted version of an encrypted file.

        Args:
            encrypted_file_path (str): Path to the encrypted file.
            output_path (str): Path to save the decrypted file.
        """
        if not os.path.exists(encrypted_file_path):
            raise FileNotFoundError(f"Encrypted file not found: {encrypted_file_path}")

        with open(encrypted_file_path, 'rb') as enc_file:
            encrypted_data = enc_file.read()
            decrypted_data = self.fernet.decrypt(encrypted_data)

        with open(output_path, 'wb') as out_file:
            out_file.write(decrypted_data)

        print(f"Decrypted file saved at: {output_path}")


# Example Usage
if __name__ == "__main__":
    archiver = DataArchiver()

    # Archive and encrypt a file
    try:
        encrypted_archive = archiver.archive_and_encrypt("example_data.csv")
    except Exception as e:
        print(f"Error archiving and encrypting file: {e}")

    # Archive and encrypt a directory
    try:
        encrypted_dir_archive = archiver.archive_and_encrypt("example_directory", is_directory=True)
    except Exception as e:
        print(f"Error archiving and encrypting directory: {e}")

    # Restore an encrypted file
    try:
        archiver.restore_encrypted_file(encrypted_archive, "restored_data.csv")
    except Exception as e:
        print(f"Error restoring encrypted file: {e}")
