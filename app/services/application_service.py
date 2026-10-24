from app.repositories.application_repository import ApplicationRepository
from app.repositories.job_repository import JobRepository
from pymongo.errors import DuplicateKeyError
from app.services.audit_service import AuditService
from app.services.notification_service import NotificationService


class ApplicationService:
    def __init__(self):
        self.applications = ApplicationRepository()
        self.jobs = JobRepository()
        self.notifications = NotificationService()
        self.audit = AuditService()

    def apply(self, payload):
        job = self.jobs.get_by_id(payload['job_id'])
        if not job:
            raise ValueError('Job not found')
        if job.get('status', 'open') != 'open':
            raise ValueError('This job is no longer accepting applications')

        for application in self.applications.by_candidate(payload['candidate_id']):
            if application.get('job_id') == payload['job_id']:
                raise ValueError('Application already submitted for this job')

        application = {
            'job_id': payload['job_id'],
            'candidate_id': payload['candidate_id'],
            'resume_url': payload.get('resume_url', ''),
            'resume_id': payload.get('resume_id', ''),
            'status': 'applied',
        }
        try:
            created = self.applications.create(application)
        except DuplicateKeyError as exc:
            raise ValueError('Application already submitted for this job') from exc
        self.notifications.create_notification(
            job.get('recruiter_id', ''),
            f"New application received for {job.get('title', 'your job')}.",
            'info',
        )
        self.audit.record(payload['candidate_id'], 'application.submitted', {'job_id': payload['job_id']})
        return created

    def list_by_candidate(self, candidate_id):
        return self.applications.by_candidate(candidate_id)

    def update_status(self, application_id, status):
        if status not in {'applied', 'screening', 'interview', 'rejected', 'offered', 'hired'}:
            raise ValueError('Invalid application status')
        application = self.applications.get_by_id(application_id)
        if not application:
            raise ValueError('Application not found')
        updated = self.applications.update(application_id, {'status': status})
        self.notifications.create_notification(
            application['candidate_id'],
            f"Your application status changed to {status}.",
            'info',
        )
        self.audit.record(
            application['candidate_id'],
            'application.status_updated',
            {'application_id': application_id, 'status': status},
        )
        return updated
