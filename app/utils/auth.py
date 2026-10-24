from functools import wraps
from flask import jsonify, redirect, url_for
from flask import session


def login_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return view_func(*args, **kwargs)
    return wrapped


def role_required(*allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(*args, **kwargs):
            user = session.get('user')
            if not user:
                return redirect(url_for('auth.login'))
            if user.get('role') not in allowed_roles:
                return redirect(url_for('dashboard.index'))
            return view_func(*args, **kwargs)
        return wrapped
    return decorator


def api_role_required(*allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(*args, **kwargs):
            user = session.get('user')
            if not user:
                return jsonify({'error': 'Authentication required'}), 401
            if user.get('role') not in allowed_roles:
                return jsonify({'error': 'Forbidden'}), 403
            return view_func(*args, **kwargs)
        return wrapped
    return decorator
