# LLM Proxy with API Key Rotation (Round-Robin)

A simple FastAPI-based proxy server that forwards chat requests to OpenAI, Anthropic, or other LLM providers. It automatically rotates API keys using a round-robin strategy. All keys and model mappings are stored securely in a single environment variable.

## Features

- **Multiple Providers:** Supports OpenAI, Anthropic, and can be extended to other providers.
- **Round-Robin Rotation:** Automatically rotates API keys for each model using a round-robin strategy.
- **Environment-Based Configuration:** No secrets are stored in code; the API key configuration is supplied via an environment variable.
- **Lightweight Proxy:** Built with FastAPI for high performance and easy integration.

## Requirements

- Python 3.8+
- Dependencies specified in `requirements.txt` (e.g., FastAPI, Uvicorn, httpx)

## Setup

### 1. Set Up the Environment Variable

Define the API keys and their metadata in a JSON array and store it in the `LLM_KEYS` environment variable.

#### Example for Linux/macOS

```bash
export LLM_KEYS='[
  { "api_key": "OPENAI_KEY_1", "model": "gpt-4o", "provider": "openai" },
  { "api_key": "OPENAI_KEY_2", "model": "gpt-4o", "provider": "openai" },
  { "api_key": "ANTHROPIC_1",  "model": "claude-3-7-sonnet", "provider": "anthropic" }
]'
```

#### Example for Windows (CMD)

```cmd
set LLM_KEYS=[{"api_key": "OPENAI_KEY_1", "model": "gpt-4o", "provider": "openai"}]
```

### 2. Install Dependencies

Create a `requirements.txt` file with the following (or adjust versions as needed):

```
fastapi==0.95.0
uvicorn==0.22.0
httpx==0.24.0
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
- Forward the request to the appropriate LLM provider.
- Return the response from the provider.