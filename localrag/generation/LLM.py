import json
import requests

from pathlib import Path
from typing import Generator

from .config import LLMSettings, llmsettings
from localrag.deploy import llama_server_settings
from localrag.core import get_session

import logging

logger = logging.getLogger(__name__)


class LLM:
    def __init__(self, model_path: Path, *, model_params: LLMSettings) -> None:
        self.settings = llmsettings
        self._session = get_session()

    def get_answer(self, conversation: list[dict[str, str]]) -> str:
        response = self._session.post(
            f"{llama_server_settings.HOST_IP}:{llama_server_settings.LLAMA_GEN_PORT}/v1/chat/completions",
            json={
                "messages": conversation,
                "temperature": self.settings.TEMP,
                "max_tokens": self.settings.MAX_TOKENS,
            },
            timeout=120,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    def stream_answer(
        self,
        conversation: list[dict[str, str]],
    ) -> Generator:
        logger.info(conversation)

        with self._session.post(
            f"{llama_server_settings.HOST_IP}:{llama_server_settings.LLAMA_GEN_PORT}/v1/chat/completions",
            json={
                "messages": conversation,
                "temperature": self.settings.TEMP,
                "max_tokens": self.settings.MAX_TOKENS,
            },
            stream=True,
            timeout=120,
        ) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if not line or not line.startswith(b"data: "):
                    continue
                chunk = line[len(b"data: ") :]
                if chunk == b"[DONE]":
                    break
                delta = json.loads(chunk)["choices"][0]["delta"]
                if "content" in delta:
                    yield delta["content"]

        return
