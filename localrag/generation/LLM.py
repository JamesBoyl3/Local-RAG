import json
import requests

from pathlib import Path
from typing import Generator

from localrag.core import get_session, LLMConfig

import logging

logger = logging.getLogger(__name__)


class LLM:
    def __init__(self, host: str, port: int, config: LLMConfig) -> None:
        self._host = host
        self._port = port
        self._temp = config.TEMP
        self._max_tokens = config.MAX_TOKENS
        # self._n_ctx = n_ctx
        self._session = get_session()

    def get_answer(self, conversation: list[dict[str, str]]) -> str:
        response = self._session.post(
            f"http://{self._host}:{self._port}/v1/chat/completions",
            json={
                "messages": conversation,
                "temperature": self._temp,
                "max_tokens": self._max_tokens,
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
        logger.info(conversation.messages[-3:])

        with self._session.post(
            f"http://{self._host}:{self._port}/v1/chat/completions",
            json={
                "messages": conversation,
                "temperature": self._temp,
                "max_tokens": self._max_tokens,
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
