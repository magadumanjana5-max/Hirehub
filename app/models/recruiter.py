from dataclasses import dataclass

from .user import User


@dataclass
class Recruiter(User):
    company_name: str = ''
    department: str = ''
    phone: str = ''

    def to_dict(self):
        data = super().to_dict()
        data.update({
            'company_name': self.company_name,
            'department': self.department,
            'phone': self.phone,
        })
        return data
