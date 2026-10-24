# HireHub API

## Auth endpoints
- POST /api/auth/register
- POST /api/auth/login
- POST /api/auth/logout
  - Authenticated routes use the Flask session cookie.

## Job endpoints
- GET /api/jobs
- POST /api/jobs (recruiter)
- PATCH /api/jobs/<job_id> (owning recruiter)

## Application endpoints
- POST /api/applications (candidate)
- GET /api/applications (role-scoped)
- GET /api/applications/<application_id> (role-scoped)
- PATCH /api/applications/<application_id>/status (owning recruiter)

## Analytics endpoints
- GET /api/analytics/dashboard (admin)
- GET /api/reports (admin)

## Additional endpoints
- GET/PATCH /api/candidate/profile (candidate)
- GET /api/notifications and PATCH /api/notifications/<id>/read (authenticated user)
- GET/POST /api/interviews (role-scoped; creation for recruiters)
- POST /api/resumes and GET /api/resumes/<id>/download
- GET /api/admin/audit-logs (admin)

All endpoint data is read from or written to the configured MongoDB database. Resume file bytes are stored in GridFS.
