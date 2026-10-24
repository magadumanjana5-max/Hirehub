from app.repositories.interview_repository import InterviewRepository
from app.repositories.application_repository import ApplicationRepository
from app.repositories.job_repository import JobRepository
from app.services.audit_service import AuditService
from app.services.notification_service import NotificationService


class InterviewService:
    def __init__(self):
        self.interviews = InterviewRepository()
        self.applications = ApplicationRepository()
        self.jobs = JobRepository()
        self.notifications = NotificationService()
        self.audit = AuditService()

    def schedule(self, payload):
        if not payload.get('scheduled_at'):
            raise ValueError('Interview date and time are required')
        application = self.applications.get_by_id(payload['application_id'])
        if not application:
            raise ValueError('Application not found')
        job = self.jobs.get_by_id(application['job_id'])
        if not job or job.get('recruiter_id') != payload['recruiter_id']:
            raise ValueError('You cannot schedule an interview for this application')
        interview = {
            'application_id': payload['application_id'],
            'candidate_id': application['candidate_id'],
            'recruiter_id': payload['recruiter_id'],
            'scheduled_at': payload['scheduled_at'],
            'mode': payload.get('mode', 'virtual'),
            'notes': payload.get('notes', ''),
        }
        created = self.interviews.create(interview)
        self.notifications.create_notification(
            application['candidate_id'],
            f"An interview has been scheduled for {job.get('title', 'your application')} at {payload['scheduled_at']}.",
            'info',
        )
        self.audit.record(payload['recruiter_id'], 'interview.scheduled', {'interview_id': created['id']})
        return created

    def for_recruiter(self, recruiter_id):
        return [item for item in self.interviews.all() if item.get('recruiter_id') == recruiter_id]

    def for_candidate(self, candidate_id):
        return [item for item in self.interviews.all() if item.get('candidate_id') == candidate_id]
