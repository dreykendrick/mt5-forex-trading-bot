from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

import requests

from src.utils.logging import get_logger


logger = get_logger(__name__)


@dataclass
class TelegramAlert:
    token: Optional[str]
    chat_id: Optional[str]

    def send(self, message: str) -> None:
        if not self.token or not self.chat_id:
            return
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {"chat_id": self.chat_id, "text": message}
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
        except requests.RequestException as exc:
            logger.error("Telegram alert failed", {"error": str(exc)})


def load_telegram_alert() -> TelegramAlert:
    return TelegramAlert(
        token=os.getenv("TELEGRAM_TOKEN"),
        chat_id=os.getenv("TELEGRAM_CHAT_ID"),
    )
