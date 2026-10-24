from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Company:
    id: str
    name: str
    industry: str = ''
    website: str = ''
    location: str = ''
    description: str = ''
    created_at: str = field(default_factory=lambda: datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'industry': self.industry,
            'website': self.website,
            'location': self.location,
            'description': self.description,
            'created_at': self.created_at,
        }
