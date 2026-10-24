from flask import Blueprint, jsonify, request, send_file, session

from app.repositories.user_repository import UserRepository
from app.services.audit_service import AuditService
from app.services.interview_service import InterviewService
from app.services.notification_service import NotificationService
from app.services.resume_service import ResumeService
from app.utils.auth import api_role_required

features_api_bp = Blueprint('features_api', __name__, url_prefix='/api')


@features_api_bp.get('/candidate/profile')
@api_role_required('candidate')
def get_candidate_profile():
    user = UserRepository().get_by_id(session['user_id'])
    if not user:
        return jsonify({'error': 'Profile not found'}), 404
    public_user = {key: value for key, value in user.items() if key != 'password_hash'}
    return jsonify({'profile': public_user})


@features_api_bp.patch('/candidate/profile')
@api_role_required('candidate')
def update_candidate_profile():
    payload = request.get_json(silent=True) or {}
    if not isinstance(payload, dict):
        return jsonify({'error': 'JSON object required'}), 400
    allowed_fields = {'first_name', 'last_name', 'phone', 'skills', 'experience_years', 'location', 'preferred_roles', 'bio'}
    changes = {key: value for key, value in payload.items() if key in allowed_fields}
    if not changes:
        return jsonify({'error': 'No editable profile fields supplied'}), 400
    updated = UserRepository().update(session['user_id'], changes)
    if not updated:
        return jsonify({'error': 'Profile not found'}), 404
    AuditService().record(session['user_id'], 'profile.updated', {'fields': sorted(changes)})
    public_user = {key: value for key, value in updated.items() if key != 'password_hash'}
    session['user'] = public_user
    return jsonify({'profile': public_user})


@features_api_bp.get('/notifications')
@api_role_required('candidate', 'recruiter', 'admin')
def list_notifications():
    return jsonify({'notifications': NotificationService().for_user(session['user_id'])})


@features_api_bp.patch('/notifications/<notification_id>/read')
@api_role_required('candidate', 'recruiter', 'admin')
def read_notification(notification_id):
    item = NotificationService().mark_read(notification_id, session['user_id'])
    if not item:
        return jsonify({'error': 'Notification not found'}), 404
    return jsonify({'notification': item})


@features_api_bp.get('/interviews')
@api_role_required('candidate', 'recruiter', 'admin')
def list_interviews():
    user = session['user']
    service = InterviewService()
    if user['role'] == 'candidate':
        interviews = service.for_candidate(user['id'])
    elif user['role'] == 'recruiter':
        interviews = service.for_recruiter(user['id'])
    else:
        interviews = service.interviews.all()
    return jsonify({'interviews': interviews})


@features_api_bp.post('/interviews')
@api_role_required('recruiter')
def create_interview():
    payload = request.get_json(silent=True) or {}
    if not isinstance(payload, dict):
        return jsonify({'error': 'JSON object required'}), 400
    payload['recruiter_id'] = session['user_id']
    try:
        interview = InterviewService().schedule(payload)
    except (KeyError, ValueError) as exc:
        return jsonify({'error': str(exc)}), 400
    return jsonify({'interview': interview}), 201


@features_api_bp.post('/resumes')
@api_role_required('candidate')
def upload_resume():
    try:
        resume = ResumeService().save_resume(session['user_id'], request.files.get('resume'))
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400
    return jsonify({'resume': resume}), 201


@features_api_bp.get('/resumes/<resume_id>/download')
@api_role_required('candidate', 'recruiter', 'admin')
def download_resume(resume_id):
    service = ResumeService()
    user = session['user']
    candidate_id = user['id'] if user['role'] == 'candidate' else None
    resume = service.get_resume(resume_id, candidate_id)
    if not resume:
        return jsonify({'error': 'Resume not found'}), 404
    if user['role'] == 'recruiter':
        from app.repositories.application_repository import ApplicationRepository
        from app.repositories.job_repository import JobRepository

        candidate_application_ids = {
            application['candidate_id']
            for application in ApplicationRepository().all()
            if application.get('candidate_id') == resume['candidate_id']
            and (job := JobRepository().get_by_id(application.get('job_id')))
            and job.get('recruiter_id') == user['id']
        }
        if resume['candidate_id'] not in candidate_application_ids:
            return jsonify({'error': 'Forbidden'}), 403
    try:
        content = service.content_for(resume)
    except (FileNotFoundError, ValueError):
        return jsonify({'error': 'Resume file is missing'}), 404
    return send_file(content, as_attachment=True, download_name=resume['filename'])


@features_api_bp.get('/admin/audit-logs')
@api_role_required('admin')
def audit_logs():
    return jsonify({'audit_logs': AuditService().recent()})
