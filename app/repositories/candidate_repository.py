from app.repositories.base_repository import BaseRepository


class CandidateRepository(BaseRepository):
    collection_name = 'users'

    def get_candidates(self):
        if self.database is not None:
            return [
                self._without_mongo_id(user)
                for user in self._collection().find({'role': 'candidate'})
            ]
        return [user for user in self.all() if user.get('role') == 'candidate']
