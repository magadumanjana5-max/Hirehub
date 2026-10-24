from dataclasses import dataclass, field

from .user import User


@dataclass
class Candidate(User):
    phone: str = ''
    skills: list[str] = field(default_factory=list)
    experience_years: int = 0
    location: str = ''
    preferred_roles: list[str] = field(default_factory=list)
    resume_url: str = ''
    bio: str = ''

    def to_dict(self):
        data = super().to_dict()
        data.update({
            'phone': self.phone,
            'skills': self.skills,
            'experience_years': self.experience_years,
            'location': self.location,
            'preferred_roles': self.preferred_roles,
            'resume_url': self.resume_url,
            'bio': self.bio,
        })
        return data
