import os
import json
import pathlib
from dotenv import load_dotenv

class KeyManager:
    def __init__(self):
        load_dotenv()
        self.key_list = self._load_key_list()
        self.round_robin_counters = {}

    def _load_key_list(self):
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

    def get_keys(self):
        return list(self.key_list)

    def add_key(self, provider, model, api_key):
        self.key_list.append({
            "provider": provider,
            "model": model,
            "api_key": api_key
        })

    def delete_key(self, provider, model):
        idx = next((i for i, k in enumerate(self.key_list) if k["provider"] == provider and k["model"] == model), None)
        if idx is not None:
            self.key_list.pop(idx)
            return True
        return False

    def save_keys_to_env_file(self):
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
        llm_keys_json = json.dumps(self.key_list, separators=(",", ":"))
        env_lines.append(f'LLM_KEYS={llm_keys_json}\n')
        # Write back to .env
        with env_path.open("w") as f:
            f.writelines(env_lines)

    def get_next_key_for_model(self, requested_model):
        matches = [k for k in self.key_list if k["model"] == requested_model]
        if not matches:
            return None

        if requested_model not in self.round_robin_counters:
            self.round_robin_counters[requested_model] = 0

        idx = self.round_robin_counters[requested_model]
        selected = matches[idx % len(matches)]
        self.round_robin_counters[requested_model] += 1
        return selected
