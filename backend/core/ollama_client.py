"""
ML Engineering Copilot - Ollama Live Client
Handles LLM streaming, fast summarization, and vector embeddings asynchronously.
"""

from __future__ import annotations

import httpx
from typing import AsyncGenerator, List, Optional, Union
from backend.config import Settings, Config


class OllamaClient:
    def __init__(
        self,
        config_or_url: Optional[Union[Settings, str]] = None,
        timeout: float = None,
    ):
        if isinstance(config_or_url, (Settings, Config)):
            self.settings = config_or_url
            self.base_url = str(self.settings.OLLAMA_BASE_URL).rstrip("/")
        elif isinstance(config_or_url, str):
            self.settings = Settings(OLLAMA_BASE_URL=config_or_url)
            self.base_url = config_or_url.rstrip("/")
        else:
            self.settings = Settings()
            self.base_url = str(self.settings.OLLAMA_BASE_URL).rstrip("/")

        self.timeout = None

    async def check_health(self) -> bool:
        """Checks if local Ollama daemon is reachable."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.get(f"{self.base_url}/api/version")
                return res.status_code == 200
        except Exception:
            return False

    async def list_models(self) -> List[str]:
        """Lists installed local models."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            res = await client.get(f"{self.base_url}/api/tags")
            res.raise_for_status()
            models_data = res.json().get("models", [])
            return [m.get("name") for m in models_data if "name" in m]

    async def generate_embedding(self, text: str, model: Optional[str] = None) -> List[float]:
        """Generates a 768-dim vector embedding using nomic-embed-text."""
        target_model = model or self.settings.EMBEDDING_MODEL
        payload = {"model": target_model, "prompt": text}

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            res = await client.post(f"{self.base_url}/api/embeddings", json=payload)
            res.raise_for_status()
            return res.json().get("embedding", [])

    async def generate_embeddings_batch(
        self, texts: List[str], model: Optional[str] = None
    ) -> List[List[float]]:
        """Sequentially generates embeddings for a batch of documents."""
        embeddings = []
        for text in texts:
            emb = await self.generate_embedding(text, model=model)
            embeddings.append(emb)
        return embeddings

    async def generate_response(
        self,
        prompt: str,
        system: Optional[str] = None,
        model: Optional[str] = None,
    ) -> str:
        """Non-streaming response generator (used for fast summaries)."""
        target_model = model or self.settings.FAST_SUMMARY_MODEL
        payload = {"model": target_model, "prompt": prompt, "stream": False}
        if system:
            payload["system"] = system

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            res = await client.post(f"{self.base_url}/api/generate", json=payload)
            res.raise_for_status()
            return res.json().get("response", "")

    async def stream_chat(
        self,
        messages: List[dict],
        model: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """Streams LLM chat tokens using qwen3:4b or specified model."""
        target_model = model or self.settings.DEFAULT_LLM_MODEL
        payload = {"model": target_model, "messages": messages, "stream": True}

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream("POST", f"{self.base_url}/api/chat", json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    try:
                        import json
                        data = json.loads(line)
                        content = data.get("message", {}).get("content", "")
                        if content:
                            yield content
                    except Exception:
                        continue
