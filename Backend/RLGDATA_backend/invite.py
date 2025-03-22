import uuid
from datetime import datetime
from typing import Any
from flask import render_template, request, flash, redirect, url_for, current_app
from models import Invite, User, db
from flask_mail import Message
from app import mail
from werkzeug.security import generate_password_hash

def send_invite(email: str, role: str) -> Any:
    """
    Send an invitation email with a unique token to a new user.
    
    Checks if the email is already invited or registered. If not, generates a unique token,
    creates a new Invite record, commits it to the database, and sends an email invitation.

    Args:
        email (str): The email address to send the invitation to.
        role (str): The role to assign upon registration.

    Returns:
        A Flask redirect response to the invite page.
    """
    try:
        existing_invite = Invite.query.filter_by(email=email).first()
        existing_user = User.query.filter_by(email=email).first()

        if existing_invite or existing_user:
            flash('This email has already been invited or registered.', 'danger')
            return redirect(url_for('invite'))

        # Generate a unique token for the invite
        token = str(uuid.uuid4())

        # Create and save the new invite
        new_invite = Invite(email=email, role=role, token=token, created_at=datetime.utcnow(), status='pending')
        db.session.add(new_invite)
        db.session.commit()

        # Compose and send the invitation email
        msg = Message(
            subject="You're invited to RLG DATA",
            sender="your_email@example.com",  # Update with your actual sender email
            recipients=[email]
        )
        invite_link = url_for('auth.accept_invite', token=token, _external=True)
        msg.body = f"Hello,\n\nYou have been invited to join RLG DATA. Please click the link below to accept the invitation:\n{invite_link}\n\nThank you!"
        mail.send(msg)

        flash(f'Invitation sent to {email}.', 'success')
        return redirect(url_for('invite'))
    except Exception as e:
        current_app.logger.error(f"Error sending invite to {email}: {e}")
        flash('An error occurred while sending the invitation. Please try again later.', 'danger')
        return redirect(url_for('invite'))


def resend_invite(invite_id: int) -> Any:
    """
    Resend an existing invitation if its status is 'pending'.
    
    Args:
        invite_id (int): The unique identifier of the invitation to be resent.
    
    Returns:
        A Flask redirect response to the invite page.
    """
    try:
        invite = Invite.query.get(invite_id)
        if invite and invite.status == 'pending':
            msg = Message(
                subject="Resend: You're invited to RLG DATA",
                sender="your_email@example.com",  # Update with your actual sender email
                recipients=[invite.email]
            )
            invite_link = url_for('auth.accept_invite', token=invite.token, _external=True)
            msg.body = f"Hello,\n\nPlease click the link to accept your invitation:\n{invite_link}\n\nThank you!"
            mail.send(msg)
            flash(f'Invitation resent to {invite.email}.', 'info')
        else:
            flash('Unable to resend invitation.', 'danger')
    except Exception as e:
        current_app.logger.error(f"Error resending invite {invite_id}: {e}")
        flash('An error occurred while resending the invitation.', 'danger')
    return redirect(url_for('invite'))


def delete_invite(invite_id: int) -> Any:
    """
    Delete a pending or expired invitation.
    
    Args:
        invite_id (int): The unique identifier of the invitation to delete.
    
    Returns:
        A Flask redirect response to the invite page.
    """
    try:
        invite = Invite.query.get(invite_id)
        if invite:
            db.session.delete(invite)
            db.session.commit()
            flash(f'Invitation for {invite.email} has been deleted.', 'warning')
        else:
            flash('Invitation not found.', 'danger')
    except Exception as e:
        current_app.logger.error(f"Error deleting invite {invite_id}: {e}")
        flash('An error occurred while deleting the invitation.', 'danger')
    return redirect(url_for('invite'))


def accept_invite(token: str) -> Any:
    """
    Accept an invitation using the provided token.
    
    If the invite is valid and pending, redirects the user to the registration page
    with pre-filled email and role parameters; otherwise, flashes an error message
    and redirects to the login page.

    Args:
        token (str): The unique invitation token.

    Returns:
        A Flask redirect response to the appropriate authentication page.
    """
    try:
        invite = Invite.query.filter_by(token=token).first()
        if invite and invite.status == 'pending':
            return redirect(url_for('auth.register', email=invite.email, role=invite.role))
        flash('Invalid or expired invitation.', 'danger')
    except Exception as e:
        current_app.logger.error(f"Error accepting invite with token {token}: {e}")
        flash('An error occurred while processing the invitation.', 'danger')
    return redirect(url_for('auth.login'))
