from werkzeug.security import check_password_hash, generate_password_hash

from app.repositories.user_repository import UserRepository
from app.services.audit_service import AuditService


class AuthService:
    def __init__(self):
        self.user_repository = UserRepository()
        self.audit = AuditService()

    def register(self, payload):
        email = payload.get('email', '').strip().lower()
        password = payload.get('password', '')
        role = payload.get('role', 'candidate')
        if not email or not password:
            raise ValueError('Email and password are required')
        if role not in {'candidate', 'recruiter'}:
            raise ValueError('Registration is limited to candidate and recruiter accounts')
        if self.user_repository.get_by_email(email):
            raise ValueError('Email already registered')
        password_hash = generate_password_hash(password)
        user = {
            'email': email,
            'password_hash': password_hash,
            'role': role,
            'first_name': payload.get('first_name', ''),
            'last_name': payload.get('last_name', ''),
            'is_active': True,
        }
        if role == 'recruiter':
            user['company_name'] = payload.get('company_name', '')
        created_user = self.user_repository.create(user)
        self.audit.record(created_user['id'], 'user.registered', {'role': role})
        return created_user

    def login(self, email, password):
        user = self.user_repository.get_by_email((email or '').strip().lower())
        if not user or not user.get('is_active', True) or not check_password_hash(user['password_hash'], password or ''):
            return None
        self.audit.record(user['id'], 'user.logged_in')
        return user
