from app.repositories.base_repository import BaseRepository


class NotificationService:
    def __init__(self):
        self.repo = BaseRepository()
        self.repo.collection_name = 'notifications'

    def create_notification(self, user_id, message, kind='info'):
        return self.repo.create({'user_id': user_id, 'message': message, 'type': kind, 'is_read': False})

    def for_user(self, user_id):
        return [item for item in self.repo.all() if item.get('user_id') == user_id]

    def mark_read(self, notification_id, user_id):
        item = self.repo.get_by_id(notification_id)
        if not item or item.get('user_id') != user_id:
            return None
        return self.repo.update(notification_id, {'is_read': True})
