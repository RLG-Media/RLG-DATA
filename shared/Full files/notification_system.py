# notification_system.py

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import requests

class NotificationSystem:
    """
    NotificationSystem class for handling different types of notifications including email, SMS, and push notifications.
    """

    def __init__(self, config_path):
        """
        Initializes the NotificationSystem with configuration data from a specified JSON file.

        :param config_path: Path to the JSON configuration file containing notification settings.
        """
        self.config_path = config_path
        self.load_config()
        self.email_service = self.config.get('email_service')
        self.sms_service = self.config.get('sms_service')
        self.push_service = self.config.get('push_service')

    def load_config(self):
        """
        Loads the notification configuration from the JSON file.
        """
        with open(self.config_path, 'r') as file:
            self.config = json.load(file)

    def send_email(self, to_email, subject, message):
        """
        Sends an email notification.

        :param to_email: Recipient email address.
        :param subject: Subject of the email.
        :param message: Content of the email.
        """
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config['email_sender']
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(message, 'plain'))
            
            # SMTP server configuration
            server = smtplib.SMTP(self.config['email_server'], self.config['email_port'])
            server.starttls()  # Secure the connection
            server.login(self.config['email_sender'], self.config['email_password'])
            server.sendmail(self.config['email_sender'], to_email, msg.as_string())
            server.quit()

            print(f"Email sent to {to_email}")
        except Exception as e:
            print(f"Failed to send email: {e}")

    def send_sms(self, to_phone, message):
        """
        Sends an SMS notification using the configured SMS service.

        :param to_phone: Recipient phone number.
        :param message: Content of the SMS.
        """
        try:
            # Example of sending SMS using an API (replace with actual implementation)
            response = requests.post(
                self.sms_service['url'],
                data={
                    'api_key': self.sms_service['api_key'],
                    'to': to_phone,
                    'message': message
                }
            )
            if response.status_code == 200:
                print(f"SMS sent to {to_phone}")
            else:
                print(f"Failed to send SMS: {response.status_code}")
        except Exception as e:
            print(f"Failed to send SMS: {e}")

    def send_push_notification(self, to_device_id, message):
        """
        Sends a push notification.

        :param to_device_id: Device ID or token to which the push notification should be sent.
        :param message: Content of the push notification.
        """
        try:
            # Example of sending push notification (replace with actual implementation)
            response = requests.post(
                self.push_service['url'],
                json={
                    'api_key': self.push_service['api_key'],
                    'device_id': to_device_id,
                    'message': message
                }
            )
            if response.status_code == 200:
                print(f"Push notification sent to device ID: {to_device_id}")
            else:
                print(f"Failed to send push notification: {response.status_code}")
        except Exception as e:
            print(f"Failed to send push notification: {e}")

    def schedule_notification(self, notification_type, to, message, schedule_time):
        """
        Schedules a notification for future delivery.

        :param notification_type: Type of notification (email, SMS, push).
        :param to: Recipient information (email, phone number, or device ID).
        :param message: Content of the notification.
        :param schedule_time: Time at which the notification should be sent (in UTC).
        """
        # Placeholder for scheduling logic, potentially integrating with a task scheduler like Celery or Cron
        print(f"Scheduled {notification_type} notification to {to} at {schedule_time}")

    def log_notification(self, notification_type, to, message, status):
        """
        Logs notification details including type, recipient, message, and status.

        :param notification_type: Type of notification.
        :param to: Recipient information.
        :param message: Content of the notification.
        :param status: Status of the notification (sent, failed, etc.).
        """
        log_file = "notification_log.txt"
        with open(log_file, 'a') as f:
            f.write(f"Type: {notification_type}, To: {to}, Message: {message}, Status: {status}\n")

# Example usage:
if __name__ == '__main__':
    notification_system = NotificationSystem('notification_config.json')

    # Example: Send Email
    notification_system.send_email('recipient@example.com', 'Test Email', 'This is a test email.')

    # Example: Send SMS
    notification_system.send_sms('1234567890', 'This is a test SMS.')

    # Example: Send Push Notification
    notification_system.send_push_notification('device12345', 'This is a test push notification.')

    # Example: Schedule Notification
    notification_system.schedule_notification('email', 'recipient@example.com', 'Scheduled email content', '2025-01-10 09:00:00')

    # Log Notification
    notification_system.log_notification('email', 'recipient@example.com', 'Test Email', 'Sent')
