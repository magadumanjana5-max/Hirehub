import pytest

from app import create_app
from app.config import Config


@pytest.fixture()
def app_client(tmp_path):
    test_config = type(
        'TestConfig',
        (Config,),
        {
            'TESTING': True,
            'SECRET_KEY': 'test-secret-key',
            'USE_IN_MEMORY_DB': True,
        },
    )

    app = create_app(test_config)
    app.config['UPLOAD_FOLDER'] = str(tmp_path)
    with app.test_client() as client:
        yield client
