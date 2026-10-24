from flask import Blueprint, jsonify
from app.repositories.application_repository import ApplicationRepository
from app.repositories.job_repository import JobRepository

from app.services.analytics_service import AnalyticsService
from app.services.report_service import ReportService
from app.utils.auth import api_role_required
from app.utils.auth import api_role_required

analytics_api_bp = Blueprint('analytics_api', __name__, url_prefix='/api')


@analytics_api_bp.get('/analytics/dashboard')
@api_role_required('admin')
def analytics_dashboard():
    data = AnalyticsService().dashboard()
    return jsonify(data)


@analytics_api_bp.get('/reports')
@api_role_required('admin')
def reports_api():
    report = ReportService().build_report(JobRepository().all(), ApplicationRepository().all())
    return jsonify(report)
