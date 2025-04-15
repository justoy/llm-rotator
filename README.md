# LLM Proxy with API Key Rotation (Round-Robin) and Web UI

A FastAPI-based proxy server that forwards chat requests to OpenAI, Anthropic, Gemini, Deepseek, Grok, or other LLM providers. It automatically rotates API keys using a round-robin strategy. API keys are managed via environment variable (with .env file support) and can be viewed/edited in-memory via the web UI.

## Features

- **Multiple Providers:** Supports OpenAI, Anthropic, Gemini, Deepseek, and Grok out of the box.
- **Round-Robin Rotation:** Automatically rotates API keys for each model using a round-robin strategy.
- **Web UI for API Key Management:** Add, update, and delete API keys using a browser-based interface (changes are in-memory only).
- **Environment-Based Configuration:** API keys are supplied via the `LLM_KEYS` environment variable, which can be set in a `.env` file.
- **Lightweight Proxy:** Built with FastAPI for high performance and easy integration.

## Requirements

- Python 3.8+
- Dependencies specified in `requirements.txt` (e.g., FastAPI, Uvicorn, httpx, python-dotenv)
- A modern web browser (for the frontend UI)

## Setup

### 1. API Key Management

#### Environment Variable or .env File (Required)

Define the API keys and their metadata in a JSON array and store it in the `LLM_KEYS` environment variable. You can set this variable directly in your shell, or by creating a `.env` file in your project directory. The server will automatically load environment variables from `.env` using [python-dotenv](https://pypi.org/project/python-dotenv/).

##### Example `.env` file

```
LLM_KEYS=[
  { "api_key": "OPENAI_KEY_1", "model": "gpt-4o", "provider": "openai" },
  { "api_key": "GEMINI_KEY", "model": "gemini-pro", "provider": "gemini" },
  { "api_key": "DEEPSEEK_KEY", "model": "deepseek-chat", "provider": "deepseek" },
  { "api_key": "GROK_KEY", "model": "grok-1", "provider": "grok" },
  { "api_key": "ANTHROPIC_1",  "model": "claude-3-7-sonnet", "provider": "anthropic" }
]
```

##### Example for Linux/macOS

```bash
export LLM_KEYS='[
  { "api_key": "OPENAI_KEY_1", "model": "gpt-4o", "provider": "openai" },
  { "api_key": "GEMINI_KEY", "model": "gemini-pro", "provider": "gemini" }
]'
```

##### Example for Windows (CMD)

```cmd
set LLM_KEYS=[{"api_key": "OPENAI_KEY_1", "model": "gpt-4o", "provider": "openai"}]
```

**Note:** The value of `LLM_KEYS` must be a valid JSON array of objects, each with `provider`, `model`, and `api_key` fields.

#### Web UI (In-Memory Only)

- You can use the Web UI to add, update, or delete API keys for any supported provider and model.
- **Changes made via the Web UI or API are only stored in memory and will be lost when the server restarts.**
- To persist changes, update the `LLM_KEYS` environment variable or your `.env` file and restart the server.

### 2. Install Dependencies

Create a `requirements.txt` file with the following (or adjust versions as needed):

```
fastapi==0.95.0
uvicorn==0.22.0
httpx==0.24.0
python-dotenv==1.0.1
```

Install them using:

```bash
pip install -r requirements.txt
```

### 3. Running the Proxy

Start the FastAPI server using Uvicorn:

```bash
uvicorn main:app --host 0.0.0.0 --port 7788
```

### 4. Using the Web UI

Open `frontend/index.html` in your browser. You can now:
- View all API keys currently configured on the backend
- Add new API keys for any supported provider/model
- Update or delete existing API keys

**All changes made via the Web UI are in-memory only. To persist changes, update your environment variable or .env file.**

## Making Requests

Once the server is running, you can forward chat completions requests to your proxy endpoint. For example, using `curl`:

```bash
curl http://localhost:7788/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o",
    "messages": [
      { "role": "system", "content": "You are a helpful assistant." },
      { "role": "user", "content": "Hello!" }
    ]
  }'
```

The proxy will:
- Parse the incoming JSON.
- Look up the API key corresponding to the model using a round-robin mechanism.
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

## Notes

- The `LLM_KEYS` environment variable (or .env file) is the only source of truth for API keys. There is no persistent file storage.
- For production, secure your API endpoints and restrict CORS as needed.
