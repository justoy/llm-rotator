import asyncio
from litellm import completion

from key_manager import LLMKey

class LlmClient():
    async def send_chat_completion(self, selected: LLMKey, body):
        model = f"{selected.provider}/{selected.model}"
        return await asyncio.to_thread(completion, api_key = selected.api_key, model=model, messages=body.get("messages", []))
