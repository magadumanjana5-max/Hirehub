from flask import Blueprint, redirect, render_template, session, url_for


dashboard_bp = Blueprint('dashboard', __name__, url_prefix='')


@dashboard_bp.route('/dashboard')
def index():
    user = session.get('user')
    if not user:
        return redirect(url_for('auth.login'))
    if user.get('role') == 'candidate':
        return redirect(url_for('candidate.dashboard'))
    if user.get('role') == 'recruiter':
        return redirect(url_for('recruiter.dashboard'))
    if user.get('role') == 'admin':
        return redirect(url_for('admin.dashboard'))
    return render_template('dashboard/index.html', user=user)
