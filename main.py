from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import json
import os
from provider_client import PROVIDER_CLIENTS
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

app = FastAPI()

# Serve static files from the 'frontend' directory at '/frontend'
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

# Allow CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------
# 1) Load KEY LIST from ENV VARIABLE or file
# ---------------------------------------
import threading

KEY_LIST_LOCK = threading.Lock()

def load_key_list():
    """
    Load key list from the LLM_KEYS environment variable.
    LLM_KEYS should be a JSON array of objects, e.g.:
    [
      {"provider": "openai", "model": "gpt-3.5-turbo", "api_key": "sk-..."},
      {"provider": "anthropic", "model": "claude-3-opus-20240229", "api_key": "sk-ant-..."}
    ]
    """
    env_json = os.getenv("LLM_KEYS")
    if env_json:
        try:
            key_list = json.loads(env_json)
        except Exception as e:
            raise RuntimeError(f"Failed to parse LLM_KEYS: {e}")
        assert isinstance(key_list, list) and all(isinstance(k, dict) for k in key_list)
        return key_list
    return []

KEY_LIST = load_key_list()

# Round-robin counters by model
round_robin_counters = {}

def get_next_key_for_model(requested_model: str):
    with KEY_LIST_LOCK:
        matches = [k for k in KEY_LIST if k["model"] == requested_model]
        if not matches:
            return None

        if requested_model not in round_robin_counters:
            round_robin_counters[requested_model] = 0

        idx = round_robin_counters[requested_model]
        selected = matches[idx % len(matches)]
        round_robin_counters[requested_model] += 1
        return selected


@app.get("/api/keys")
async def get_keys():
    with KEY_LIST_LOCK:
        return JSONResponse(content=KEY_LIST)

@app.post("/api/keys")
async def add_key(request: Request):
    """
    Add a key to the in-memory key list (not persisted).
    To persist keys, update the LLM_KEYS environment variable or .env file manually.
    """
    data = await request.json()
    required_fields = {"provider", "model", "api_key"}
    if not required_fields.issubset(data):
        return JSONResponse(content={"error": "Missing required fields"}, status_code=400)
    with KEY_LIST_LOCK:
        KEY_LIST.append({
            "provider": data["provider"],
            "model": data["model"],
            "api_key": data["api_key"]
        })
    return JSONResponse(content={"success": True})

@app.delete("/api/keys")
async def delete_key(request: Request):
    """
    Delete a key from the in-memory key list (not persisted).
    To persist keys, update the LLM_KEYS environment variable or .env file manually.
    """
    data = await request.json()
    required_fields = {"provider", "model"}
    if not required_fields.issubset(data):
        return JSONResponse(content={"error": "Missing required fields"}, status_code=400)
    with KEY_LIST_LOCK:
        idx = next((i for i, k in enumerate(KEY_LIST) if k["provider"] == data["provider"] and k["model"] == data["model"]), None)
        if idx is not None:
            KEY_LIST.pop(idx)
            return JSONResponse(content={"success": True})
    return JSONResponse(content={"error": "Key not found"}, status_code=404)

@app.post("/chat/completions")
async def chat_completions(request: Request):
    body = await request.json()
    requested_model = body.get("model")
    if not requested_model:
        return {"error": "Missing 'model' in request"}

    selected = get_next_key_for_model(requested_model)
    if not selected:
        return {"error": f"No available key for model '{requested_model}'"}

    provider = selected["provider"]
    api_key = selected["api_key"]
    messages = body.get("messages", [])

    client = PROVIDER_CLIENTS.get(provider)
    if not client:
        return {"error": f"Provider '{provider}' not implemented"}

    return await client.send_chat_completion(api_key, requested_model, messages)

# Redirect root URL to /frontend/index.html
@app.get("/")
async def root():
    return RedirectResponse(url="/frontend/index.html")
