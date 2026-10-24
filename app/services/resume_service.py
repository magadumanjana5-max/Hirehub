import uuid
from io import BytesIO
from datetime import datetime, timezone
from pathlib import Path

from flask import current_app
from gridfs import GridFSBucket
from bson import ObjectId
from gridfs.errors import NoFile
from werkzeug.utils import secure_filename

from app.repositories.base_repository import BaseRepository
from app.services.audit_service import AuditService


class ResumeService:
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

    def __init__(self):
        self.repo = BaseRepository()
        self.repo.collection_name = 'resumes'

    def save_resume(self, candidate_id, file_storage):
        if not file_storage or not file_storage.filename:
            raise ValueError('No resume file uploaded')
        filename = secure_filename(file_storage.filename)
        if '.' not in filename or filename.rsplit('.', 1)[1].lower() not in self.ALLOWED_EXTENSIONS:
            raise ValueError('Resume must be a PDF, DOC, or DOCX file')
        unique_name = f'{uuid.uuid4().hex}_{filename}'
        if self.repo.database is not None:
            bucket = GridFSBucket(self.repo.database, bucket_name='resumes')
            file_id = bucket.upload_from_stream(
                unique_name,
                file_storage.stream,
                metadata={'candidate_id': candidate_id, 'original_filename': filename},
            )
            storage_name = str(file_id)
        else:
            folder = Path(current_app.config['UPLOAD_FOLDER'])
            folder.mkdir(parents=True, exist_ok=True)
            path = folder / unique_name
            file_storage.save(path)
            storage_name = unique_name
        record = {
            'id': str(uuid.uuid4()),
            'candidate_id': candidate_id,
            'filename': filename,
            'storage_name': storage_name,
            'uploaded_at': datetime.now(timezone.utc).isoformat(),
        }
        self.repo.create(record)
        AuditService().record(candidate_id, 'resume.uploaded', {'resume_id': record['id']})
        return record

    def get_resume(self, resume_id, candidate_id=None):
        resume = self.repo.get_by_id(resume_id)
        if not resume or (candidate_id and resume.get('candidate_id') != candidate_id):
            return None
        return resume

    def for_candidate(self, candidate_id):
        return [
            resume for resume in self.repo.all()
            if resume.get('candidate_id') == candidate_id
        ]

    def content_for(self, resume):
        if self.repo.database is not None:
            bucket = GridFSBucket(self.repo.database, bucket_name='resumes')
            output = BytesIO()
            try:
                bucket.download_to_stream(ObjectId(resume['storage_name']), output)
            except NoFile as exc:
                raise FileNotFoundError('Resume file is missing') from exc
            output.seek(0)
            return output
        path = Path(current_app.config['UPLOAD_FOLDER']) / resume['storage_name']
        if path.parent.resolve() != Path(current_app.config['UPLOAD_FOLDER']).resolve():
            raise ValueError('Invalid resume storage path')
        return path
