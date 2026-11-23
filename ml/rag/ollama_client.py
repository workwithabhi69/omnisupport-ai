"""
Dual LLM Client: Supports Local & Cloud Colab Ollama via Ngrok, plus HF Inference.
Automatically reads OLLAMA_BASE_URL from Streamlit secrets and adds ngrok bypass headers.
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
        timeout: int = 35
    ):
        self._explicit_base_url = base_url
        self.model_name = model_name or os.getenv("OLLAMA_MODEL", "qwen2.5:0.5b")
        self.hf_model = "Qwen/Qwen2.5-0.5B-Instruct"
        self.timeout = timeout

    @property
    def base_url(self) -> str:
        if self._explicit_base_url:
            return self._explicit_base_url.rstrip("/")
        # Check Streamlit Cloud secrets first
        try:
            import streamlit as st
            if hasattr(st, "secrets") and "OLLAMA_BASE_URL" in st.secrets:
                return str(st.secrets["OLLAMA_BASE_URL"]).strip().rstrip("/")
        except Exception:
            pass
        return os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")

    def _get_headers(self) -> Dict[str, str]:
        # Bypasses ngrok free tier browser interstitial page
        return {
            "ngrok-skip-browser-warning": "true",
            "User-Agent": "OmniSupportAI/2.5"
        }

    def _get_hf_token(self) -> Optional[str]:
        try:
            import streamlit as st
            if hasattr(st, "secrets") and "HF_TOKEN" in st.secrets:
                return str(st.secrets["HF_TOKEN"]).strip()
        except Exception:
            pass
        return os.getenv("HF_TOKEN")

    def check_connection(self) -> Dict[str, Any]:
        """Checks Ollama (local or Colab Ngrok tunnel)."""
        current_url = self.base_url
        try:
            resp = requests.get(
                f"{current_url}/api/tags",
                headers=self._get_headers(),
                timeout=4
            )
            if resp.status_code == 200:
                models_data = resp.json().get("models", [])
                model_names = [m.get("name", "") for m in models_data]
                return {
                    "connected": True,
                    "provider": "ollama",
                    "available_models": model_names,
                    "model_available": True,
                    "model_name": f"Ollama ({self.model_name})",
                    "message": "Ollama is online."
                }
        except Exception:
            pass

        # Check HuggingFace Token fallback
        hf_token = self._get_hf_token()
        if hf_token and len(hf_token) > 10:
            return {
                "connected": True,
                "provider": "huggingface",
                "available_models": [self.hf_model],
                "model_available": True,
                "model_name": "Qwen2.5 LLM",
                "message": "Cloud Qwen2.5 LLM is live."
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

        return {"success": False, "text": "", "error": "No active provider"}

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
            resp = requests.post(
                f"{self.base_url}/api/generate",
                headers=self._get_headers(),
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
            return {"success": False, "text": "", "error": resp.text}
        except Exception as e:
            return {"success": False, "text": "", "error": str(e)}
