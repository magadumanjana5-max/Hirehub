from app.repositories.base_repository import BaseRepository


class RecruiterRepository(BaseRepository):
    collection_name = 'users'

    def get_recruiters(self):
        if self.database is not None:
            return [
                self._without_mongo_id(user)
                for user in self._collection().find({'role': 'recruiter'})
            ]
        return [user for user in self.all() if user.get('role') == 'recruiter']
