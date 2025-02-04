# LLM Proxy Server

A mock server that implements OpenAI's chat completions API for development and testing purposes. Particularly useful for testing OpenAI-compatible integrations like Continue.dev.

## Features

- OpenAI-compatible `/v1/chat/completions` endpoint
- Supports both streaming and non-streaming responses
- Real token counting based on message length
- Request logging for debugging
- Compatible with Continue.dev VSCode extension

## Setup

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Run the mock server:

   ```bash
   python -m app.mock_server
   ```

The server will start on `http://localhost:8888`.

## Usage

### Direct API Access

Test basic completion (non-streaming):

```bash
curl -X POST http://localhost:8888/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

Test streaming response:

```bash
curl -X POST http://localhost:8888/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Hello!"}],
    "stream": true
  }'
```

### Continue.dev Integration

1. Create/edit Continue.dev configuration file:

   ```json
   {
   "models": [
      {
         "title": "Local Mock GPT",
         "provider": "openai",
         "model": "gpt-3.5-turbo",
         "apiKey": "dummy-key",
         "apiBase": "http://localhost:8888/v1",
         "useLegacyCompletionsEndpoint": false
      }
   ]
   }
   ```

2. Place this configuration in:

   - Windows: `%APPDATA%\continue\config.json`
   - macOS/Linux: `~/.continue/config.json`

3. Restart VSCode

4. Select "Local Mock GPT" as your model in Continue.dev

## Response Format

Non-streaming response:

```json
{
  "id": "chatcmpl-abc123def456",
  "object": "chat.completion",
  "created": 1738125758,
  "model": "gpt-3.5-turbo",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Based on the context, I recommend this approach..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 12,
    "completion_tokens": 9,
    "total_tokens": 21
  }
}
```

Streaming response format:

```jsonl
data: {"id":"chatcmpl-abc123def456","object":"chat.completion.chunk","created":1738125758,"model":"gpt-3.5-turbo","choices":[{"index":0,"delta":{"role":"assistant"},"finish_reason":null}]}

data: {"id":"chatcmpl-abc123def456","object":"chat.completion.chunk","created":1738125758,"model":"gpt-3.5-turbo","choices":[{"index":0,"delta":{"content":"Based "},"finish_reason":null}]}

data: {"id":"chatcmpl-abc123def456","object":"chat.completion.chunk","created":1738125758,"model":"gpt-3.5-turbo","choices":[{"index":0,"delta":{"content":"on "},"finish_reason":null}]}

data: [DONE]
```

## Using the Adapter Server

The adapter server [adapter_server.py](app/adapter_server.py) acts as a bridge between Continue.dev and a running FastAPI API server that provides streaming responses. This allows you to test your Continue.dev integration with either a real API or a legacy API implementation.

### Configuration

1. Create a `.env` file (or update your existing one) based on [.env.sample](.env.sample) with the following parameter:

   ```bash
   STREAM_URL="http://127.0.0.1:8000/stream?topNDocuments=3&sessionID=12345"
   ```

   Ensure that the URL points to your running FastAPI API server. You can use:

   - A real API server, or
   - A legacy API server cloned from the mock-api repository, which simulates a streaming response for search queries.

### Legacy API (Mock API) Overview

The legacy API provides a simulated streaming response with the following key features:

- **Streaming Response:** Data is sent as a series of Server-Sent Events (SSE).
- **Response Format:** Each SSE line is in one of the formats:

  ```log
  data: {'type': 'response', 'data': 'word'}
  data: {'type': 'citation', 'data': 'citation_id'}
  ```

- **Parameters:**
  - `search_query`: The search query (URL-encoded).
  - `topNDocuments`: Number of citation documents to return.
  - `sessionID`: A unique identifier for the session.

#### Steps to Run the Legacy API

1. Clone the mock API repository.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Start the API server with Uvicorn:

   ```bash
   uvicorn main:app --reload
   ```

   The server will run at `http://127.0.0.1:8000`.

4. View the interactive API documentation at:

    - [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
    - [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### Running the Adapter Server

Once your FastAPI (or legacy) server is running and your `.env` file is correctly set up, start the adapter server:

```bash
python -m app.adapter_server
```

This server will:

- Fetch streaming responses from the API using the URL specified in `.env`.
- Convert these responses into OpenAI's chat completion chunk format.
- Format citations as a separate, bullet-listed block for clear presentation.

Your Continue.dev integration will then be able to consume these formatted responses as before.

## Development

### Project Structure

```text
llm-proxy/
├── app/
│   ├── __init__.py
│   └── mock_server.py
│   └── adapter_server.py
├── tests/
│   └── test_mock_server.py
├── requirements.txt
└── README.md
```

### Token Counting

The server approximates tokens using a simple character-based approach (1 token ≈ 4 characters). While this is not as accurate as OpenAI's tokenizer, it's sufficient for testing purposes.
