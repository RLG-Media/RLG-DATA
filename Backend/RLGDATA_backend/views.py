from flask import render_template, request, flash, redirect, url_for
from models import Invite
from flask_login import login_required

views_blueprint = Blueprint('views', __name__)

@views_blueprint.route('/invite')
@login_required
def invite():
    """Render the invite management page."""
    pending_invites = Invite.query.filter_by(status='pending').all()
    return render_template('invite.html', pending_invites=pending_invites)
