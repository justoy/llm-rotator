import random
from typing import List, Optional
from key_manager import LLMKey

class ApiKeySelector:
    def __init__(self):
        pass

    def get_next_key_for_model(self, key_list: List[LLMKey], requested_models: List[str]) -> Optional[LLMKey]:
        # Find all keys matching the requested model
        matches = [k for k in key_list if k.model in requested_models]
        if not matches:
            return None

        # Pick a random key from matches
        return random.choice(matches)
