from dataclasses import dataclass

from .user import User


@dataclass
class Admin(User):
    department: str = 'Administration'

    def to_dict(self):
        data = super().to_dict()
        data.update({'department': self.department})
        return data
