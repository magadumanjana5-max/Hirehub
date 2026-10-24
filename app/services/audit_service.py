from datetime import datetime, timezone

from app.repositories.base_repository import BaseRepository


class AuditService:
    def __init__(self):
        self.repository = BaseRepository()
        self.repository.collection_name = 'audit_logs'

    def record(self, user_id, action, details=None):
        return self.repository.create({
            'user_id': user_id,
            'action': action,
            'details': details or {},
            'created_at': datetime.now(timezone.utc).isoformat(),
        })

    def recent(self, limit=100):
        records = self.repository.all()
        return sorted(records, key=lambda item: item.get('created_at', ''), reverse=True)[:limit]
