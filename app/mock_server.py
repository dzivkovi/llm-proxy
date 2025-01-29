#!/usr/bin/env python
import random
import json
import time
import uuid
from flask import Flask, request, jsonify, Response

app = Flask(__name__)

# Simple mock responses that look "wise" but are generic enough
MOCK_RESPONSES = [
    "Based on the context, I recommend this approach...",
    "Here's a solution that should work well...",
    "Looking at your code, I suggest...",
    "Let me help you improve this code...",
    "I see what you're trying to do. Consider this alternative...",
    "The code could be optimized by...",
    "Here's how we can enhance this implementation...",
]


def generate_stream_response(content: str):
    """Generate streaming response in OpenAI format."""
    # First chunk with role
    yield "data: " + json.dumps({
        "id": f"chatcmpl-{random.randint(1000,9999)}",
        "object": "chat.completion.chunk",
        "created": int(time.time()),
        "model": "gpt-3.5-turbo",
        "choices": [{"index": 0, "delta": {"role": "assistant"}, "finish_reason": None}]
    }) + "\n\n"

    # Content chunks (simulate typing)
    words = content.split()
    for word in words:
        chunk = {
            "id": f"chatcmpl-{random.randint(1000,9999)}",
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": "gpt-3.5-turbo",
            "choices": [{"index": 0, "delta": {"content": word + " "}, "finish_reason": None}]
        }
        yield "data: " + json.dumps(chunk) + "\n\n"
        time.sleep(0.1)  # Simulate typing delay

    # Final chunk
    yield "data: " + json.dumps({
        "id": f"chatcmpl-{random.randint(1000,9999)}",
        "object": "chat.completion.chunk",
        "created": int(time.time()),
        "model": "gpt-3.5-turbo",
        "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}]
    }) + "\n\n"

    # End stream
    yield "data: [DONE]\n\n"


@app.route("/v1/chat/completions", methods=["POST"])
def chat_completions():
    # Log the entire incoming request
    print("\n=== Incoming Request ===")
    print(f"Headers: {dict(request.headers)}")
    print(f"Data: {request.get_json()}")
    print("========================\n")

    data = request.get_json()
    is_streaming = data.get('stream', False)

    if is_streaming:
        content = random.choice(MOCK_RESPONSES)
        return Response(
            generate_stream_response(content),
            mimetype='text/event-stream'
        )

    # Non-streaming response (same as before)
    response_body = {
        "id": f"chatcmpl-{uuid.uuid4().hex[:12]}",  # OpenAI-like ID
        "object": "chat.completion",
        "created": int(time.time()),  # Current Unix timestamp
        "model": data.get("model", "gpt-3.5-turbo"),
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": random.choice(MOCK_RESPONSES),
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 50, "completion_tokens": 30, "total_tokens": 80},
    }

    return jsonify(response_body)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8888, debug=True)
