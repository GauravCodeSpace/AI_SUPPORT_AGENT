"""
Application Configuration Module.

Manages configuration settings for the PyQt5 Customer Support desktop client,
including n8n webhook URLs, Ollama server URL, request timeouts, and storage paths.
Settings are loaded from and saved to a local config.json file.
"""

import os
import json
from pathlib import Path
from dataclasses import dataclass, asdict

# Base application directory
BASE_DIR = Path(__file__).resolve().parent
CONFIG_FILE = BASE_DIR / "config.json"
DATA_DIR = BASE_DIR / "data"
CHAT_HISTORY_FILE = DATA_DIR / "chat_history.json"

# Inspected default values from the local n8n workflow "Customer Support Agent"
DEFAULT_WEBHOOK_ID = "bd156e94-be53-47cf-85c4-0b3999089d3c"
DEFAULT_N8N_BASE_URL = "http://localhost:5678"
DEFAULT_PRODUCTION_URL = f"{DEFAULT_N8N_BASE_URL}/webhook/{DEFAULT_WEBHOOK_ID}/chat"
DEFAULT_TEST_URL = f"{DEFAULT_N8N_BASE_URL}/webhook-test/{DEFAULT_WEBHOOK_ID}/chat"
DEFAULT_OLLAMA_URL = "http://127.0.0.1:11434"
DEFAULT_MODEL_NAME = "gemma4:26b"


@dataclass
class AppConfig:
    n8n_webhook_url: str = DEFAULT_PRODUCTION_URL
    n8n_test_webhook_url: str = DEFAULT_TEST_URL
    use_test_endpoint: bool = False
    n8n_base_url: str = DEFAULT_N8N_BASE_URL
    ollama_base_url: str = DEFAULT_OLLAMA_URL
    ollama_model: str = DEFAULT_MODEL_NAME
    request_timeout: int = 120  # seconds (Ollama 26B model may take time on local GPU/CPU)
    theme: str = "dark"
    auto_check_health: bool = True
    health_check_interval_seconds: int = 15

    def get_effective_webhook_url(self) -> str:
        """Return the active webhook endpoint URL based on mode."""
        if self.use_test_endpoint and self.n8n_test_webhook_url:
            return self.n8n_test_webhook_url.strip()
        return self.n8n_webhook_url.strip()

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "AppConfig":
        valid_keys = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered)


def load_config() -> AppConfig:
    """Load configuration from config.json or environment variables."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    config = AppConfig()

    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                config = AppConfig.from_dict(data)
        except Exception as e:
            print(f"Warning: Failed to load {CONFIG_FILE}: {e}. Using defaults.")

    # Environment variable overrides (if set)
    env_webhook = os.getenv("N8N_WEBHOOK_URL")
    if env_webhook:
        config.n8n_webhook_url = env_webhook

    env_ollama = os.getenv("OLLAMA_BASE_URL")
    if env_ollama:
        config.ollama_base_url = env_ollama

    env_timeout = os.getenv("N8N_REQUEST_TIMEOUT")
    if env_timeout:
        try:
            config.request_timeout = int(env_timeout)
        except ValueError:
            pass

    return config


def save_config(config: AppConfig) -> bool:
    """Persist configuration to config.json."""
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config.to_dict(), f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving configuration: {e}")
        return False
