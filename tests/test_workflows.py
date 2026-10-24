from io import BytesIO


def login(client, email, password):
    return client.post(
        '/login',
        data={'email': email, 'password': password},
        follow_redirects=False,
    )


def test_registration_hashes_password_and_rejects_admin_self_signup(app_client):
    response = app_client.post(
        '/register',
        data={
            'email': 'created@example.com',
            'password': 'strong-password',
            'role': 'candidate',
        },
    )
    assert response.status_code == 302
    user = next(
        item for item in app_client.application.config['DATA_STORE']['users']
        if item['email'] == 'created@example.com'
    )
    assert user['password_hash'] != 'strong-password'
    with app_client.session_transaction() as session:
        assert 'password_hash' not in session['user']
        assert session.permanent is True

    response = app_client.post(
        '/api/auth/register',
        json={'email': 'admin2@example.com', 'password': 'password', 'role': 'admin'},
    )
    assert response.status_code == 400


def test_candidate_application_tracking_and_resume_download(app_client):
    login(app_client, 'candidate@hirehub.local', 'Candidate@123')
    response = app_client.post('/jobs/job-frontend-1/apply')
    assert response.status_code == 302

    response = app_client.get('/candidate/applications')
    assert response.status_code == 200
    assert b'Senior Frontend Engineer' in response.data

    duplicate = app_client.post('/jobs/job-frontend-1/apply')
    assert duplicate.status_code == 302
    response = app_client.get('/candidate/applications')
    assert response.data.count(b'Senior Frontend Engineer') == 1

    uploaded = app_client.post(
        '/candidate/resume',
        data={'resume': (BytesIO(b'%PDF test'), 'candidate.pdf')},
        content_type='multipart/form-data',
    )
    assert uploaded.status_code == 302
    resume = app_client.application.config['DATA_STORE']['resumes'][0]
    download = app_client.get(f"/candidate/resume/{resume['id']}/download")
    assert download.status_code == 200
    assert download.data == b'%PDF test'


def test_recruiter_can_manage_jobs_applications_interviews_and_notifications(app_client):
    login(app_client, 'recruiter@hirehub.local', 'Recruiter@123')
    create_job = app_client.post(
        '/recruiter/jobs',
        data={
            'title': 'QA Engineer',
            'company_name': 'HireHub Labs',
            'location': 'Remote',
            'employment_type': 'Full-time',
            'description': 'Test product quality.',
            'requirements': 'Testing, Python',
        },
    )
    assert create_job.status_code == 302
    jobs = app_client.application.config['DATA_STORE']['jobs']
    created_job = next(job for job in jobs if job['title'] == 'QA Engineer')

    login(app_client, 'candidate@hirehub.local', 'Candidate@123')
    app_client.post(f"/jobs/{created_job['id']}/apply")
    login(app_client, 'recruiter@hirehub.local', 'Recruiter@123')

    response = app_client.get('/recruiter/applications')
    assert response.status_code == 200
    assert b'Demo Candidate' in response.data

    application = next(
        item for item in app_client.application.config['DATA_STORE']['applications']
        if item['job_id'] == created_job['id']
    )
    response = app_client.post(
        f"/recruiter/applications/{application['id']}/status",
        data={'status': 'screening'},
    )
    assert response.status_code == 302
    assert application['status'] == 'screening'

    response = app_client.post(
        '/recruiter/interviews/schedule',
        data={
            'application_id': application['id'],
            'scheduled_at': '2026-11-01T10:00',
            'mode': 'virtual',
            'notes': 'Technical interview',
        },
    )
    assert response.status_code == 302
    assert len(app_client.application.config['DATA_STORE']['interviews']) == 2
    assert app_client.application.config['DATA_STORE']['notifications']


def test_admin_analytics_reports_audit_and_role_boundaries(app_client):
    login(app_client, 'admin@hirehub.local', 'Admin@123')
    for path in ('/admin/dashboard', '/admin/users', '/admin/analytics', '/admin/reports', '/admin/audit-logs'):
        assert app_client.get(path).status_code == 200
    assert app_client.get('/admin/profile').status_code == 200
    assert app_client.get('/admin/reports.csv').mimetype == 'text/csv'
    assert app_client.get('/api/analytics/dashboard').status_code == 200
    assert app_client.get('/api/reports').status_code == 200

    login(app_client, 'candidate@hirehub.local', 'Candidate@123')
    assert app_client.get('/admin/users').status_code == 302
    assert app_client.get('/api/analytics/dashboard').status_code == 403
    assert app_client.get('/api/applications').status_code == 200
    assert app_client.get('/api/notifications').status_code == 200


def test_recruiter_profile_page_does_not_remove_password_hash(app_client):
    login(app_client, 'recruiter@hirehub.local', 'Recruiter@123')
    response = app_client.get('/recruiter/profile')
    assert response.status_code == 200
    recruiter = next(
        item for item in app_client.application.config['DATA_STORE']['users']
        if item['id'] == 'default-recruiter'
    )
    assert recruiter.get('password_hash')


def test_logout_clears_session_and_api_requires_authentication(app_client):
    response = login(app_client, 'candidate@hirehub.local', 'Candidate@123')
    cookie = response.headers['Set-Cookie']
    assert 'HttpOnly' in cookie
    assert 'SameSite=Lax' in cookie
    response = app_client.post('/logout', follow_redirects=False)
    assert response.status_code == 302
    with app_client.session_transaction() as session:
        assert 'user_id' not in session
    assert app_client.post('/api/applications', json={'job_id': 'job-frontend-1'}).status_code == 401


def test_profile_reads_and_updates_never_remove_password_hash(app_client):
    login(app_client, 'admin@hirehub.local', 'Admin@123')
    response = app_client.get('/admin/profile')
    assert response.status_code == 200
    admin = next(
        item for item in app_client.application.config['DATA_STORE']['users']
        if item['id'] == 'default-admin'
    )
    assert admin.get('password_hash')
    response = app_client.post('/admin/profile', data={'first_name': 'Updated', 'last_name': 'Admin'})
    assert response.status_code == 302
    assert admin.get('password_hash')

    login(app_client, 'candidate@hirehub.local', 'Candidate@123')
    profile = app_client.get('/api/candidate/profile')
    assert profile.status_code == 200
    assert 'password_hash' not in profile.get_json()['profile']
    candidate = next(
        item for item in app_client.application.config['DATA_STORE']['users']
        if item['id'] == 'default-candidate'
    )
    assert candidate.get('password_hash')


def test_job_search_filters_and_closed_jobs_reject_applications(app_client):
    response = app_client.get('/api/jobs?location=Nairobi&employment_type=Hybrid')
    assert response.status_code == 200
    assert [job['title'] for job in response.get_json()['jobs']] == ['Senior Frontend Engineer']

    login(app_client, 'recruiter@hirehub.local', 'Recruiter@123')
    app_client.post('/recruiter/jobs/job-frontend-1/status', data={'status': 'closed'})
    login(app_client, 'candidate@hirehub.local', 'Candidate@123')
    app_client.post('/jobs/job-frontend-1/apply')
    response = app_client.get('/candidate/applications')
    assert b'This job is no longer accepting applications' in response.data
