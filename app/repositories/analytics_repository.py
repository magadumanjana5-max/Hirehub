from app.repositories.base_repository import BaseRepository


class AnalyticsRepository(BaseRepository):
    collection_name = 'jobs'

    def overview(self):
        jobs = self.all()
        if self.database is not None:
            job_count = self.database['jobs'].count_documents({})
            application_count = self.database['applications'].count_documents({})
            user_count = self.database['users'].count_documents({})
        else:
            job_count = len(jobs)
            application_count = len(self.store.get('applications', []))
            user_count = len(self.store.get('users', []))
        return {
            'total_jobs': job_count,
            'total_applications': application_count,
            'total_users': user_count,
        }
