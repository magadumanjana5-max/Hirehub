from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository):
    collection_name = 'users'

    def get_by_email(self, email):
        if self.database is not None:
            user = self._collection().find_one({'email': email.strip().lower()})
            return self._without_mongo_id(user) if user else None
        for user in self.all():
            if user.get('email', '').lower() == email.lower():
                return user
        return None

    def get_by_role(self, role):
        if self.database is not None:
            return [
                self._without_mongo_id(user)
                for user in self._collection().find({'role': role})
            ]
        return [user for user in self.all() if user.get('role') == role]
