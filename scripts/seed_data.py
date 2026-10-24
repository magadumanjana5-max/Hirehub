"""Ensure the default development data exists in MongoDB."""

from app import create_app


def seed_data():
    app = create_app()
    app.config['MONGO_CLIENT'].close()
    print('MongoDB seed data is ready.')


if __name__ == '__main__':
    seed_data()
