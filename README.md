# LLM Proxy with API Key Rotation and Web UI

This FastAPI-based proxy server routes chat requests to multiple LLM providers such as OpenAI, Anthropic, Gemini, Deepseek, Grok, and others. It automatically rotates API keys, which are managed through environment variables (with support for .env files) and can be viewed or edited in real time via the web UI.

This solution is especially beneficial if you manage several free-tier LLM API keys, as it eliminates the need for manual changes to API keys or model selections.

## Features

- **Multiple Providers:** Supports popular providers including OpenAI, Anthropic, Gemini, Deepseek, and Grok.
- **Automatic API Key Rotation:** Seamlessly rotates API keys without manual intervention.
- **Cross-Model Requests:** Specify multiple models in a single request (e.g., `"model": "gpt-4o,claude-3-7-sonnet-latest"`) and have the proxy automatically select the appropriate model along with its API key.
- **Web-Based API Key Management:** Easily add, update, or delete API keys through an intuitive browser interface (changes are temporary and maintained in memory).
- **Environment-Based Configuration:** Configure API keys via the `LLM_KEYS` environment variable, with support for .env files.
- **Lightweight & High Performance:** Built with FastAPI for efficiency and straightforward integration.

## Setup

### 1. Install Dependencies

Run the following command to install the necessary packages:

```bash
pip install -r requirements.txt
```

### 2. Start the Proxy Server

Launch the FastAPI server using Uvicorn:

```bash
uvicorn main:app --host 0.0.0.0 --port 7788
```

### 3. Use the Web UI for API Key Management

Open your browser and navigate to `http://0.0.0.0:7788`. Through the web interface you can:
- View all currently configured API keys.
- Add new API keys for any supported provider/model.
- Update or delete existing API keys.
- Save API keys to a `.env` file (note: changes made via the UI are temporary).

## Making Requests

Before sending any requests, ensure that the necessary API keys and models have been added.

Once the server is running, your client (e.g., Cursor, Cline, or SillyTarven) can forward chat completion requests to the proxy endpoint. For example, using `curl` to query models like gpt-4o or claude-3-7-sonnet-latest:

```bash
curl localhost:7788/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer DUMMY_API_KEY" \
  -d '{
    "model": "gpt-4o,claude-3-7-sonnet-latest",
    "messages": [
      {
        "role": "assistant",
        "content": "You are a helpful assistant."
      },
      {
        "role": "user",
        "content": "Hello!"
      }
    ]
  }'
```

The proxy will:
- Parse the incoming JSON request.
- Automatically select the appropriate model and corresponding API key.
- Forward the request to the respective LLM provider (e.g., OpenAI, Anthropic, Gemini, Deepseek, or Grok).
- Return the response from the provider.

## API Endpoints for Key Management

- `GET /api/keys` — Retrieve all API keys.
- `POST /api/keys` — Add a new API key (JSON format: `{provider, model, api_key}`).
- `DELETE /api/keys` — Remove an API key (JSON format: `{provider, model}`).

These endpoints are primarily used by the frontend UI but can also be accessed directly.
