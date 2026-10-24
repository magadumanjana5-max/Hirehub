from app.repositories.job_repository import JobRepository
from app.services.audit_service import AuditService


class JobService:
    def __init__(self):
        self.jobs = JobRepository()
        self.audit = AuditService()

    def list_jobs(self, query=None, location=None, employment_type=None):
        return self.jobs.search(query=query, location=location, employment_type=employment_type)

    def get_job(self, job_id):
        return self.jobs.get_by_id(job_id)

    def create_job(self, payload):
        required = ('title', 'company_name', 'location', 'employment_type', 'description', 'recruiter_id')
        if any(not str(payload.get(field, '')).strip() for field in required):
            raise ValueError('Complete all required job fields')
        job = {
            'title': payload['title'].strip(),
            'company_name': payload['company_name'].strip(),
            'location': payload['location'].strip(),
            'employment_type': payload['employment_type'].strip(),
            'description': payload['description'].strip(),
            'requirements': payload.get('requirements', []),
            'salary': payload.get('salary', ''),
            'recruiter_id': payload['recruiter_id'],
            'status': 'open',
        }
        created = self.jobs.create(job)
        self.audit.record(payload['recruiter_id'], 'job.created', {'job_id': created['id']})
        return created

    def update_job(self, job_id, changes, recruiter_id):
        job = self.jobs.get_by_id(job_id)
        if not job:
            raise ValueError('Job not found')
        if job.get('recruiter_id') != recruiter_id:
            raise PermissionError('You cannot update this job')
        allowed_fields = {'title', 'company_name', 'location', 'employment_type', 'description', 'requirements', 'salary', 'status'}
        changes = {key: value for key, value in changes.items() if key in allowed_fields}
        if not changes:
            raise ValueError('No editable job fields supplied')
        if 'status' in changes and changes['status'] not in {'open', 'closed'}:
            raise ValueError('Status must be open or closed')
        updated = self.jobs.update(job_id, changes)
        self.audit.record(recruiter_id, 'job.updated', {'job_id': job_id, 'fields': sorted(changes)})
        return updated
