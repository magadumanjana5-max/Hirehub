from app.repositories.application_repository import ApplicationRepository
from app.repositories.job_repository import JobRepository
from app.repositories.user_repository import UserRepository


class CandidateService:
    def __init__(self):
        self.users = UserRepository()
        self.jobs = JobRepository()
        self.applications = ApplicationRepository()

    def get_profile(self, candidate_id):
        return self.users.get_by_id(candidate_id)

    def update_profile(self, candidate_id, payload):
        return self.users.update(candidate_id, payload)

    def get_recommendations(self, candidate_id):
        candidate = self.users.get_by_id(candidate_id)
        if not candidate:
            return []
        skills = set(candidate.get('skills', [])) or set()
        recs = []
        for job in self.jobs.all():
            if job.get('status', 'open') != 'open':
                continue
            if not skills:
                recs.append(job)
                continue
            reqs = set(job.get('requirements', []))
            if skills & reqs or candidate.get('preferred_roles', []) and job.get('title', '').lower() in [r.lower() for r in candidate.get('preferred_roles', [])]:
                recs.append(job)
        return recs[:5]
