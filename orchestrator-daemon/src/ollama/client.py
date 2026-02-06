import requests
import dataclasses
from typing import List

OLLAMA_HOST = "http://127.0.0.1:11434"

@dataclasses.dataclass
class OllamaModel:
    name: str
    size_gb: float

def is_ollama_running() -> bool:
    try:
        resp = requests.get(f"{OLLAMA_HOST}/", timeout=1.0)
        return resp.status_code == 200
    except:
        return False

def list_models() -> List[OllamaModel]:
    try:
        resp = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=2.0)
        if resp.status_code != 200:
            return []
        data = resp.json()
        models = []
        for m in data.get("models", []):
            size_bytes = m.get("size", 0)
            models.append(OllamaModel(
                name=m.get("name", "unknown"),
                size_gb=round(size_bytes / (1024**3), 2)
            ))
        return models
    except:
        return []

def pull_model_hook(model_name: str) -> bool:
    # Trigger pull (non-blocking hook for now, just checks if reachable)
    # Real implementation would spawn a background task
    return is_ollama_running()

def generate_completion(model: str, prompt: str, system: str = "") -> str:
    """
    Generates a completion from Ollama.
    """
    try:
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        if system:
            payload["system"] = system
            
        resp = requests.post(f"{OLLAMA_HOST}/api/generate", json=payload, timeout=60.0)
        resp.raise_for_status()
        return resp.json().get("response", "")
    except Exception as e:
        print(f"Ollama generation failed: {e}")
        return f"Error responding to prompt: {e}"
