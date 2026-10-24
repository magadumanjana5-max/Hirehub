# HireHub

HireHub is a Flask-based recruitment and hiring portal built for candidates, recruiters, and admins.

## Features
- Candidate registration and login
- Recruiter and admin roles
- Job listing, search, filtering, and applications
- Resume upload and download
- Interview scheduling and notifications
- REST APIs for jobs and analytics
- Bootstrap-based responsive UI

## Default credentials
Use these credentials when you want to log in immediately in development mode:

- Admin: `admin@hirehub.local` / `Admin@123`
- Recruiter: `recruiter@hirehub.local` / `Recruiter@123`
- Candidate: `candidate@hirehub.local` / `Candidate@123`

## Run locally
```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows PowerShell
pip install -r requirements.txt
python run.py
```

Ensure MongoDB is running locally, or set `MONGODB_URI` in `.env` to your MongoDB connection string. The app creates the `hirehub` database and seeds demo records when its `users` collection is empty. Data is stored in MongoDB and persists across app restarts.

The database name can be changed with `MONGODB_DATABASE`. User accounts, profiles, jobs, applications, interviews, notifications, analytics source records, and audit logs use MongoDB collections. Resume file contents use MongoDB GridFS. If MongoDB is unavailable, the app reports a connection error instead of silently switching to temporary storage.

Available workflows include candidate applications and tracking, recruiter job/application/interview management, candidate resume upload/download, in-app notifications, role-specific reports and analytics, and admin audit logs. Web and REST API routes enforce role permissions.

Create or verify indexes with:
```powershell
python scripts/create_indexes.py
```

Then open:
- http://localhost:5000

## Default login flow
1. Visit `/login`
2. Use one of the default credentials above
3. After login, you will be redirected to the role-based dashboard
