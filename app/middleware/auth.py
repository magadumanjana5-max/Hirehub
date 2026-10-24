from flask import session, redirect, url_for


def require_login():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    return None
