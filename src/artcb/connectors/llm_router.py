"""Clients LLM utilisateur — OpenAI, Anthropic, Bob via clés connecteur."""

from __future__ import annotations

import json
import logging
from typing import Any

import httpx

from artcb.connectors.manager import ConnectorRecord

logger = logging.getLogger("artcb.connectors.llm_router")


class LLMRouter:
    """Route les requêtes LLM vers le fournisseur choisi par l'utilisateur."""

    def classify_sentences(
        self,
        sentences: list[str],
        *,
        record: ConnectorRecord,
        api_key: str,
    ) -> list[dict[str, str]] | None:
        numbered = "\n".join(f"{i}: {s}" for i, s in enumerate(sentences))
        prompt = (
            "Classify each sentence for an IR knowledge graph. "
            "Return ONLY a JSON array of objects with keys: index (int), type (one of "
            "FACT, DECISION, HYPOTHESIS, REASON, GOAL, PROOF, EVENT, CONTEXT), "
            f"symbol (short USP code like O1M1).\n\nSentences:\n{numbered}"
        )
        model = record.config.get("model")
        try:
            if record.provider == "openai":
                raw = self._openai_chat(api_key, prompt, model=model or "gpt-4o-mini")
            elif record.provider == "anthropic":
                raw = self._anthropic_chat(api_key, prompt, model=model or "claude-3-5-haiku-20241022")
            elif record.provider == "bob":
                raw = self._bob_chat(api_key, prompt, record, model=model)
            else:
                logger.warning("Unsupported LLM provider: %s", record.provider)
                return None
            return self._parse_classification(raw)
        except Exception as exc:
            logger.error("LLM classify via %s failed: %s", record.provider, exc)
            return None

    def _parse_classification(self, raw: str) -> list[dict[str, str]] | None:
        start = raw.find("[")
        end = raw.rfind("]") + 1
        if start < 0 or end <= start:
            return None
        parsed = json.loads(raw[start:end])
        if not isinstance(parsed, list):
            return None
        return [
            {
                "index": str(item.get("index", "")),
                "type": str(item.get("type", "FACT")),
                "symbol": str(item.get("symbol", "")),
            }
            for item in parsed
        ]

    def _openai_chat(self, api_key: str, prompt: str, *, model: str) -> str:
        with httpx.Client(timeout=60.0) as client:
            r = client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                },
            )
            r.raise_for_status()
            return str(r.json()["choices"][0]["message"]["content"]).strip()

    def _anthropic_chat(self, api_key: str, prompt: str, *, model: str) -> str:
        with httpx.Client(timeout=60.0) as client:
            r = client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "max_tokens": 4096,
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
            r.raise_for_status()
            data = r.json()
            return str(data["content"][0]["text"]).strip()

    def _bob_chat(self, api_key: str, prompt: str, record: ConnectorRecord, *, model: str | None) -> str:
        from artcb.config import load_settings

        settings = load_settings()
        base = record.config.get("base_url") or settings.bob_api_base
        model_name = model or settings.bob_model
        from litellm_ibm_bob._transport import BobTransport, TransportConfig

        cfg = TransportConfig(
            api_key=api_key,
            base_url=base,
            team_id=record.config.get("team_id"),
            instance_id=record.config.get("instance_id"),
        )
        transport = BobTransport(cfg)
        try:
            response = transport.request(
                "POST",
                "/inference/v1/chat/completions",
                body={
                    "model": model_name,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                },
            )
            if not response.is_success:
                raise RuntimeError(f"Bob failed: {response.status_code} {response.text[:300]}")
            data = response.json()
            return str(data["choices"][0]["message"]["content"]).strip()
        finally:
            transport.close()
