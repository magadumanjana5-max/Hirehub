"""Create MongoDB indexes for the HireHub application."""

from app import create_app


def create_indexes():
    app = create_app()
    database = app.config['MONGO_DB']
    database['users'].create_index('email', unique=True)
    database['applications'].create_index(
        [('candidate_id', 1), ('job_id', 1)],
        unique=True,
    )
    database['applications'].create_index([('job_id', 1), ('status', 1)])
    database['jobs'].create_index([('status', 1), ('created_at', -1)])
    database['notifications'].create_index([('user_id', 1), ('is_read', 1)])
    database['interviews'].create_index([('candidate_id', 1), ('scheduled_at', 1)])
    app.config['MONGO_CLIENT'].close()
    print('MongoDB indexes created.')


if __name__ == '__main__':
    create_indexes()
