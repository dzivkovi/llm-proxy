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

## Development

### Project Structure

```text
llm-proxy/
├── app/
│   ├── __init__.py
│   └── mock_server.py
├── tests/
│   └── test_mock_server.py
├── requirements.txt
└── README.md
```

### Token Counting

The server approximates tokens using a simple character-based approach (1 token ≈ 4 characters). While this is not as accurate as OpenAI's tokenizer, it's sufficient for testing purposes.
