import requests
import json


def test_mock_server_basic():
    """Test basic non-streaming response"""
    response = requests.post(
        "http://localhost:8888/v1/chat/completions",
        json={"messages": [{"role": "user", "content": "Hello!"}]},
        timeout=5,
    )
    assert response.status_code == 200
    assert "choices" in response.json()


def test_mock_server_streaming():
    """Test streaming response format and content"""
    response = requests.post(
        "http://localhost:8888/v1/chat/completions",
        json={
            "messages": [{"role": "user", "content": "Hello!"}],
            "stream": True,
        },
        stream=True,
        timeout=5,
    )

    assert response.status_code == 200

    # Parse streaming response
    got_role = False
    got_content = False
    got_done = False

    for line in response.iter_lines():
        # Skip empty lines
        if not line:
            continue

        # Remove "data: " prefix and parse JSON
        line = line.decode("utf-8")
        if not line.startswith("data: "):
            continue

        if line.strip() == "data: [DONE]":
            got_done = True
            continue

        data = json.loads(line[6:])  # Skip "data: " prefix

        # Validate response structure
        assert "id" in data
        assert data["id"].startswith("chatcmpl-")
        assert data["object"] == "chat.completion.chunk"
        assert "created" in data
        assert data["model"] == "gpt-3.5-turbo"
        assert len(data["choices"]) == 1
        assert data["choices"][0]["index"] == 0

        # Track what we've received
        delta = data["choices"][0]["delta"]
        if "role" in delta:
            assert delta["role"] == "assistant"
            got_role = True
        if "content" in delta:
            assert isinstance(delta["content"], str)
            got_content = True

    # Verify we got all expected parts
    assert got_role, "Did not receive role chunk"
    assert got_content, "Did not receive content chunks"
    assert got_done, "Did not receive DONE message"


if __name__ == "__main__":
    test_mock_server_basic()
    test_mock_server_streaming()
    print("All tests passed!")
