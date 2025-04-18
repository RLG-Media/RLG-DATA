import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from itsdangerous import URLSafeTimedSerializer
from flask import current_app, url_for
from datetime import datetime

class EmailVerificationService:
    def __init__(self, smtp_server, smtp_port, smtp_user, smtp_password):
        """
        Initialize the email verification service with SMTP details.
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])

    def generate_verification_token(self, email):
        """
        Generate a time-sensitive token for email verification.
        """
        return self.serializer.dumps(email, salt=current_app.config['SECURITY_PASSWORD_SALT'])

    def verify_token(self, token, expiration=3600):
        """
        Verify the provided token and return the associated email.
        """
        try:
            email = self.serializer.loads(token, salt=current_app.config['SECURITY_PASSWORD_SALT'], max_age=expiration)
            return email
        except Exception as e:
            current_app.logger.error(f"Token verification failed: {e}")
            return None

    def send_verification_email(self, email, platform, user_name=None):
        """
        Send a verification email to the user with a secure link.
        """
        try:
            token = self.generate_verification_token(email)
            verification_url = url_for('verify_email', token=token, _external=True)

            # Email content
            subject = f"Verify Your Email for RLG {platform}"
            sender_email = self.smtp_user
            recipient_email = email

            html_content = f"""
            <html>
            <body>
                <h1>Hello{f", {user_name}" if user_name else ""},</h1>
                <p>
                    Thank you for registering with RLG {platform}. Please click the link below to verify your email address:
                </p>
                <p>
                    <a href="{verification_url}" style="color: #007bff; text-decoration: none;">
                        Verify My Email
                    </a>
                </p>
                <p>If you did not register for RLG {platform}, please ignore this email.</p>
                <br>
                <p>Best regards,<br>The RLG {platform} Team</p>
            </body>
            </html>
            """

            # MIME Email Setup
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = sender_email
            message["To"] = recipient_email

            message.attach(MIMEText(html_content, "html"))

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(sender_email, recipient_email, message.as_string())

            current_app.logger.info(f"Verification email sent to {email}")
            return True
        except Exception as e:
            current_app.logger.error(f"Failed to send verification email: {e}")
            return False

    def log_verification_attempt(self, email, status, platform):
        """
        Log email verification attempts for auditing purposes.
        """
        try:
            log_message = f"[{datetime.utcnow()}] Email: {email}, Status: {status}, Platform: RLG {platform}"
            with open('email_verification.log', 'a') as log_file:
                log_file.write(log_message + '\n')
        except Exception as e:
            current_app.logger.error(f"Failed to log verification attempt: {e}")


# Configuration Example
email_service = EmailVerificationService(
    smtp_server="smtp.gmail.com",
    smtp_port=587,
    smtp_user="your_email@example.com",
    smtp_password="your_password"
)
email_service = EmailVerificationService(
    smtp_server="smtp.example.com",
    smtp_port=587,
    smtp_user="your_email@example.com",
    smtp_password="your_password"
)
email_service.send_verification_email(
    email="user@example.com",
    platform="Data",
    user_name="John Doe"
)
email = email_service.verify_token(token)
if email:
    print("Token is valid")
else:
    print("Token is invalid or expired")

email_service.log_verification_attempt(
    email="user@example.com",
    status="Success",
    platform="Fans"
)
