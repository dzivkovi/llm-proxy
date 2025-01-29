#!/usr/bin/env python
from flask import Flask, request, jsonify
from typing import Dict, Any
import random
import time
import uuid

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

def calculate_tokens(text: str) -> int:
    """Rough approximation of tokens (1 token ≈ 4 chars)"""
    return len(text) // 4

@app.route("/v1/chat/completions", methods=["POST"])
def chat_completions():
    # Log the entire incoming request
    print("\n=== Incoming Request ===")
    print(f"Headers: {dict(request.headers)}")
    print(f"Data: {request.get_json()}")
    print("=====================\n")

    data = request.get_json()
    response_content = random.choice(MOCK_RESPONSES)
    
    # Calculate realistic token counts
    prompt_tokens = sum(calculate_tokens(msg.get("content", "")) for msg in data.get("messages", []))
    completion_tokens = calculate_tokens(response_content)

    # Return a response with realistic metadata
    response_body = {
        "id": f"chatcmpl-{uuid.uuid4().hex[:12]}", # OpenAI-like ID
        "object": "chat.completion",
        "created": int(time.time()),  # Current Unix timestamp
        "model": data.get("model", "gpt-3.5-turbo"),
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response_content,
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
        },
    }

    return jsonify(response_body)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8888, debug=True)
