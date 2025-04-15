import os
import json
import pathlib
from dotenv import load_dotenv
from dataclasses import dataclass, asdict
from typing import List, Optional, Any

@dataclass
class LLMKey:
    provider: str
    model: str
    api_key: str

class KeyManager:
    def __init__(self):
        load_dotenv()
        self.key_list: List[LLMKey] = self._load_key_list()

    def _load_key_list(self) -> List[LLMKey]:
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
            return [LLMKey(**k) for k in key_list]
        return []

    def get_keys(self) -> List[LLMKey]:
        return list(self.key_list)

    def add_key(self, provider: str, model: str, api_key: str) -> None:
        self.key_list.append(LLMKey(provider=provider, model=model, api_key=api_key))

    def delete_key(self, provider: str, model: str) -> bool:
        idx = next((i for i, k in enumerate(self.key_list) if k.provider == provider and k.model == model), None)
        if idx is not None:
            self.key_list.pop(idx)
            return True
        return False

    def save_keys_to_env_file(self) -> None:
        """
        Save the current key_list to the .env file as the LLM_KEYS variable.
        """
        env_path = pathlib.Path(".env")
        # Read existing .env content if present
        env_lines = []
        if env_path.exists():
            with env_path.open("r") as f:
                env_lines = f.readlines()
        # Remove any existing LLM_KEYS line
        env_lines = [line for line in env_lines if not line.strip().startswith("LLM_KEYS=")]
        # Add the new LLM_KEYS line
        llm_keys_json = json.dumps([asdict(k) for k in self.key_list], separators=(",", ":"))
        env_lines.append(f'LLM_KEYS={llm_keys_json}\n')
        # Write back to .env
        with env_path.open("w") as f:
            f.writelines(env_lines)
