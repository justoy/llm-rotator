from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from provider_client import PROVIDER_CLIENTS
from key_manager import KeyManager, LLMKey
from api_key_selector import ApiKeySelector
from dataclasses import asdict
from typing import List

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
# Key management via KeyManager class
# ---------------------------------------
key_manager = KeyManager()
api_key_selector = ApiKeySelector()

@app.get("/api/keys")
async def get_keys():
    # Convert LLMKey objects to dicts for JSON serialization
    keys: List[LLMKey] = key_manager.get_keys()
    return JSONResponse(content=[asdict(k) for k in keys])

@app.post("/api/keys/save")
async def save_keys():
    """
    Save the current in-memory key list to the .env file (persist to disk).
    """
    try:
        key_manager.save_keys_to_env_file()
        return JSONResponse(content={"success": True})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

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
    # Ensure correct types and pass to add_key
    key_manager.add_key(
        provider=str(data["provider"]),
        model=str(data["model"]),
        api_key=str(data["api_key"])
    )
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
    success = key_manager.delete_key(data["provider"], data["model"])
    if success:
        return JSONResponse(content={"success": True})
    return JSONResponse(content={"error": "Key not found"}, status_code=404)

@app.post("/chat/completions")
async def chat_completions(request: Request):
    body = await request.json()
    requested_model = body.get("model")
    if not requested_model:
        return {"error": "Missing 'model' in request"}

    # Support multiple models separated by comma in the string
    model_candidates = [m.strip() for m in requested_model.split(",") if m.strip()]
    selected_model: LLMKey = api_key_selector.get_next_key_for_model(key_manager.get_keys(), model_candidates)

    if not selected_model:
        return {"error": f"No available key for any of the requested models: {model_candidates}"}

    client = PROVIDER_CLIENTS.get(selected_model.provider)
    if not client:
        return {"error": f"Provider '{selected_model.provider}' not implemented"}

    # Use the selected model for forwarding
    # Pass the model name string to the client
    # Pass original request headers to preserve them except for replacing dummy key

    return await client.send_chat_completion(selected_model.api_key, selected_model.model, body, dict(request.headers))

# Redirect root URL to /frontend/index.html
@app.get("/")
async def root():
    return RedirectResponse(url="/frontend/index.html")
