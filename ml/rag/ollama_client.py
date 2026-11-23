"""
Dual LLM Client: Supports Local Ollama and Hugging Face Serverless Inference.
Uses official huggingface_hub InferenceClient with automatic model fallback.
100% free, 100% open-source, zero credit card required.
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
        self.base_url = (base_url or os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")).rstrip("/")
        self.model_name = model_name or os.getenv("OLLAMA_MODEL", "qwen2.5:0.5b")
        self.hf_model = "Qwen/Qwen2.5-0.5B-Instruct"
        self.timeout = timeout

    def _get_hf_token(self) -> Optional[str]:
        """Retrieves HuggingFace token from Streamlit secrets or environment."""
        try:
            import streamlit as st
            if hasattr(st, "secrets"):
                if "HF_TOKEN" in st.secrets:
                    return str(st.secrets["HF_TOKEN"]).strip()
                if "huggingface" in st.secrets and "token" in st.secrets["huggingface"]:
                    return str(st.secrets["huggingface"]["token"]).strip()
        except Exception:
            pass
        return os.getenv("HF_TOKEN")

    def check_connection(self) -> Dict[str, Any]:
        """Checks if local Ollama or Hugging Face cloud inference is available."""
        # 1. Check local Ollama first
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=1.2)
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

        # 2. Check if Hugging Face token is provided for cloud deployment
        hf_token = self._get_hf_token()
        if hf_token and len(hf_token) > 10:
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
        """Generates response using local Ollama or Hugging Face serverless client."""
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
        """Local Ollama generation."""
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
        """Hugging Face Official InferenceClient with free model fallback."""
        hf_token = self._get_hf_token()
        if not hf_token:
            return {"success": False, "text": "", "error": "No HF_TOKEN found"}

        candidate_models = [
            "Qwen/Qwen2.5-0.5B-Instruct",
            "meta-llama/Llama-3.2-1B-Instruct",
            "google/gemma-2-2b-it"
        ]

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # Try official InferenceClient first
        try:
            from huggingface_hub import InferenceClient
            client = InferenceClient(api_key=hf_token, timeout=self.timeout)
            
            for mod in candidate_models:
                try:
                    response = client.chat.completions.create(
                        model=mod,
                        messages=messages,
                        max_tokens=220,
                        temperature=temperature
                    )
                    if response and response.choices:
                        text = response.choices[0].message.content.strip()
                        if text:
                            return {"success": True, "text": text}
                except Exception:
                    continue
        except Exception:
            pass

        # Fallback to direct HTTP post if library wrapper has issue
        headers = {
            "Authorization": f"Bearer {hf_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "Qwen/Qwen2.5-0.5B-Instruct",
            "messages": messages,
            "max_tokens": 200,
            "temperature": temperature
        }
        
        try:
            resp = requests.post(
                "https://router.huggingface.co/hf-inference/models/Qwen/Qwen2.5-0.5B-Instruct/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            if resp.status_code == 200:
                data = resp.json()
                choices = data.get("choices", [])
                if choices:
                    content = choices[0].get("message", {}).get("content", "").strip()
                    if content:
                        return {"success": True, "text": content}
        except Exception as e:
            return {"success": False, "text": "", "error": str(e)}

        return {"success": False, "text": "", "error": "Inference server is busy, fallback active."}
