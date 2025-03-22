import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask_socketio import SocketIO
from flask import current_app
import logging

# Initialize SocketIO for real-time notifications (e.g., WebSocket support)
socketio = SocketIO()

def send_email_notification(to_email, subject, message):
    """
    Send an email notification to the specified address.
    """
    try:
        smtp_server = current_app.config['MAIL_SERVER']
        smtp_port = current_app.config['MAIL_PORT']
        smtp_username = current_app.config['MAIL_USERNAME']
        smtp_password = current_app.config['MAIL_PASSWORD']
        sender_email = current_app.config['MAIL_DEFAULT_SENDER']

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'html'))

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(sender_email, to_email, msg.as_string())
            logging.info(f"Email sent to {to_email} with subject: '{subject}'")

    except Exception as e:
        logging.error(f"Failed to send email to {to_email}: {str(e)}")

def send_in_app_notification(user_id, title, message):
    """
    Store in-app notification in the database for the given user.
    This function assumes a notifications table exists and is integrated.
    """
    from shared.models import Notification, db  # Lazy import to avoid circular imports

    try:
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            is_read=False
        )
        db.session.add(notification)
        db.session.commit()
        logging.info(f"In-app notification stored for user {user_id}")

    except Exception as e:
        logging.error(f"Failed to store in-app notification for user {user_id}: {str(e)}")

def send_real_time_notification(event, data):
    """
    Emit a real-time notification using WebSocket.
    """
    try:
        socketio.emit(event, data)
        logging.info(f"Real-time notification sent: event '{event}' with data: {data}")

    except Exception as e:
        logging.error(f"Failed to send real-time notification for event '{event}': {str(e)}")

# New Notifications for Keyword Research and Insights
def notify_keyword_insight(user_id, keyword, search_volume, competition_level):
    """
    Notify user of insights for a specific keyword.
    """
    title = f"Keyword Insight: {keyword}"
    message = (
        f"The keyword '{keyword}' has a search volume of {search_volume} and "
        f"a competition level of {competition_level}. Consider targeting it in your strategy."
    )
    send_in_app_notification(user_id, title, message)
    send_real_time_notification('keyword_insight', {'keyword': keyword, 'search_volume': search_volume, 'competition_level': competition_level})

def notify_new_keyword_suggestions(user_id, suggestions):
    """
    Notify user of new keyword suggestions.
    """
    title = "New Keyword Suggestions Available"
    message = (
        "Based on your recent activities, we have identified new keyword opportunities: "
        f"{', '.join(suggestions)}. Check them out in the Keyword Research Tool."
    )
    send_in_app_notification(user_id, title, message)
    send_real_time_notification('new_keyword_suggestions', {'suggestions': suggestions})

# Enhanced Notifications for SEO and Analytics
def notify_trending_keywords(user_id, platform, trending_keywords):
    """
    Notify user of trending keywords on a specific platform.
    """
    title = f"Trending Keywords on {platform}"
    message = (
        f"The following keywords are trending on {platform}: {', '.join(trending_keywords)}. "
        "Leverage them to increase your reach and engagement."
    )
    send_in_app_notification(user_id, title, message)
    send_real_time_notification('trending_keywords', {'platform': platform, 'trending_keywords': trending_keywords})

def notify_analytics_performance(user_id, metrics):
    """
    Notify user of performance insights from analytics data.
    """
    title = "Performance Analytics Update"
    message = f"Your recent analytics report highlights the following metrics: {metrics}."
    send_in_app_notification(user_id, title, message)
    send_real_time_notification('analytics_performance', {'metrics': metrics})

# Notifications for User Engagement and API Updates
def notify_engagement_update(user_id, platform, engagement_rate):
    """
    Notify user of updated engagement rate for a platform.
    """
    title = f"Engagement Rate Update for {platform}"
    message = f"Your engagement rate is now {engagement_rate}% on {platform}."
    send_in_app_notification(user_id, title, message)
    send_real_time_notification('engagement_update', {'platform': platform, 'engagement_rate': engagement_rate})

def notify_api_key_expiration(user_id, platform, expiration_date):
    """
    Alert user of upcoming API key expiration.
    """
    title = f"API Key Expiration Notice for {platform}"
    message = f"Your API key for {platform} will expire on {expiration_date}. Please update it to avoid disruptions."
    send_in_app_notification(user_id, title, message)
    send_real_time_notification('api_key_expiration', {'platform': platform, 'expiration_date': expiration_date})

def notify_custom_alert(user_id, title, message):
    """
    Send a custom notification to the user for specific alerts or reminders.
    """
    send_in_app_notification(user_id, title, message)
    send_real_time_notification('custom_alert', {'title': title, 'message': message})
