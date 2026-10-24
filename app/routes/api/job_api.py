from flask import Blueprint, jsonify, request, session

from app.repositories.job_repository import JobRepository
from app.services.job_service import JobService
from app.utils.auth import api_role_required

job_api_bp = Blueprint('job_api', __name__, url_prefix='/api')


@job_api_bp.get('/jobs')
def list_jobs_api():
    jobs = JobService().list_jobs(request.args.get('q'), request.args.get('location'), request.args.get('employment_type'))
    return jsonify({'jobs': jobs})


@job_api_bp.post('/jobs')
@api_role_required('recruiter')
def create_job_api():
    payload = request.get_json(silent=True) or {}
    if not isinstance(payload, dict):
        return jsonify({'error': 'JSON object required'}), 400
    payload['recruiter_id'] = session['user_id']
    try:
        job = JobService().create_job(payload)
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400
    return jsonify({'message': 'Job created', 'job': job}), 201


@job_api_bp.patch('/jobs/<job_id>')
@api_role_required('recruiter')
def update_job_api(job_id):
    payload = request.get_json(silent=True) or {}
    if not isinstance(payload, dict):
        return jsonify({'error': 'JSON object required'}), 400
    try:
        updated = JobService().update_job(job_id, payload, session['user_id'])
    except PermissionError as exc:
        return jsonify({'error': str(exc)}), 403
    except ValueError as exc:
        status_code = 404 if str(exc) == 'Job not found' else 400
        return jsonify({'error': str(exc)}), status_code
    return jsonify({'job': updated})
