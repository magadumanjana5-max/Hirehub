import csv
import io

from flask import Blueprint, Response, redirect, render_template, request, session, url_for

from app.repositories.user_repository import UserRepository
from app.services.audit_service import AuditService
from app.services.analytics_service import AnalyticsService
from app.services.report_service import ReportService
from app.repositories.application_repository import ApplicationRepository
from app.repositories.job_repository import JobRepository
from app.utils.auth import login_required, role_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/dashboard')
@login_required
@role_required('admin')
def dashboard():
    user = session.get('user')
    stats = AnalyticsService().dashboard()
    return render_template('admin/dashboard.html', user=user, stats=stats)


@admin_bp.route('/users')
@login_required
@role_required('admin')
def users():
    user = session.get('user')
    user_list = [
        {key: value for key, value in record.items() if key != 'password_hash'}
        for record in UserRepository().all()
    ]
    return render_template('admin/users.html', user=user, users=user_list)


@admin_bp.route('/analytics')
@login_required
@role_required('admin')
def analytics():
    user = session.get('user')
    stats = AnalyticsService().dashboard()
    return render_template('admin/analytics.html', user=user, stats=stats)


@admin_bp.route('/reports')
@login_required
@role_required('admin')
def reports():
    user = session.get('user')
    stats = AnalyticsService().dashboard()
    report = ReportService().build_report(JobRepository().all(), ApplicationRepository().all())
    return render_template('admin/reports.html', user=user, stats=stats, report=report)


@admin_bp.get('/reports.csv')
@login_required
@role_required('admin')
def export_reports():
    report = ReportService().build_report(JobRepository().all(), ApplicationRepository().all())
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Metric', 'Value'])
    writer.writerow(['Total jobs', report['total_jobs']])
    writer.writerow(['Total applications', report['total_applications']])
    for title in report['job_titles']:
        writer.writerow(['Job title', title])
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=hirehub-report.csv'},
    )


@admin_bp.get('/audit-logs')
@login_required
@role_required('admin')
def audit_logs():
    return render_template('admin/audit_logs.html', logs=AuditService().recent())


@admin_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def profile():
    user = session['user']
    repository = UserRepository()
    if request.method == 'POST':
        changes = {
            'first_name': request.form.get('first_name', '').strip(),
            'last_name': request.form.get('last_name', '').strip(),
        }
        updated = repository.update(user['id'], changes)
        if updated:
            session['user'] = {key: value for key, value in updated.items() if key != 'password_hash'}
            AuditService().record(user['id'], 'profile.updated')
            return redirect(url_for('admin.profile'))
        return {'message': 'Profile not found'}, 404
    profile_user = repository.get_by_id(user['id'])
    if profile_user:
        profile_user = {key: value for key, value in profile_user.items() if key != 'password_hash'}
    return render_template('account/profile.html', user=profile_user)
