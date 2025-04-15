import httpx

class ProviderClient:
    async def send_chat_completion(self, api_key, model, messages):
        raise NotImplementedError

class OpenAIClient(ProviderClient):
    async def send_chat_completion(self, api_key, model, messages):
        url = "https://api.openai.com/v1/chat/completions"
        payload = {"model": model, "messages": messages}
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            resp = await client.post(url, headers=headers, json=payload)
        return resp.json()

class AnthropicClient(ProviderClient):
    async def send_chat_completion(self, api_key, model, messages):
        url = "https://api.anthropic.com/v1/messages"
        payload = {
            "model": model,
            "messages": messages
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
    async def send_chat_completion(self, api_key, model, messages):
        # Google Gemini API (assumed endpoint and format)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateMessage"
        payload = {
            "contents": [
                {"role": m.get("role", "user"), "parts": [{"text": m.get("content", "")}]} for m in messages
            ]
        }
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            resp = await client.post(url, headers=headers, json=payload)
        return resp.json()

class DeepseekClient(ProviderClient):
    async def send_chat_completion(self, api_key, model, messages):
        # Deepseek API (assumed endpoint and format)
        url = "https://api.deepseek.com/v1/chat/completions"
        payload = {"model": model, "messages": messages}
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            resp = await client.post(url, headers=headers, json=payload)
        return resp.json()

class GrokClient(ProviderClient):
    async def send_chat_completion(self, api_key, model, messages):
        # Grok API (assumed endpoint and format)
        url = "https://api.grok.com/v1/chat/completions"
        payload = {"model": model, "messages": messages}
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
