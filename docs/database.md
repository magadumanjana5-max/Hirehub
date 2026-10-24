# HireHub Database

The application uses PyMongo and the database configured by `MONGODB_DATABASE` (defaults to `hirehub`). The configured `MONGODB_URI` must point to a reachable MongoDB server. Application data is persisted across restarts.

Collections:
- users
- companies
- jobs
- applications
- interviews
- notifications
- resumes
- audit_logs

Resume file bytes are stored in the `resumes.files` and `resumes.chunks` GridFS collections. The `resumes` collection stores ownership and display metadata.

Indexes enforce unique user emails and prevent a candidate from applying to the same job more than once. `python scripts/create_indexes.py` creates those indexes and a job browsing index.

Tests explicitly enable the in-memory repository adapter; production and normal local app startup use MongoDB. The app intentionally fails to start when MongoDB is unavailable rather than silently dropping data into memory.
