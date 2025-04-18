import os
import shutil
import datetime
import logging
from subprocess import run, PIPE
from .config import DATABASE_CONFIG, BACKUP_DIRECTORY, NOTIFICATION_EMAILS, BACKUP_RETENTION_PERIOD
from smtplib import SMTP
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Setup logging configuration for backup operations
logging.basicConfig(
    filename='/var/log/database_backup.log',  # Change this to your desired log file path
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def send_notification_email(subject, body):
    """
    Sends an email notification about the backup status.
    """
    try:
        sender_email = "backup@yourdomain.com"
        smtp_server = "smtp.yourdomain.com"
        smtp_port = 587
        receiver_email = NOTIFICATION_EMAILS

        # Set up the MIME
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = receiver_email
        message['Subject'] = subject
        message.attach(MIMEText(body, 'plain'))

        # Send the email
        with SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, "your_password")  # Ensure the password is securely stored
            server.sendmail(sender_email, receiver_email, message.as_string())
        logging.info(f"Notification sent successfully to {receiver_email}.")
    except Exception as e:
        logging.error(f"Error sending email notification: {e}")

def create_backup():
    """
    Creates a backup of the database (e.g., MySQL/PostgreSQL) by running a database dump command.
    """
    try:
        # Get the current date for naming the backup file
        current_date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_filename = f"{DATABASE_CONFIG['DB_NAME']}_backup_{current_date}.sql"
        backup_path = os.path.join(BACKUP_DIRECTORY, backup_filename)

        # Command to create a database dump (MySQL/PostgreSQL example)
        if DATABASE_CONFIG['DB_TYPE'] == 'mysql':
            backup_command = [
                "mysqldump", 
                "-u", DATABASE_CONFIG['DB_USER'], 
                "-p" + DATABASE_CONFIG['DB_PASSWORD'], 
                DATABASE_CONFIG['DB_NAME'], 
                ">", backup_path
            ]
        elif DATABASE_CONFIG['DB_TYPE'] == 'postgresql':
            backup_command = [
                "pg_dump", 
                "-U", DATABASE_CONFIG['DB_USER'], 
                "-h", DATABASE_CONFIG['DB_HOST'], 
                DATABASE_CONFIG['DB_NAME'], 
                "-f", backup_path
            ]
        else:
            raise ValueError(f"Unsupported DB type: {DATABASE_CONFIG['DB_TYPE']}")

        # Run the command to create the backup
        result = run(" ".join(backup_command), shell=True, stdout=PIPE, stderr=PIPE)
        if result.returncode == 0:
            logging.info(f"Backup created successfully: {backup_path}")
            send_notification_email("Database Backup Success", f"Backup created successfully: {backup_path}")
        else:
            raise Exception(f"Backup command failed: {result.stderr.decode('utf-8')}")

    except Exception as e:
        logging.error(f"Error during backup creation: {e}")
        send_notification_email("Database Backup Failure", f"Error during backup creation: {e}")

def clean_old_backups():
    """
    Cleans up old database backups that exceed the retention period.
    """
    try:
        # Get current time to check against backup file modification times
        current_time = datetime.datetime.now()

        # List all files in the backup directory
        for filename in os.listdir(BACKUP_DIRECTORY):
            file_path = os.path.join(BACKUP_DIRECTORY, filename)
            if os.path.isfile(file_path):
                # Get file modification time
                file_mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))

                # Check if the file exceeds the retention period
                if (current_time - file_mod_time).days > BACKUP_RETENTION_PERIOD:
                    try:
                        os.remove(file_path)
                        logging.info(f"Old backup removed: {file_path}")
                    except Exception as e:
                        logging.error(f"Error removing old backup {file_path}: {e}")
    except Exception as e:
        logging.error(f"Error during old backup cleanup: {e}")

def backup_database():
    """
    Backups the database and cleans up old backups based on the retention period.
    """
    try:
        logging.info("Starting database backup process.")
        
        # Step 1: Create a fresh database backup
        create_backup()

        # Step 2: Clean up old backups
        clean_old_backups()

        logging.info("Database backup process completed successfully.")
    except Exception as e:
        logging.error(f"Error during backup process: {e}")
        send_notification_email("Database Backup Process Failure", f"Error during backup process: {e}")

if __name__ == "__main__":
    # Run the backup process
    backup_database()
