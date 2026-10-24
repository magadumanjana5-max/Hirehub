import re

from app.repositories.base_repository import BaseRepository


class JobRepository(BaseRepository):
    collection_name = 'jobs'

    def search(self, query=None, location=None, employment_type=None):
        if self.database is not None:
            filters = {'status': 'open'}
            if query:
                filters['$or'] = [
                    {'title': {'$regex': re.escape(query), '$options': 'i'}},
                    {'description': {'$regex': re.escape(query), '$options': 'i'}},
                    {'company_name': {'$regex': re.escape(query), '$options': 'i'}},
                ]
            if location:
                filters['location'] = {'$regex': re.escape(location), '$options': 'i'}
            if employment_type:
                filters['employment_type'] = {
                    '$regex': f'^{re.escape(employment_type)}$',
                    '$options': 'i',
                }
            return [
                self._without_mongo_id(job)
                for job in self._collection().find(filters)
            ]

        jobs = [job for job in self.all() if job.get('status', 'open') == 'open']
        if query:
            q = query.lower()
            jobs = [job for job in jobs if q in job.get('title', '').lower() or q in job.get('description', '').lower()]
        if location:
            loc = location.lower()
            jobs = [job for job in jobs if loc in job.get('location', '').lower()]
        if employment_type:
            et = employment_type.lower()
            jobs = [job for job in jobs if et == job.get('employment_type', '').lower()]
        return jobs
