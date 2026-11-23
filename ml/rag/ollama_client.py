"""
Ollama Local LLM Client with Health Checking and Streaming Generation.
Handles connection checks, model availability, timeout management, and graceful error handling.
"""

import os
import requests
import json
from typing import Dict, Any, Generator, Optional, List


class OllamaClient:
    def __init__(
        self,
        base_url: Optional[str] = None,
        model_name: Optional[str] = None,
        timeout: int = 45
    ):
        self.base_url = (base_url or os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")).rstrip("/")
        self.model_name = model_name or os.getenv("OLLAMA_MODEL", "qwen2.5:0.5b")
        self.timeout = timeout

    def check_connection(self) -> Dict[str, Any]:
        """Checks if Ollama service is reachable and responsive."""
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=3)
            if resp.status_code == 200:
                models_data = resp.json().get("models", [])
                model_names = [m.get("name", "") for m in models_data]
                return {
                    "connected": True,
                    "available_models": model_names,
                    "model_available": any(self.model_name in m for m in model_names),
                    "message": "Ollama is online and connected."
                }
            return {
                "connected": False,
                "available_models": [],
                "model_available": False,
                "message": f"Ollama returned HTTP status {resp.status_code}"
            }
        except requests.exceptions.ConnectionError:
            return {
                "connected": False,
                "available_models": [],
                "model_available": False,
                "message": "Cannot connect to Ollama. Service is not running on 127.0.0.1:11434."
            }
        except Exception as e:
            return {
                "connected": False,
                "available_models": [],
                "model_available": False,
                "message": f"Ollama connection error: {str(e)}"
            }

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Sends generation request to Ollama /api/generate.
        """
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "top_p": 0.85,
                "repeat_penalty": 1.25,
                "repeat_last_n": 64,
                "num_predict": 200
            }
        }
        if system_prompt:
            payload["system"] = system_prompt

        try:
            resp = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout
            )
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "success": True,
                    "text": data.get("response", "").strip(),
                    "total_duration": data.get("total_duration", 0),
                    "eval_count": data.get("eval_count", 0)
                }
            return {
                "success": False,
                "text": "",
                "error": f"Ollama API error: HTTP {resp.status_code} - {resp.text}"
            }
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "text": "",
                "error": f"Generation timed out after {self.timeout}s on model '{self.model_name}'"
            }
        except Exception as e:
            return {
                "success": False,
                "text": "",
                "error": f"Error invoking Ollama: {str(e)}"
            }

    def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2
    ) -> Generator[str, None, None]:
        """
        Streams response tokens directly from Ollama.
        """
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": temperature,
                "top_p": 0.9,
                "num_predict": 512
            }
        }
        if system_prompt:
            payload["system"] = system_prompt

        resp = requests.post(
            f"{self.base_url}/api/generate",
            json=payload,
            stream=True,
            timeout=self.timeout
        )
        if resp.status_code != 200:
            yield f"Error from Ollama ({resp.status_code}): {resp.text}"
            return

        for line in resp.iter_lines():
            if line:
                chunk = json.loads(line.decode("utf-8"))
                token = chunk.get("response", "")
                yield token
