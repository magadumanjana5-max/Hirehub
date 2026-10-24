from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app.services.application_service import ApplicationService
from app.services.job_service import JobService
from app.services.resume_service import ResumeService

job_bp = Blueprint('job', __name__, url_prefix='/jobs')


@job_bp.route('/')
@job_bp.route('')
def list_jobs():
    query = request.args.get('q')
    location = request.args.get('location')
    employment_type = request.args.get('employment_type')
    jobs = JobService().list_jobs(query=query, location=location, employment_type=employment_type)
    return render_template('jobs/list.html', jobs=jobs)


@job_bp.route('/<job_id>')
def detail(job_id):
    job = JobService().get_job(job_id)
    resumes = []
    user = session.get('user')
    if user and user.get('role') == 'candidate':
        resumes = ResumeService().for_candidate(user['id'])
    return render_template('jobs/detail.html', job=job, resumes=resumes)


@job_bp.route('/<job_id>/apply', methods=['POST'])
def apply(job_id):
    user = session.get('user')
    if not user:
        return redirect(url_for('auth.login'))
    if user.get('role') != 'candidate':
        return redirect(url_for('dashboard.index'))
    resume_id = request.form.get('resume_id', '')
    payload = {'job_id': job_id, 'candidate_id': user['id']}
    if resume_id:
        resume = ResumeService().get_resume(resume_id, user['id'])
        if not resume:
            flash('Select one of your uploaded resumes.', 'danger')
            return redirect(url_for('job.detail', job_id=job_id))
        payload['resume_id'] = resume_id
        payload['resume_url'] = resume['filename']
    try:
        ApplicationService().apply(payload)
        flash('Application submitted successfully.', 'success')
    except ValueError as exc:
        flash(str(exc), 'warning')
    return redirect(url_for('candidate.applications'))
