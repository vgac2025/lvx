"""Alertes utilisateur — Telegram et Gmail (SMTP)."""

from __future__ import annotations

import json
import logging
import smtplib
from dataclasses import dataclass
from datetime import datetime, timezone
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any, Literal

import httpx

from artcb.wallet.encryption import decrypt_secret_blob, encrypt_secret_blob

logger = logging.getLogger("artcb.notifications.manager")

ChannelType = Literal["telegram", "gmail"]


class NotificationError(Exception):
    """Notification delivery failed."""


@dataclass
class NotificationChannel:
    channel_id: str
    channel_type: ChannelType
    label: str
    config: dict[str, Any]
    enabled: bool = True
    _secret: str | None = None

    def public_dict(self) -> dict[str, Any]:
        return {
            "channel_id": self.channel_id,
            "channel_type": self.channel_type,
            "label": self.label,
            "config": {k: v for k, v in self.config.items()},
            "enabled": self.enabled,
            "secret_masked": "****" if self._secret else None,
        }


class NotificationManager:
    """Stocke tokens Telegram / mots de passe app Gmail localement chiffrés."""

    def __init__(self, data_dir: Path) -> None:
        self.store_path = Path(data_dir) / "notifications" / "channels.json"
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.store_path.is_file():
            self._write({"channels": []})

    def _read(self) -> dict:
        return json.loads(self.store_path.read_text(encoding="utf-8"))

    def _write(self, data: dict) -> None:
        self.store_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        self.store_path.chmod(0o600)

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def list_channels(self) -> list[NotificationChannel]:
        return [self._load(c) for c in self._read().get("channels", [])]

    def _load(self, item: dict) -> NotificationChannel:
        secret = None
        if item.get("secret_encrypted"):
            try:
                secret = decrypt_secret_blob(bytes.fromhex(item["secret_encrypted"])).decode("utf-8")
            except Exception as exc:
                logger.warning("Decrypt notification channel failed: %s", exc)
        return NotificationChannel(
            channel_id=item["channel_id"],
            channel_type=item["channel_type"],
            label=item["label"],
            config=item.get("config", {}),
            enabled=item.get("enabled", True),
            _secret=secret,
        )

    def save_channel(
        self,
        *,
        channel_type: ChannelType,
        label: str,
        secret: str,
        config: dict[str, Any] | None = None,
        channel_id: str | None = None,
    ) -> NotificationChannel:
        import uuid

        if len(secret.strip()) < 8:
            raise NotificationError("secret requis (min 8 caractères)")
        cid = channel_id or f"notif_{uuid.uuid4().hex[:12]}"
        now = self._now()
        raw = self._read()
        items = [c for c in raw.get("channels", []) if c["channel_id"] != cid]
        items.append({
            "channel_id": cid,
            "channel_type": channel_type,
            "label": label,
            "config": config or {},
            "secret_encrypted": encrypt_secret_blob(secret.strip().encode("utf-8")).hex(),
            "enabled": True,
            "created_at": now,
            "updated_at": now,
        })
        raw["channels"] = items
        self._write(raw)
        return self._load(items[-1])

    def delete_channel(self, channel_id: str) -> bool:
        raw = self._read()
        before = len(raw.get("channels", []))
        raw["channels"] = [c for c in raw.get("channels", []) if c["channel_id"] != channel_id]
        if len(raw["channels"]) == before:
            return False
        self._write(raw)
        return True

    def send(self, channel_id: str, *, subject: str, body: str) -> dict[str, Any]:
        channel = next((c for c in self.list_channels() if c.channel_id == channel_id), None)
        if not channel or not channel.enabled or not channel._secret:
            raise NotificationError("Canal introuvable ou désactivé")
        if channel.channel_type == "telegram":
            return self._send_telegram(channel, body)
        if channel.channel_type == "gmail":
            return self._send_gmail(channel, subject, body)
        raise NotificationError(f"Type inconnu: {channel.channel_type}")

    def broadcast(self, *, event: str, subject: str, body: str) -> list[dict[str, Any]]:
        results = []
        for channel in self.list_channels():
            if not channel.enabled:
                continue
            try:
                r = self.send(channel.channel_id, subject=subject, body=f"[{event}]\n{body}")
                results.append({"channel_id": channel.channel_id, "ok": True, **r})
            except NotificationError as exc:
                results.append({"channel_id": channel.channel_id, "ok": False, "error": str(exc)})
        return results

    def _send_telegram(self, channel: NotificationChannel, body: str) -> dict[str, Any]:
        chat_id = channel.config.get("chat_id")
        if not chat_id:
            raise NotificationError("telegram requiert config.chat_id")
        token = channel._secret or ""
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        with httpx.Client(timeout=20.0) as client:
            r = client.post(url, json={"chat_id": chat_id, "text": body[:4096]})
            r.raise_for_status()
            data = r.json()
        if not data.get("ok"):
            raise NotificationError(data.get("description", "Telegram API error"))
        return {"provider": "telegram", "message_id": data.get("result", {}).get("message_id")}

    def _send_gmail(self, channel: NotificationChannel, subject: str, body: str) -> dict[str, Any]:
        from_email = channel.config.get("from_email") or channel.config.get("email")
        to_email = channel.config.get("to_email") or from_email
        smtp_host = channel.config.get("smtp_host", "smtp.gmail.com")
        smtp_port = int(channel.config.get("smtp_port", 587))
        if not from_email or not to_email:
            raise NotificationError("gmail requiert config.from_email et config.to_email")
        password = channel._secret or ""
        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = from_email
        msg["To"] = to_email
        with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as server:
            server.starttls()
            server.login(from_email, password)
            server.sendmail(from_email, [to_email], msg.as_string())
        return {"provider": "gmail", "to": to_email}
