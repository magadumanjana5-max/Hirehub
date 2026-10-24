from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Job:
    id: str
    title: str
    company_name: str
    location: str
    employment_type: str
    description: str
    requirements: list[str] = field(default_factory=list)
    salary: str = ''
    recruiter_id: str = ''
    created_at: str = field(default_factory=lambda: datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))
    status: str = 'open'

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'company_name': self.company_name,
            'location': self.location,
            'employment_type': self.employment_type,
            'description': self.description,
            'requirements': self.requirements,
            'salary': self.salary,
            'recruiter_id': self.recruiter_id,
            'created_at': self.created_at,
            'status': self.status,
        }
