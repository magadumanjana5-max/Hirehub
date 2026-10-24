from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app.services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__, url_prefix='')


def _session_user(user):
    return {key: value for key, value in user.items() if key != 'password_hash'}


@auth_bp.get('/')
@auth_bp.get('/index')
def index():
    return render_template('home.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.form
        try:
            service = AuthService()
            user = service.register({
                'email': data.get('email', ''),
                'password': data.get('password', ''),
                'first_name': data.get('first_name', ''),
                'last_name': data.get('last_name', ''),
                'role': data.get('role', 'candidate'),
                'company_name': data.get('company_name', ''),
            })
            session.clear()
            session['user'] = _session_user(user)
            session['user_id'] = user['id']
            session.permanent = True
            return redirect(url_for('dashboard.index'))
        except ValueError as exc:
            flash(str(exc), 'danger')
    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '')
        password = request.form.get('password', '')
        user = AuthService().login(email, password)
        if user:
            session.clear()
            session['user'] = _session_user(user)
            session['user_id'] = user['id']
            session.permanent = True
            return redirect(url_for('dashboard.index'))
        flash('Invalid credentials', 'danger')
    return render_template('auth/login.html')


@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    user_id = session.get('user_id')
    if user_id:
        from app.services.audit_service import AuditService
        AuditService().record(user_id, 'user.logged_out')
    session.clear()
    return redirect(url_for('auth.login'))
