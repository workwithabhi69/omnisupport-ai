"""
Dual LLM Client: Supports Local Ollama and Hugging Face Serverless Inference.
100% open-source, zero paid APIs required.
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
        timeout: int = 40
    ):
        self.base_url = (base_url or os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")).rstrip("/")
        self.model_name = model_name or os.getenv("OLLAMA_MODEL", "qwen2.5:0.5b")
        self.hf_model = os.getenv("HF_MODEL", "Qwen/Qwen2.5-1.5B-Instruct")
        self.timeout = timeout

    def _get_hf_token(self) -> Optional[str]:
        """Retrieves HuggingFace token from Streamlit secrets or environment."""
        try:
            import streamlit as st
            if hasattr(st, "secrets") and "HF_TOKEN" in st.secrets:
                return st.secrets["HF_TOKEN"]
        except Exception:
            pass
        return os.getenv("HF_TOKEN")

    def check_connection(self) -> Dict[str, Any]:
        """Checks if local Ollama or Hugging Face cloud inference is available."""
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=1.5)
            if resp.status_code == 200:
                models_data = resp.json().get("models", [])
                model_names = [m.get("name", "") for m in models_data]
                return {
                    "connected": True,
                    "provider": "ollama",
                    "available_models": model_names,
                    "model_available": True,
                    "model_name": f"Ollama ({self.model_name})",
                    "message": "Local Ollama is online."
                }
        except Exception:
            pass

        hf_token = self._get_hf_token()
        if hf_token:
            return {
                "connected": True,
                "provider": "huggingface",
                "available_models": [self.hf_model],
                "model_available": True,
                "model_name": "Qwen2.5 LLM",
                "message": "Cloud Qwen2.5 LLM is live via HuggingFace Serverless Inference."
            }

        return {
            "connected": False,
            "provider": "none",
            "available_models": [],
            "model_available": False,
            "model_name": self.model_name,
            "message": "Using Grounded Policy Engine."
        }

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2
    ) -> Dict[str, Any]:
        conn = self.check_connection()
        if not conn.get("connected"):
            return {"success": False, "text": "", "error": "No LLM provider available"}

        if conn.get("provider") == "ollama":
            return self._generate_ollama(prompt, system_prompt, temperature)

        if conn.get("provider") == "huggingface":
            return self._generate_huggingface(prompt, system_prompt, temperature)

        return {"success": False, "text": "", "error": "Unknown provider"}

    def _generate_ollama(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2
    ) -> Dict[str, Any]:
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
            resp = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=self.timeout)
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "success": True,
                    "text": data.get("response", "").strip(),
                    "total_duration": data.get("total_duration", 0),
                    "eval_count": data.get("eval_count", 0)
                }
            return {"success": False, "text": "", "error": resp.text}
        except Exception as e:
            return {"success": False, "text": "", "error": str(e)}

    def _generate_huggingface(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2
    ) -> Dict[str, Any]:
        hf_token = self._get_hf_token()
        if not hf_token:
            return {"success": False, "text": "", "error": "No HF_TOKEN found"}

        headers = {
            "Authorization": f"Bearer {hf_token}",
            "Content-Type": "application/json"
        }

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.hf_model,
            "messages": messages,
            "max_tokens": 200,
            "temperature": temperature
        }

        urls = [
            f"https://router.huggingface.co/hf-inference/models/{self.hf_model}/v1/chat/completions",
            f"https://api-inference.huggingface.co/models/{self.hf_model}/v1/chat/completions"
        ]

        for url in urls:
            try:
                resp = requests.post(url, headers=headers, json=payload, timeout=self.timeout)
                if resp.status_code == 200:
                    data = resp.json()
                    choices = data.get("choices", [])
                    if choices:
                        content = choices[0].get("message", {}).get("content", "").strip()
                        if content:
                            return {"success": True, "text": content}
            except Exception:
                continue

        try:
            raw_url = f"https://api-inference.huggingface.co/models/{self.hf_model}"
            full_text = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            raw_payload = {
                "inputs": full_text,
                "parameters": {"max_new_tokens": 150, "temperature": temperature, "return_full_text": False}
            }
            resp = requests.post(raw_url, headers=headers, json=raw_payload, timeout=self.timeout)
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, list) and len(data) > 0:
                    generated = data[0].get("generated_text", "").strip()
                    if generated:
                        return {"success": True, "text": generated}
        except Exception as e:
            return {"success": False, "text": "", "error": str(e)}

        return {"success": False, "text": "", "error": "Hugging Face Inference call failed"}
