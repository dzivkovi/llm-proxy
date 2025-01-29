#!/usr/bin/env python
from flask import Flask, request, jsonify
from typing import Dict, Any
from litellm import completion

app = Flask(__name__)


def convert_usage_to_dict(usage: Any) -> Dict[str, int]:
    """Convert usage object to a dictionary with integer values."""
    if hasattr(usage, "__dict__"):
        # If usage is an object with attributes, convert to dict
        return {
            "prompt_tokens": getattr(usage, "prompt_tokens", 0),
            "completion_tokens": getattr(usage, "completion_tokens", 0),
            "total_tokens": getattr(usage, "total_tokens", 0),
        }
    elif isinstance(usage, dict):
        # If usage is already a dict, return it
        return usage
    else:
        # Default values if usage is None or unexpected type
        return {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}


@app.route("/v1/chat/completions", methods=["POST"])
def chat_completions():
    data = request.get_json()
    messages = data.get("messages", [])
    model = data.get("model", "gpt-3.5-turbo")

    raw_response = completion(
        model=model,
        messages=messages,
        max_tokens=100,
        temperature=0.7,
    )

    # Extract assistant text from the litellm response
    assistant_content = raw_response["choices"][0]["message"]["content"].strip()

    # Convert usage object to dictionary
    usage_dict = convert_usage_to_dict(raw_response.get("usage"))

    # Construct OpenAI-compatible JSON response
    response_body = {
        "id": "chatcmpl-temp-id",
        "object": "chat.completion",
        "created": 1234567890,
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": assistant_content},
                "finish_reason": "stop",
            }
        ],
        "usage": usage_dict,
    }

    return jsonify(response_body)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
