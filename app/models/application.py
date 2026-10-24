from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Application:
    id: str
    job_id: str
    candidate_id: str
    resume_url: str = ''
    status: str = 'applied'
    applied_at: str = field(default_factory=lambda: datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))

    def to_dict(self):
        return {
            'id': self.id,
            'job_id': self.job_id,
            'candidate_id': self.candidate_id,
            'resume_url': self.resume_url,
            'status': self.status,
            'applied_at': self.applied_at,
        }
