from flask_mail import Message
from app import mail
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def send_email(subject, recipient, body, html_body=None):
    """
    General-purpose email function to send emails with optional HTML content.
    Logs the success or failure of email sending.

    :param subject: The subject of the email
    :param recipient: The email recipient (a single email or a list of emails)
    :param body: The plain text body of the email
    :param html_body: Optional HTML content for the email
    """
    try:
        msg = Message(subject, sender='no-reply@rlgdata.com', recipients=[recipient])
        msg.body = body

        if html_body:
            msg.html = html_body  # Optional: add HTML content

        mail.send(msg)
        logging.info(f"Email sent successfully to {recipient} with subject: {subject}")

    except Exception as e:
        logging.error(f"Failed to send email to {recipient}: {e}")
        raise  # Reraise the exception if you want to handle it at a higher level


def send_scraping_completed_email(recipient, url):
    """
    Sends an email notification when a scraping task is completed.

    :param recipient: The email recipient
    :param url: The URL that was scraped
    """
    subject = "Scraping Task Completed"
    body = f"The scraping task for {url} has been completed successfully."

    # Optional: Add a richer HTML content for the email
    html_body = f"""
    <html>
    <body>
        <h2>Scraping Task Completed</h2>
        <p>The scraping task for the URL <a href="{url}">{url}</a> has been successfully completed.</p>
        <p>Click the link to view the results or review the report.</p>
    </body>
    </html>
    """

    send_email(subject, recipient, body, html_body)


def send_invitation_email(recipient, token):
    """
    Sends an email invitation to a new user with a token to accept the invite.

    :param recipient: The email recipient
    :param token: The invitation token
    """
    subject = "You're Invited to Join RLG DATA"
    body = f"Please click the following link to accept the invitation and register: {url_for('auth.accept_invite', token=token, _external=True)}"
    
    html_body = f"""
    <html>
    <body>
        <h2>You're Invited!</h2>
        <p>Please click the following link to accept your invitation and complete your registration:</p>
        <a href="{url_for('auth.accept_invite', token=token, _external=True)}">Accept Invitation</a>
    </body>
    </html>
    """

    send_email(subject, recipient, body, html_body)
