from dataclasses import dataclass


@dataclass
class Resume:
    id: str
    candidate_id: str
    filename: str
    storage_path: str
    uploaded_at: str

    def to_dict(self):
        return {
            'id': self.id,
            'candidate_id': self.candidate_id,
            'filename': self.filename,
            'storage_path': self.storage_path,
            'uploaded_at': self.uploaded_at,
        }
