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

PROVIDER_CLIENTS = {
    "openai": OpenAIClient(),
    "anthropic": AnthropicClient(),
}
