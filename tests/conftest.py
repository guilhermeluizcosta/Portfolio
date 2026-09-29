import os

import pytest

os.environ["secret_key"] = "test-secret-key"
os.environ["CHAT_QUESTION_LIMIT"] = "7"
os.environ["CHAT_REQUEST_TIMEOUT"] = "120"

TEST_CHAT_API_URL = "http://test-api.example/api/v1/chat"
os.environ["CHAT_API_URL"] = TEST_CHAT_API_URL


@pytest.fixture
def app():

    from app import create_app

    application = create_app()
    application.config.update(
        TESTING=True,
        SECRET_KEY="test-secret-key",
        CHAT_API_URL=TEST_CHAT_API_URL,
        CHAT_QUESTION_LIMIT=7,
        CHAT_REQUEST_TIMEOUT=120,
    )
    return application



@pytest.fixture
def client(app):

    return app.test_client()