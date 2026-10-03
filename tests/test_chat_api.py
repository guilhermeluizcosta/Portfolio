import responses

from tests.conftest import TEST_CHAT_API_URL


def test_chat_status_returns_initial_quota(client):
    """A new visitor should see the full question quota available."""
    response = client.get("/api/chat/status")

    assert response.status_code == 200
    assert response.get_json() == {
        "used": 0,
        "limit": 7,
        "remaining": 7,
    }


def test_chat_rejects_empty_question(client):
    """An empty question should be rejected before calling the assistant API."""
    response = client.post("/api/chat", json={"question": "   "})

    assert response.status_code == 400
    assert "error" in response.get_json()


@responses.activate
def test_chat_proxies_successful_answer(client):
    """A valid question should return the assistant answer and decrement the quota."""
    responses.add(
        responses.POST,
        TEST_CHAT_API_URL,
        json={"answer": "I am a Python developer."},
        status=200,
    )

    response = client.post("/api/chat", json={"question": "What do you do?"})

    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == TEST_CHAT_API_URL
    assert response.status_code == 200
    body = response.get_json()
    assert body["answer"] == "I am a Python developer."
    assert body["remaining"] == 6

    status = client.get("/api/chat/status").get_json()
    assert status["used"] == 1
    assert status["remaining"] == 6


@responses.activate
def test_chat_enforces_question_limit(client):
    """The eighth question in a session should be rejected with HTTP 429."""
    responses.add(
        responses.POST,
        TEST_CHAT_API_URL,
        json={"answer": "ok"},
        status=200,
    )

    for _ in range(7):
        response = client.post("/api/chat", json={"question": "Tell me more"})
        assert response.status_code == 200

    blocked = client.post("/api/chat", json={"question": "One more"})
    assert blocked.status_code == 429
    assert blocked.get_json()["remaining"] == 0


@responses.activate
def test_chat_returns_friendly_error_on_upstream_connection_failure(client):
    """An unreachable assistant API should surface a friendly unavailable message."""
    responses.add(
        responses.POST,
        TEST_CHAT_API_URL,
        body=responses.ConnectionError("connection refused"),
    )

    response = client.post("/api/chat", json={"question": "Hello?"})

    assert response.status_code == 503
    assert "error" in response.get_json()
    assert "500" not in response.get_json()["error"]
    assert "connection refused" not in response.get_json()["error"].lower()


@responses.activate
def test_chat_returns_friendly_error_on_upstream_timeout(client, monkeypatch):
    """A slow assistant startup should surface a friendly timeout message."""
    import requests as requests_lib

    def raise_timeout(*_args, **_kwargs):
        raise requests_lib.Timeout("timed out")

    monkeypatch.setattr("app.requests.post", raise_timeout)

    response = client.post("/api/chat", json={"question": "Hello?"})

    assert response.status_code == 504
    assert "error" in response.get_json()