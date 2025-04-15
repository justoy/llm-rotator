# LLM Proxy with API Key Rotation and Web UI

A FastAPI-based proxy server that forwards chat requests to OpenAI, Anthropic, Gemini, Deepseek, Grok, or other LLM providers. It automatically rotates API keys. API keys are managed via environment variable (with .env file support) and can be viewed/edited in-memory via the web UI.

This is useful when you have multiple LLM API keys with free tier. You don't need to manually change API key or model anymore.

## Features

- **Multiple Providers:** Supports OpenAI, Anthropic, Gemini, Deepseek, and Grok out of the box.
- **API Key Rotation:** Automatically rotates API keys.
- **Cross-Model Call:** You can specify multiple models in one request, e.g., `"model": "gpt-4o,claude-3-7-sonnet-latest"`,  and the proxy will auto select a model and its API key.
- **Web UI for API Key Management:** Add, update, and delete API keys using a browser-based interface (changes are in-memory only).
- **Environment-Based Configuration:** API keys are supplied via the `LLM_KEYS` environment variable, which can be set in a `.env` file.
- **Lightweight Proxy:** Built with FastAPI for high performance and easy integration.

## Requirements

- Python 3.8+
- Dependencies specified in `requirements.txt` (e.g., FastAPI, Uvicorn, httpx, python-dotenv)
- A modern web browser (for the frontend UI)

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Running the Proxy

Start the FastAPI server using Uvicorn:

```bash
uvicorn main:app --host 0.0.0.0 --port 7788
```

### 3. Using the Web UI to manage LLM Model API Keys

Open `http://0.0.0.0:7788` in your browser. You can now:
- View all API keys currently configured on the backend
- Add new API keys for any supported provider/model
- Update or delete existing API keys
- Save API keys to `.env` file

## Making Requests
Before making requests, please ensure you already added corresponding API keys and models.

Once the server is running, your client (e.g., Cursor, Cline, and SillyTarven) can forward chat completions requests to your proxy endpoint. For example, using `curl` to query gpt-4o or claude-3-7-sonnet-latest:

```bash
curl localhost:7788/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer DUMMY_API_KEY" \
  -d '{
    "model": "gpt-4o,claude-3-7-sonnet-latest",
    "messages": [
      {
        "role": "developer",
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
- Parse the incoming JSON.
- Pick up a model and Look up the API key corresponding to the model.
- Forward the request to the appropriate LLM provider (OpenAI, Anthropic, Gemini, Deepseek, or Grok).
- Return the response from the provider.

## API Endpoints for Key Management

- `GET /api/keys` — List all API keys
- `POST /api/keys` — Add a new API key (JSON: `{provider, model, api_key}`)
- `DELETE /api/keys` — Delete an API key (JSON: `{provider, model}`)

These endpoints are used by the frontend UI, but can also be called directly.

**Note:** Changes made via these endpoints are not persisted. To make changes permanent, update your environment variable or .env file.

## Supported Providers

- **OpenAI** (`provider: "openai"`)
- **Anthropic** (`provider: "anthropic"`)
- **Gemini** (`provider: "gemini"`)
- **Deepseek** (`provider: "deepseek"`)
- **Grok** (`provider: "grok"`)

You can extend support for additional providers by adding new client classes in `provider_client.py`.
