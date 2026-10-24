from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app.repositories.application_repository import ApplicationRepository
from app.repositories.job_repository import JobRepository
from app.repositories.user_repository import UserRepository
from app.services.application_service import ApplicationService
from app.services.audit_service import AuditService
from app.services.interview_service import InterviewService
from app.services.job_service import JobService
from app.services.notification_service import NotificationService
from app.services.recruiter_service import RecruiterService
from app.utils.auth import login_required, role_required

recruiter_bp = Blueprint('recruiter', __name__, url_prefix='/recruiter')


@recruiter_bp.route('/dashboard')
@login_required
@role_required('recruiter')
def dashboard():
    user = session.get('user')
    jobs = RecruiterService().list_jobs(user['id'])
    return render_template('recruiter/dashboard.html', user=user, jobs=jobs)


@recruiter_bp.route('/jobs', methods=['GET', 'POST'])
@login_required
@role_required('recruiter')
def jobs():
    user = session.get('user')
    if request.method == 'POST':
        payload = {
            'title': request.form['title'],
            'company_name': request.form.get('company_name', '').strip() or user.get('company_name', 'HireHub'),
            'location': request.form.get('location', 'Remote'),
            'employment_type': request.form.get('employment_type', 'Full-time'),
            'description': request.form.get('description', ''),
            'requirements': [item.strip() for item in request.form.get('requirements', '').split(',') if item.strip()],
            'salary': request.form.get('salary', ''),
            'recruiter_id': user['id'],
        }
        RecruiterService().create_job(payload)
        return redirect(url_for('recruiter.dashboard'))
    return render_template('recruiter/jobs.html', user=user)


@recruiter_bp.route('/candidates')
@login_required
@role_required('recruiter')
def candidates():
    user = session.get('user')
    candidates = [
        {key: value for key, value in candidate.items() if key != 'password_hash'}
        for candidate in UserRepository().get_by_role('candidate')
    ]
    return render_template('recruiter/candidates.html', user=user, candidates=candidates)


@recruiter_bp.route('/interviews')
@login_required
@role_required('recruiter')
def interviews():
    user = session.get('user')
    interviews = InterviewService().for_recruiter(user['id'])
    job_ids = {job['id'] for job in RecruiterService().list_jobs(user['id'])}
    applications = []
    users = UserRepository()
    for job_id in job_ids:
        job = JobRepository().get_by_id(job_id)
        for application in ApplicationRepository().by_job(job_id):
            candidate = users.get_by_id(application['candidate_id']) or {}
            applications.append({
                'id': application['id'],
                'job_title': job.get('title', '') if job else '',
                'candidate_name': f"{candidate.get('first_name', '')} {candidate.get('last_name', '')}".strip(),
                'candidate_email': candidate.get('email', ''),
            })
    for interview in interviews:
        candidate = users.get_by_id(interview.get('candidate_id')) or {}
        interview['candidate_name'] = f"{candidate.get('first_name', '')} {candidate.get('last_name', '')}".strip()
    return render_template('recruiter/interviews.html', user=user, interviews=interviews, applications=applications)


@recruiter_bp.route('/applications')
@login_required
@role_required('recruiter')
def applications():
    user = session['user']
    jobs = RecruiterService().list_jobs(user['id'])
    applications = []
    users = UserRepository()
    for job in jobs:
        for application in ApplicationRepository().by_job(job['id']):
            candidate = users.get_by_id(application['candidate_id']) or {}
            applications.append({
                **application,
                'job_title': job.get('title', ''),
                'candidate_name': f"{candidate.get('first_name', '')} {candidate.get('last_name', '')}".strip(),
                'candidate_email': candidate.get('email', ''),
                'resume_id': application.get('resume_id'),
            })
    return render_template('recruiter/applications.html', applications=applications)


@recruiter_bp.post('/applications/<application_id>/status')
@login_required
@role_required('recruiter')
def update_application_status(application_id):
    application = ApplicationRepository().get_by_id(application_id)
    if not application:
        return {'message': 'Application not found'}, 404
    job = JobRepository().get_by_id(application['job_id'])
    if not job or job.get('recruiter_id') != session['user_id']:
        return {'message': 'Not authorized'}, 403
    try:
        ApplicationService().update_status(application_id, request.form.get('status', ''))
    except ValueError as exc:
        flash(str(exc), 'danger')
    else:
        flash('Application status updated.', 'success')
    return redirect(url_for('recruiter.applications'))


@recruiter_bp.route('/interviews/schedule', methods=['POST'])
@login_required
@role_required('recruiter')
def schedule_interview():
    try:
        InterviewService().schedule({
            'application_id': request.form.get('application_id', ''),
            'recruiter_id': session['user_id'],
            'scheduled_at': request.form.get('scheduled_at', ''),
            'mode': request.form.get('mode', 'virtual'),
            'notes': request.form.get('notes', ''),
        })
    except (KeyError, ValueError) as exc:
        flash(str(exc) or 'Provide an application and interview time.', 'danger')
    else:
        flash('Interview scheduled and candidate notified.', 'success')
    return redirect(url_for('recruiter.interviews'))


@recruiter_bp.post('/jobs/<job_id>/status')
@login_required
@role_required('recruiter')
def update_job_status(job_id):
    status = request.form.get('status')
    try:
        JobService().update_job(job_id, {'status': status}, session['user_id'])
    except PermissionError:
        return {'message': 'Not authorized'}, 403
    except ValueError as exc:
        flash(str(exc), 'danger')
    else:
        flash('Job status updated.', 'success')
    return redirect(url_for('recruiter.dashboard'))


@recruiter_bp.route('/notifications')
@login_required
@role_required('recruiter')
def notifications():
    items = NotificationService().for_user(session['user_id'])
    return render_template('recruiter/notifications.html', notifications=items)


@recruiter_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@role_required('recruiter')
def profile():
    repository = UserRepository()
    user_id = session['user_id']
    if request.method == 'POST':
        changes = {
            'first_name': request.form.get('first_name', '').strip(),
            'last_name': request.form.get('last_name', '').strip(),
            'company_name': request.form.get('company_name', '').strip(),
            'department': request.form.get('department', '').strip(),
            'phone': request.form.get('phone', '').strip(),
        }
        updated = repository.update(user_id, changes)
        if not updated:
            return {'message': 'Profile not found'}, 404
        session['user'] = {key: value for key, value in updated.items() if key != 'password_hash'}
        AuditService().record(user_id, 'profile.updated')
        return redirect(url_for('recruiter.profile'))
    user = repository.get_by_id(user_id)
    if user:
        user = {key: value for key, value in user.items() if key != 'password_hash'}
    return render_template('account/profile.html', user=user)
