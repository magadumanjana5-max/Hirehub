from app.repositories.job_repository import JobRepository
from app.services.job_service import JobService


class RecruiterService:
    def __init__(self):
        self.jobs = JobRepository()

    def create_job(self, payload):
        job = {
            'title': payload['title'],
            'company_name': payload.get('company_name', 'HireHub'),
            'location': payload.get('location', 'Remote'),
            'employment_type': payload.get('employment_type', 'Full-time'),
            'description': payload.get('description', ''),
            'requirements': payload.get('requirements', []),
            'salary': payload.get('salary', ''),
            'recruiter_id': payload.get('recruiter_id', ''),
        }
        return JobService().create_job(job)

    def list_jobs(self, recruiter_id):
        return [job for job in self.jobs.all() if job.get('recruiter_id') == recruiter_id]
