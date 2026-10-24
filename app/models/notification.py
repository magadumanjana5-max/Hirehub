from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Notification:
    id: str
    user_id: str
    message: str
    type: str = 'info'
    is_read: bool = False
    created_at: str = field(default_factory=lambda: datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'message': self.message,
            'type': self.type,
            'is_read': self.is_read,
            'created_at': self.created_at,
        }
