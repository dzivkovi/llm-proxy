#!/usr/bin/env python
import os
import json
import time
import random
import uuid
import urllib.parse
import requests

from flask import Flask, request, jsonify, Response
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# STREAM_URL already contains something like:
#   http://127.0.0.1:8000/stream?topNDocuments=3&sessionID=12345
# We’ll just append &search_query=... later.
STREAM_URL = os.getenv("STREAM_URL", "http://127.0.0.1:8000/stream?topNDocuments=3&sessionID=12345")


def generate_stream_response_from_remote(query: str):
    """
    1) Build the final URL by appending &search_query=...
    2) GET request to your FastAPI /stream endpoint.
    3) Stream each line (SSE).
    4) Convert to OpenAI chat completion chunk format.
    """

    # Encode the user’s prompt for safe URL usage
    query_encoded = urllib.parse.quote_plus(query)

    # Build the final URL, e.g.:
    #   http://127.0.0.1:8000/stream?topNDocuments=3&sessionID=12345&search_query=meaning%20of%20life
    final_url = f"{STREAM_URL}&search_query={query_encoded}"

    with requests.get(final_url, stream=True, timeout=10) as r:
        r.raise_for_status()

        for raw_line in r.iter_lines(decode_unicode=True):
            # SSE lines typically look like:  data: {...JSON...}
            if not raw_line or not raw_line.startswith("data: "):
                continue

            # Remove "data: " prefix
            line = raw_line[6:].strip()

            # If your FastAPI mock never sends "[DONE]", skip this check or adapt as needed
            if line == "[DONE]":
                yield "data: [DONE]\n\n"
                break

            # Parse the JSON from the FastAPI SSE response: {"type": "...", "data": "..."}
            try:
                parsed = json.loads(line)
            except json.JSONDecodeError:
                continue

            # Extract the chunk content (token, citation, etc.)
            content = parsed.get("data", "")

            # Build OpenAI-like chunk
            chunk = {
                "id": f"chatcmpl-{random.randint(1000, 9999)}",
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": "gpt-3.5-turbo",
                "choices": [
                    {
                        "index": 0,
                        "delta": {"content": content + " "},
                        "finish_reason": None
                    }
                ]
            }

            # Stream SSE chunk back
            yield f"data: {json.dumps(chunk)}\n\n"
            time.sleep(0.05)

    # After reading all lines or if remote closed, signal we're done
    yield "data: [DONE]\n\n"


@app.route("/v1/chat/completions", methods=["POST"])
def chat_completions():
    # Log for debugging
    data = request.get_json(silent=True) or {}
    print("\n=== Incoming Request ===")
    print(f"Headers: {dict(request.headers)}")
    print(f"Data: {data}")
    print("========================\n")

    # Check if streaming is requested
    is_streaming = data.get('stream', False)

    if is_streaming:
        # Typical OpenAI Chat spec: an array of "messages"
        # We'll extract the last user message as the prompt
        messages = data.get("messages", [])
        if messages:
            query = messages[-1].get("content", "Default text")
        else:
            query = "No messages found"

        return Response(
            generate_stream_response_from_remote(query),
            mimetype='text/event-stream'
        )

    # If not streaming, just return a static JSON response
    response_body = {
        "id": f"chatcmpl-{uuid.uuid4().hex[:12]}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": data.get("model", "gpt-3.5-turbo"),
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "Non-streaming mock response."
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 50, "completion_tokens": 30, "total_tokens": 80},
    }
    return jsonify(response_body)


if __name__ == "__main__":
    # Start the Flask adapter server
    app.run(host="0.0.0.0", port=8888, debug=True)
