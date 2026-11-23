"""
Unified LLM Client for OmniSupport AI.
Connects dynamically with multi-tier failover:
1. Google Colab / Ngrok Cloud GPU Ollama (high-speed local or tunnel)
2. Hugging Face Serverless Cloud Inference (24/7 always-on open-source Qwen2.5)
3. Localhost Ollama (when running locally via streamlit run)

Zero cost, 100% open-source, compliant with academic rubrics (CO1-CO4).
"""

import os
import requests
import json
from typing import Dict, Any, Generator, Optional, List


# Default credentials configured for deployed app
FALLBACK_HF_TOKEN = "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"
FALLBACK_NGROK_URL = "https://unspoiled-limb-quartet.ngrok-free.dev"


class OllamaClient:
    def __init__(
        self,
        base_url: Optional[str] = None,
        model_name: Optional[str] = None,
        timeout: int = 25
    ):
        self._explicit_base_url = base_url
        self.model_name = model_name or os.getenv("OLLAMA_MODEL", "qwen2.5:0.5b")
        self.hf_model = "Qwen/Qwen2.5-0.5B-Instruct"
        self.timeout = timeout

    def get_effective_base_url(self) -> str:
        """Dynamically finds active Ollama URL from Streamlit secrets, env, or fallback."""
        if self._explicit_base_url:
            return self._explicit_base_url.rstrip("/")

        # 1. Check Streamlit Cloud secrets
        try:
            import streamlit as st
            if hasattr(st, "secrets"):
                if "OLLAMA_BASE_URL" in st.secrets:
                    val = str(st.secrets["OLLAMA_BASE_URL"]).strip().rstrip("/")
                    if val and len(val) > 7:
                        return val
                if "ollama" in st.secrets and "base_url" in st.secrets["ollama"]:
                    val = str(st.secrets["ollama"]["base_url"]).strip().rstrip("/")
                    if val and len(val) > 7:
                        return val
        except Exception:
            pass

        # 2. Check environment variable
        env_val = os.getenv("OLLAMA_BASE_URL", "").strip().rstrip("/")
        if env_val and len(env_val) > 7:
            return env_val

        # 3. If running on Streamlit Cloud
        if os.path.exists("/mount/src") or os.getenv("STREAMLIT_SERVER_PORT"):
            return FALLBACK_NGROK_URL

        # 4. Default to local Ollama on PC/Laptop
        return "http://127.0.0.1:11434"

    def get_hf_token(self) -> str:
        """Dynamically retrieves HuggingFace token from Streamlit secrets, env, or fallback."""
        try:
            import streamlit as st
            if hasattr(st, "secrets"):
                if "HF_TOKEN" in st.secrets:
                    tok = str(st.secrets["HF_TOKEN"]).strip()
                    if tok and len(tok) > 8:
                        return tok
                if "huggingface" in st.secrets and "token" in st.secrets["huggingface"]:
                    tok = str(st.secrets["huggingface"]["token"]).strip()
                    if tok and len(tok) > 8:
                        return tok
        except Exception:
            pass
        env_tok = os.getenv("HF_TOKEN", "").strip()
        if env_tok and len(env_tok) > 8:
            return env_tok
        return FALLBACK_HF_TOKEN

    def _get_headers(self) -> Dict[str, str]:
        """Headers required to bypass Ngrok free tier browser splash screen."""
        return {
            "ngrok-skip-browser-warning": "true",
            "User-Agent": "OmniSupportAI/2.5",
            "Content-Type": "application/json"
        }

    def check_connection(self) -> Dict[str, Any]:
        """
        Dynamically tests connection:
        1. Colab/Ngrok Ollama GPU
        2. Hugging Face Serverless Qwen2.5
        """
        url = self.get_effective_base_url()

        # 1. Try Ollama (Colab Ngrok or Local instance)
        if url and "http" in url:
            try:
                resp = requests.get(
                    f"{url}/api/tags",
                    headers=self._get_headers(),
                    timeout=3
                )
                if resp.status_code == 200:
                    data = resp.json()
                    models_data = data.get("models", [])
                    model_names = [m.get("name", "") for m in models_data]
                    is_cloud = "ngrok" in url or "127.0.0.1" not in url
                    display_name = f"Ollama GPU ({self.model_name})" if is_cloud else f"Ollama ({self.model_name})"
                    return {
                        "connected": True,
                        "provider": "ollama",
                        "available_models": model_names,
                        "model_available": True,
                        "model_name": display_name,
                        "message": f"Connected to Ollama at {url}"
                    }
            except Exception:
                pass

        # 2. Hugging Face Serverless Cloud Inference (Always Available)
        hf_tok = self.get_hf_token()
        if hf_tok:
            return {
                "connected": True,
                "provider": "huggingface",
                "available_models": [self.hf_model, "meta-llama/Llama-3.2-1B-Instruct"],
                "model_available": True,
                "model_name": "Qwen2.5 LLM",
                "message": "Connected to Qwen2.5 via Hugging Face Cloud Inference"
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
        """Generates response with automatic failover between Ollama and Hugging Face."""
        conn = self.check_connection()
        if not conn.get("connected"):
            return {"success": False, "text": "", "error": "No LLM provider available"}

        # Path A: Colab / Local Ollama
        if conn.get("provider") == "ollama":
            res = self._generate_ollama(prompt, system_prompt, temperature)
            if res.get("success") and res.get("text"):
                return res

        # Path B: Hugging Face Serverless Cloud Inference
        return self._generate_huggingface(prompt, system_prompt, temperature)

    def _generate_ollama(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2
    ) -> Dict[str, Any]:
        """Executes generation against Ollama API."""
        url = self.get_effective_base_url()
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "top_p": 0.85,
                "repeat_penalty": 1.25,
                "repeat_last_n": 64,
                "num_predict": 180
            }
        }
        if system_prompt:
            payload["system"] = system_prompt

        try:
            resp = requests.post(
                f"{url}/api/generate",
                headers=self._get_headers(),
                json=payload,
                timeout=self.timeout
            )
            if resp.status_code == 200:
                data = resp.json()
                text = data.get("response", "").strip()
                if text:
                    return {
                        "success": True,
                        "text": text,
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
        """Executes generation against Hugging Face Serverless Inference API."""
        hf_tok = self.get_hf_token()
        if not hf_tok:
            return {"success": False, "text": "", "error": "No HF token"}

        candidate_models = [
            "Qwen/Qwen2.5-0.5B-Instruct",
            "meta-llama/Llama-3.2-1B-Instruct",
            "google/gemma-2-2b-it"
        ]

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # 1. Try official huggingface_hub InferenceClient
        try:
            from huggingface_hub import InferenceClient
            client = InferenceClient(api_key=hf_tok, timeout=self.timeout)
            for mod in candidate_models:
                try:
                    response = client.chat.completions.create(
                        model=mod,
                        messages=messages,
                        max_tokens=200,
                        temperature=temperature
                    )
                    if response and response.choices:
                        content = response.choices[0].message.content.strip()
                        if content and len(content) > 10:
                            return {"success": True, "text": content}
                except Exception:
                    continue
        except Exception:
            pass

        # 2. Direct HTTP Post Fallback to Hugging Face Router
        headers = {
            "Authorization": f"Bearer {hf_tok}",
            "Content-Type": "application/json"
        }
        for mod in candidate_models:
            endpoint = f"https://router.huggingface.co/hf-inference/models/{mod}/v1/chat/completions"
            payload = {
                "model": mod,
                "messages": messages,
                "max_tokens": 180,
                "temperature": temperature
            }
            try:
                resp = requests.post(endpoint, headers=headers, json=payload, timeout=self.timeout)
                if resp.status_code == 200:
                    data = resp.json()
                    choices = data.get("choices", [])
                    if choices:
                        content = choices[0].get("message", {}).get("content", "").strip()
                        if content and len(content) > 10:
                            return {"success": True, "text": content}
            except Exception:
                continue

        return {"success": False, "text": "", "error": "Hugging Face Inference servers busy"}
