import httpx
import logging
import subprocess
import os

logger = logging.getLogger(__name__)

class OllamaManager:
    BASE_URL = "http://localhost:11434"

    @staticmethod
    async def check_installation():
        """Checks if Ollama is running by querying its version."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{OllamaManager.BASE_URL}/api/version")
                return response.status_code == 200
        except Exception:
            return False

    @staticmethod
    async def pull_model(model_name: str):
        """Triggers a model pull in Ollama."""
        logger.info(f"Pulling model: {model_name}")
        try:
            async with httpx.AsyncClient(timeout=None) as client:
                # Stream the pull progress
                async with client.stream("POST", f"{OllamaManager.BASE_URL}/api/pull", json={"name": model_name}) as response:
                    async for line in response.aiter_lines():
                        if line:
                            logger.debug(line)
            return True
        except Exception as e:
            logger.error(f"Failed to pull model {model_name}: {e}")
            return False

    @staticmethod
    async def start_model(model_name: str):
        """Ensures a model is loaded in memory."""
        # Ollama loads on first generate call. We send an empty prompt to warm up.
        try:
            async with httpx.AsyncClient() as client:
                await client.post(f"{OllamaManager.BASE_URL}/api/generate", json={
                    "model": model_name,
                    "prompt": "",
                    "keep_alive": -1 # Keep loaded indefinitely until told otherwise
                })
            return True
        except Exception as e:
            logger.error(f"Failed to start model {model_name}: {e}")
            return False

    @staticmethod
    async def stop_model(model_name: str):
        """Stops a model by setting keep_alive to 0."""
        try:
            async with httpx.AsyncClient() as client:
                await client.post(f"{OllamaManager.BASE_URL}/api/generate", json={
                    "model": model_name,
                    "prompt": "",
                    "keep_alive": 0
                })
            return True
        except Exception as e:
            logger.error(f"Failed to stop model {model_name}: {e}")
            return False
