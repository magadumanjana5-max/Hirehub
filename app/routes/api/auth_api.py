from flask import Blueprint, jsonify, request, session

from app.services.auth_service import AuthService

auth_api_bp = Blueprint('auth_api', __name__, url_prefix='/api')


def _public_user(user):
    return {key: value for key, value in user.items() if key != 'password_hash'}


@auth_api_bp.route('/auth/register', methods=['POST'])
def register_api():
    payload = request.get_json(silent=True) or {}
    if not isinstance(payload, dict):
        return jsonify({'error': 'JSON object required'}), 400
    try:
        user = AuthService().register(payload)
        session.clear()
        session['user'] = _public_user(user)
        session['user_id'] = user['id']
        session.permanent = True
        return jsonify({'message': 'User registered', 'user': _public_user(user)}), 201
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400


@auth_api_bp.route('/auth/login', methods=['POST'])
def login_api():
    payload = request.get_json(silent=True) or {}
    if not isinstance(payload, dict):
        return jsonify({'error': 'JSON object required'}), 400
    user = AuthService().login(payload.get('email', ''), payload.get('password', ''))
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401
    session.clear()
    session['user'] = _public_user(user)
    session['user_id'] = user['id']
    session.permanent = True
    return jsonify({'message': 'Login successful', 'user': _public_user(user)})


@auth_api_bp.route('/auth/logout', methods=['POST'])
def logout_api():
    user_id = session.get('user_id')
    if user_id:
        from app.services.audit_service import AuditService
        AuditService().record(user_id, 'user.logged_out')
    session.clear()
    return jsonify({'message': 'Logged out'})
