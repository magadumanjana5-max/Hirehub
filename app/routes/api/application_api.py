from flask import Blueprint, jsonify, request, session
from app.repositories.application_repository import ApplicationRepository
from app.repositories.job_repository import JobRepository

from app.services.application_service import ApplicationService
from app.services.resume_service import ResumeService
from app.utils.auth import api_role_required

application_api_bp = Blueprint('application_api', __name__, url_prefix='/api')


@application_api_bp.post('/applications')
@api_role_required('candidate')
def apply_api():
    payload = request.get_json(silent=True) or {}
    if not isinstance(payload, dict):
        return jsonify({'error': 'JSON object required'}), 400
    payload['candidate_id'] = session['user_id']
    if payload.get('resume_id'):
        resume = ResumeService().get_resume(payload['resume_id'], session['user_id'])
        if not resume:
            return jsonify({'error': 'Resume not found'}), 400
        payload['resume_url'] = resume['filename']
    try:
        app = ApplicationService().apply(payload)
        return jsonify({'message': 'Application submitted', 'application': app}), 201
    except ValueError as exc:
        status_code = 404 if str(exc) == 'Job not found' else 409
        return jsonify({'error': str(exc)}), status_code


@application_api_bp.get('/applications/<application_id>')
@api_role_required('candidate', 'recruiter', 'admin')
def get_application(application_id):
    application = ApplicationRepository().get_by_id(application_id)
    if not application:
        return jsonify({'error': 'Application not found'}), 404
    user = session.get('user')
    if user['role'] == 'candidate' and application.get('candidate_id') != user['id']:
        return jsonify({'error': 'Forbidden'}), 403
    if user['role'] == 'recruiter':
        job = JobRepository().get_by_id(application.get('job_id'))
        if not job or job.get('recruiter_id') != user['id']:
            return jsonify({'error': 'Forbidden'}), 403
    return jsonify(application)


@application_api_bp.get('/applications')
@api_role_required('candidate', 'recruiter', 'admin')
def list_applications():
    user = session.get('user')
    repository = ApplicationRepository()
    if user['role'] == 'candidate':
        applications = repository.by_candidate(user['id'])
    elif user['role'] == 'recruiter':
        jobs = JobRepository().all()
        owned_job_ids = {job['id'] for job in jobs if job.get('recruiter_id') == user['id']}
        applications = [item for item in repository.all() if item.get('job_id') in owned_job_ids]
    else:
        applications = repository.all()
    return jsonify({'applications': applications})


@application_api_bp.patch('/applications/<application_id>/status')
@api_role_required('recruiter')
def update_application_status_api(application_id):
    application = ApplicationRepository().get_by_id(application_id)
    if not application:
        return jsonify({'error': 'Application not found'}), 404
    user = session.get('user')
    job = JobRepository().get_by_id(application.get('job_id'))
    if not job or job.get('recruiter_id') != user['id']:
        return jsonify({'error': 'Forbidden'}), 403
    payload = request.get_json(silent=True) or {}
    if not isinstance(payload, dict):
        return jsonify({'error': 'JSON object required'}), 400
    try:
        updated = ApplicationService().update_status(application_id, payload.get('status', ''))
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400
    return jsonify({'application': updated})
