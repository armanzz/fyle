import pytest
import json
import logging
from core import db
from tests import app

@pytest.fixture
def client():
    return app.test_client()

@pytest.fixture
def h_student_1():
    headers = {
        'X-Principal': json.dumps({
            'student_id': 1,
            'user_id': 1
        })
    }
    return headers

@pytest.fixture
def h_student_2():
    headers = {
        'X-Principal': json.dumps({
            'student_id': 2,
            'user_id': 2
        })
    }
    return headers

@pytest.fixture
def h_teacher_1():
    headers = {
        'X-Principal': json.dumps({
            'teacher_id': 1,
            'user_id': 3
        })
    }
    return headers

@pytest.fixture
def h_teacher_2():
    headers = {
        'X-Principal': json.dumps({
            'teacher_id': 2,
            'user_id': 4
        })
    }
    return headers

@pytest.fixture
def h_principal():
    headers = {
        'X-Principal': json.dumps({
            'principal_id': 1,
            'user_id': 5
        })
    }
    return headers


@pytest.fixture(autouse=True)
def run_around_tests():
    """Wrap each test in a transaction and rollback at the end."""
    with app.app_context():  # Ensure the application context is active
        # Start a transaction
        app.logger.setLevel(logging.DEBUG)
        connection = db.engine.connect()
        transaction = connection.begin()

        # Override db.session for the test
        db.session = db._make_scoped_session({'bind': connection, 'binds': {}})

        yield  # Run the test

        # Rollback the transaction and close the connection after each test
        transaction.rollback()
        connection.close()
        db.session.remove()
