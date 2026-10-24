from flask import Blueprint, flash, redirect, render_template, request, send_file, session, url_for

from app.services.application_service import ApplicationService
from app.services.candidate_service import CandidateService
from app.services.interview_service import InterviewService
from app.services.job_service import JobService
from app.services.notification_service import NotificationService
from app.services.resume_service import ResumeService
from app.services.audit_service import AuditService
from app.utils.auth import login_required, role_required

candidate_bp = Blueprint('candidate', __name__, url_prefix='/candidate')


@candidate_bp.route('/dashboard')
@login_required
@role_required('candidate')
def dashboard():
    user = session.get('user')
    service = CandidateService()
    jobs = JobService().list_jobs()
    recommendations = service.get_recommendations(user['id'])
    return render_template('candidate/dashboard.html', user=user, jobs=jobs, recommendations=recommendations)


@candidate_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@role_required('candidate')
def profile():
    user = session.get('user')
    service = CandidateService()
    if request.method == 'POST':
        payload = {
            'first_name': request.form.get('first_name', user.get('first_name', '')),
            'last_name': request.form.get('last_name', user.get('last_name', '')),
            'phone': request.form.get('phone', ''),
            'skills': [item.strip() for item in request.form.get('skills', '').split(',') if item.strip()],
            'experience_years': request.form.get('experience_years', type=int) or 0,
            'location': request.form.get('location', ''),
            'preferred_roles': [item.strip() for item in request.form.get('preferred_roles', '').split(',') if item.strip()],
            'bio': request.form.get('bio', ''),
        }
        updated = service.update_profile(user['id'], payload)
        if not updated:
            return {'message': 'Profile not found'}, 404
        session_user = service.get_profile(user['id'])
        session['user'] = {key: value for key, value in session_user.items() if key != 'password_hash'}
        AuditService().record(user['id'], 'profile.updated')
        flash('Profile updated.', 'success')
        return redirect(url_for('candidate.profile'))
    resumes = ResumeService().for_candidate(user['id'])
    return render_template(
        'candidate/profile.html',
        user=service.get_profile(user['id']),
        resumes=resumes,
    )


@candidate_bp.route('/applications')
@login_required
@role_required('candidate')
def applications():
    user = session.get('user')
    job_service = JobService()
    applications = ApplicationService().list_by_candidate(user['id'])
    application_rows = []
    for application in applications:
        job = job_service.get_job(application.get('job_id'))
        application_rows.append({
            'id': application.get('id'),
            'job_title': job.get('title', 'Unknown job') if job else 'Unknown job',
            'company': job.get('company_name', 'Unknown company') if job else 'Unknown company',
            'location': job.get('location', 'Remote') if job else 'Remote',
            'status': application.get('status', 'applied'),
            'applied_at': application.get('applied_at', 'Recently'),
            'resume_id': application.get('resume_id'),
        })
    return render_template('candidate/applications.html', applications=application_rows, user=user)


@candidate_bp.route('/resume', methods=['POST'])
@login_required
@role_required('candidate')
def upload_resume():
    resume_file = request.files.get('resume')
    try:
        resume = ResumeService().save_resume(session['user_id'], resume_file)
        flash(f"Resume '{resume['filename']}' uploaded.", 'success')
    except ValueError as exc:
        flash(str(exc), 'danger')
    return redirect(url_for('candidate.profile'))


@candidate_bp.route('/resume/<resume_id>/download')
@login_required
@role_required('candidate')
def download_resume(resume_id):
    service = ResumeService()
    resume = service.get_resume(resume_id, session['user_id'])
    if not resume:
        return {'message': 'Resume not found'}, 404
    try:
        content = service.content_for(resume)
    except (FileNotFoundError, ValueError):
        return {'message': 'Resume file is missing'}, 404
    return send_file(content, as_attachment=True, download_name=resume['filename'])


@candidate_bp.route('/notifications')
@login_required
@role_required('candidate')
def notifications():
    items = NotificationService().for_user(session['user_id'])
    return render_template('candidate/notifications.html', notifications=items)


@candidate_bp.post('/notifications/<notification_id>/read')
@login_required
@role_required('candidate')
def mark_notification_read(notification_id):
    item = NotificationService().mark_read(notification_id, session['user_id'])
    if not item:
        return {'message': 'Notification not found'}, 404
    return redirect(url_for('candidate.notifications'))


@candidate_bp.route('/interviews')
@login_required
@role_required('candidate')
def interviews():
    items = InterviewService().for_candidate(session['user_id'])
    return render_template('candidate/interviews.html', interviews=items)
