import httpx

class ProviderClient:
    async def send_chat_completion(self, api_key, model, body, original_headers):
        raise NotImplementedError

class OpenAIClient(ProviderClient):
    async def send_chat_completion(self, api_key, model, body, original_headers):
        url = "https://api.openai.com/v1/chat/completions"
        payload = {"model": model, "messages": body.get("messages", [])}
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            resp = await client.post(url, headers=headers, json=payload)
        return resp.json()

class AnthropicClient(ProviderClient):
    async def send_chat_completion(self, api_key, model, body, original_headers):
        url = "https://api.anthropic.com/v1/messages"
        payload = {
            "model": model,
            "messages": body.get('messages'),
            "max_tokens": body.get('max_tokens', 64000)
        }
        async with httpx.AsyncClient() as client:
            headers = {
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json"
            }
            resp = await client.post(url, headers=headers, json=payload)
        return resp.json()

class GeminiClient(ProviderClient):
    async def send_chat_completion(self, api_key, model, body, original_headers):
        # Google Gemini API (assumed endpoint and format)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateMessage"
        messages = body.get('messages')
        payload = {
            "contents": [
                {"role": m.get("role", "user"), "parts": [{"text": m.get("content", "")}]} for m in messages
            ]
        }
        async with httpx.AsyncClient() as client:
            headers = {}
            headers.update(original_headers)
            headers.pop("Content-Length", None)
            headers.pop("content-length", None)
            headers.pop("host")
            # Replace dummy key with actual API key
            headers.pop("authorization", None)
            headers["Authorization"] = f"Bearer {api_key}"
            resp = await client.post(url, headers=headers, json=payload)
        return resp.json()

class DeepseekClient(ProviderClient):
    async def send_chat_completion(self, api_key, model, body, original_headers):
        # Deepseek API (assumed endpoint and format)
        url = "https://api.deepseek.com/v1/chat/completions"
        payload = {"model": model, "messages": body.get('messages')}
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            resp = await client.post(url, headers=headers, json=payload)
        return resp.json()

class GrokClient(ProviderClient):
    async def send_chat_completion(self, api_key, model, body, original_headers):
        # Grok API (assumed endpoint and format)
        url = "https://api.grok.com/v1/chat/completions"
        payload = {"model": model, "messages": body.get('messages')}
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            resp = await client.post(url, headers=headers, json=payload)
        return resp.json()

PROVIDER_CLIENTS = {
    "openai": OpenAIClient(),
    "anthropic": AnthropicClient(),
    "google": GeminiClient(),
    "deepseek": DeepseekClient(),
    "grok": GrokClient(),
}
