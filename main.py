from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from provider_client import PROVIDER_CLIENTS
from key_manager import KeyManager

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

@app.get("/api/keys")
async def get_keys():
    return JSONResponse(content=key_manager.get_keys())

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
    key_manager.add_key(data["provider"], data["model"], data["api_key"])
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

    selected = key_manager.get_next_key_for_model(requested_model)
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
