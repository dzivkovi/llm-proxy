import requests


def test_mock_server():
    response = requests.post(
        "http://localhost:8888/v1/chat/completions",
        json={"messages": [{"role": "user", "content": "Hello!"}]},
        timeout=5,
    )
    assert response.status_code == 200
    assert "choices" in response.json()
