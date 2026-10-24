from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class User:
    id: str
    email: str
    password_hash: str
    role: str
    first_name: str = ''
    last_name: str = ''
    created_at: str = field(default_factory=lambda: datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))
    is_active: bool = True

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'password_hash': self.password_hash,
            'role': self.role,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'created_at': self.created_at,
            'is_active': self.is_active,
        }
