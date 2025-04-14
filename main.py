from fastapi import FastAPI, Request
import json
import os
from provider_client import PROVIDER_CLIENTS

app = FastAPI()

# ---------------------------------------
# 1) Load KEY LIST from ENV VARIABLE
# ---------------------------------------
env_json = os.getenv("LLM_KEYS")
if not env_json:
    raise RuntimeError("Missing LLM_KEYS environment variable")

try:
    KEY_LIST = json.loads(env_json)
except Exception as e:
    raise RuntimeError(f"Failed to parse LLM_KEYS: {e}")

# Ensure it's a list of dicts
assert isinstance(KEY_LIST, list) and all(isinstance(k, dict) for k in KEY_LIST)

# Round-robin counters by model
round_robin_counters = {}

def get_next_key_for_model(requested_model: str):
    matches = [k for k in KEY_LIST if k["model"] == requested_model]
    if not matches:
        return None

    if requested_model not in round_robin_counters:
        round_robin_counters[requested_model] = 0

    idx = round_robin_counters[requested_model]
    selected = matches[idx % len(matches)]
    round_robin_counters[requested_model] += 1
    return selected


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
