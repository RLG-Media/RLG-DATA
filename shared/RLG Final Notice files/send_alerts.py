import smtplib
import requests
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client
from discord_webhook import DiscordWebhook
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def send_email_alert(to_email, subject, message):
    """Send alert via Email."""
    try:
        sender_email = "your_email@example.com"
        sender_password = "your_password"
        smtp_server = "smtp.example.com"
        smtp_port = 587
        
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        
        logging.info(f"Email sent successfully to {to_email}")
    except Exception as e:
        logging.error(f"Failed to send email: {e}")

def send_sms_alert(to_number, message):
    """Send alert via SMS."""
    try:
        twilio_sid = "your_twilio_sid"
        twilio_auth_token = "your_twilio_auth_token"
        twilio_phone_number = "your_twilio_phone_number"
        
        client = Client(twilio_sid, twilio_auth_token)
        message = client.messages.create(
            body=message,
            from_=twilio_phone_number,
            to=to_number
        )
        
        logging.info(f"SMS sent successfully to {to_number}")
    except Exception as e:
        logging.error(f"Failed to send SMS: {e}")

def send_discord_alert(webhook_url, message):
    """Send alert via Discord webhook."""
    try:
        webhook = DiscordWebhook(url=webhook_url, content=message)
        response = webhook.execute()
        logging.info("Discord alert sent successfully.")
    except Exception as e:
        logging.error(f"Failed to send Discord alert: {e}")

def send_slack_alert(token, channel, message):
    """Send alert via Slack."""
    try:
        client = WebClient(token=token)
        response = client.chat_postMessage(channel=channel, text=message)
        logging.info("Slack alert sent successfully.")
    except SlackApiError as e:
        logging.error(f"Failed to send Slack alert: {e.response['error']}")

def send_webhook_alert(url, payload):
    """Send alert via a generic webhook."""
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            logging.info("Webhook alert sent successfully.")
        else:
            logging.error(f"Failed to send webhook alert: {response.status_code}")
    except Exception as e:
        logging.error(f"Failed to send webhook alert: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # Example usage
    send_email_alert("recipient@example.com", "Test Alert", "This is a test email alert.")
    send_sms_alert("+1234567890", "This is a test SMS alert.")
    send_discord_alert("your_discord_webhook_url", "This is a test Discord alert.")
    send_slack_alert("your_slack_token", "#general", "This is a test Slack alert.")
    send_webhook_alert("https://your-webhook-url.com", {"message": "This is a test webhook alert."})
