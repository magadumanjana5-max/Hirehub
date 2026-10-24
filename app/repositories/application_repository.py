from app.repositories.base_repository import BaseRepository


class ApplicationRepository(BaseRepository):
    collection_name = 'applications'

    def by_candidate(self, candidate_id):
        if self.database is not None:
            return [
                self._without_mongo_id(item)
                for item in self._collection().find({'candidate_id': candidate_id})
            ]
        return [item for item in self.all() if item.get('candidate_id') == candidate_id]

    def by_job(self, job_id):
        if self.database is not None:
            return [
                self._without_mongo_id(item)
                for item in self._collection().find({'job_id': job_id})
            ]
        return [item for item in self.all() if item.get('job_id') == job_id]
