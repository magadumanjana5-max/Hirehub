from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Interview:
    id: str
    application_id: str
    candidate_id: str
    recruiter_id: str
    scheduled_at: str
    mode: str = 'virtual'
    notes: str = ''
    created_at: str = field(default_factory=lambda: datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))

    def to_dict(self):
        return {
            'id': self.id,
            'application_id': self.application_id,
            'candidate_id': self.candidate_id,
            'recruiter_id': self.recruiter_id,
            'scheduled_at': self.scheduled_at,
            'mode': self.mode,
            'notes': self.notes,
            'created_at': self.created_at,
        }
