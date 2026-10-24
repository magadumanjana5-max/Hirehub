import os
from flask import Flask
from werkzeug.security import generate_password_hash

from app.config import Config
from app.extensions import init_mongodb
from app.routes.api.auth_api import auth_api_bp
from app.routes.api.job_api import job_api_bp
from app.routes.api.application_api import application_api_bp
from app.routes.api.analytics_api import analytics_api_bp
from app.routes.api.features_api import features_api_bp
from app.routes.web.auth_routes import auth_bp
from app.routes.web.job_routes import job_bp
from app.routes.web.candidate_routes import candidate_bp
from app.routes.web.recruiter_routes import recruiter_bp
from app.routes.web.admin_routes import admin_bp
from app.routes.web.dashboard_routes import dashboard_bp


def _seed_default_users(app):
    store = app.config.setdefault('DATA_STORE', {
        'users': [],
        'companies': [],
        'jobs': [],
        'applications': [],
        'interviews': [],
        'notifications': [],
        'resumes': [],
        'audit_logs': [],
    })
    database = app.config.get('MONGO_DB')
    if database is not None and database['users'].count_documents({}) > 0:
        return

    users = store.setdefault('users', [])
    if database is None and users:
        return

    default_users = [
        {
            'id': 'default-admin',
            'email': os.getenv('DEFAULT_ADMIN_EMAIL', 'admin@hirehub.local'),
            'password_hash': generate_password_hash(os.getenv('DEFAULT_ADMIN_PASSWORD', 'Admin@123')),
            'role': 'admin',
            'first_name': 'System',
            'last_name': 'Admin',
            'skills': ['Operations', 'Compliance', 'Reporting'],
            'preferred_roles': ['Admin'],
            'location': 'Nairobi',
            'bio': 'Platform administrator and hiring operations lead.',
            'is_active': True,
        },
        {
            'id': 'default-recruiter',
            'email': os.getenv('DEFAULT_RECRUITER_EMAIL', 'recruiter@hirehub.local'),
            'password_hash': generate_password_hash(os.getenv('DEFAULT_RECRUITER_PASSWORD', 'Recruiter@123')),
            'role': 'recruiter',
            'first_name': 'Demo',
            'last_name': 'Recruiter',
            'company_name': 'HireHub Labs',
            'department': 'Engineering',
            'skills': ['Hiring', 'Talent Mapping', 'Interviewing'],
            'preferred_roles': ['Recruiter'],
            'location': 'Nairobi',
            'bio': 'Recruiting partner focused on hiring top engineering talent.',
            'is_active': True,
        },
        {
            'id': 'default-candidate',
            'email': os.getenv('DEFAULT_CANDIDATE_EMAIL', 'candidate@hirehub.local'),
            'password_hash': generate_password_hash(os.getenv('DEFAULT_CANDIDATE_PASSWORD', 'Candidate@123')),
            'role': 'candidate',
            'first_name': 'Demo',
            'last_name': 'Candidate',
            'skills': ['Python', 'Flask', 'MongoDB', 'SQL', 'REST APIs'],
            'preferred_roles': ['Backend Developer', 'Full Stack Developer'],
            'location': 'Nairobi',
            'bio': 'Software engineer looking for backend and product-focused roles.',
            'is_active': True,
        },
    ]
    users.extend(default_users)

    jobs = store.setdefault('jobs', [])
    if not jobs:
        jobs.extend([
            {
                'id': 'job-python-1',
                'title': 'Python Backend Engineer',
                'company_name': 'HireHub Labs',
                'location': 'Remote',
                'employment_type': 'Full-time',
                'description': 'Build resilient backend APIs, automation workflows, and data integrations.',
                'requirements': ['Python', 'Flask', 'REST APIs', 'SQL'],
                'salary': '$120k - $150k',
                'recruiter_id': 'default-recruiter',
                'status': 'open',
            },
            {
                'id': 'job-frontend-1',
                'title': 'Senior Frontend Engineer',
                'company_name': 'Northstar Studio',
                'location': 'Nairobi',
                'employment_type': 'Hybrid',
                'description': 'Own the web app interface, design system, and performance tuning.',
                'requirements': ['JavaScript', 'React', 'UI Design', 'Performance'],
                'salary': '$100k - $130k',
                'recruiter_id': 'default-recruiter',
                'status': 'open',
            },
            {
                'id': 'job-ml-1',
                'title': 'Data Analyst',
                'company_name': 'InsightCore',
                'location': 'Remote',
                'employment_type': 'Contract',
                'description': 'Turn hiring and product performance data into measurable insights for the business.',
                'requirements': ['SQL', 'Python', 'Analytics', 'Dashboards'],
                'salary': '$80k - $110k',
                'recruiter_id': 'default-recruiter',
                'status': 'open',
            },
        ])

    applications = store.setdefault('applications', [])
    if not applications:
        applications.extend([
            {
                'id': 'app-1',
                'job_id': 'job-python-1',
                'candidate_id': 'default-candidate',
                'resume_url': 'uploads/resumes/demo-candidate.pdf',
                'status': 'applied',
            },
            {
                'id': 'app-2',
                'job_id': 'job-ml-1',
                'candidate_id': 'default-candidate',
                'resume_url': 'uploads/resumes/demo-candidate.pdf',
                'status': 'screening',
            },
        ])

    interviews = store.setdefault('interviews', [])
    if not interviews:
        interviews.extend([
            {
                'id': 'int-1',
                'application_id': 'app-1',
                'candidate_id': 'default-candidate',
                'recruiter_id': 'default-recruiter',
                'scheduled_at': '2026-10-30 14:00',
                'mode': 'virtual',
                'notes': 'System design and Python coding round.',
            },
        ])

    notifications = store.setdefault('notifications', [])
    if not notifications:
        notifications.extend([
            {'id': 'note-1', 'user_id': 'default-candidate', 'message': 'Your application for Python Backend Engineer is under review.', 'type': 'info', 'is_read': False},
            {'id': 'note-2', 'user_id': 'default-recruiter', 'message': 'Two new candidates match the backend engineering role.', 'type': 'success', 'is_read': False},
            {'id': 'note-3', 'user_id': 'default-admin', 'message': 'Weekly hiring insights report is ready.', 'type': 'info', 'is_read': True},
        ])

    if database is not None:
        for collection_name, records in store.items():
            if records and database[collection_name].count_documents({}) == 0:
                database[collection_name].insert_many(records)


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', app.config.get('SECRET_KEY', 'dev-secret-key'))
    if app.config.get('USE_IN_MEMORY_DB'):
        app.config.setdefault('DATA_STORE', {
            'users': [],
            'companies': [],
            'jobs': [],
            'applications': [],
            'interviews': [],
            'notifications': [],
            'resumes': [],
            'audit_logs': [],
        })
    else:
        init_mongodb(app)
    _seed_default_users(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(job_bp)
    app.register_blueprint(candidate_bp)
    app.register_blueprint(recruiter_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(auth_api_bp)
    app.register_blueprint(job_api_bp)
    app.register_blueprint(application_api_bp)
    app.register_blueprint(analytics_api_bp)
    app.register_blueprint(features_api_bp)

    @app.get('/health')
    def health_check():
        return {'status': 'ok', 'app': 'HireHub'}, 200

    @app.errorhandler(404)
    def not_found(_error):
        return {'message': 'Not found'}, 404

    return app
