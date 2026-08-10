import requests
import json

from pathlib import Path

from .config import llmsettings

import logging

logger = logging.getLogger(__name__)


class LLM:
    def __init__(self, model_loc: Path, *, model_params: LLMConfig) -> None:
        self._model = Llama(
            model_path=str(model_loc), n_ctx=n_ctx, n_threads=n_threads, verbose=False
        )
        self.settings = llmsettings

    def get_answer(self, conversation: list[dict[str, str]]) -> str:
        response = requests.post(
            f"{LLAMA_SERVER_URL}/v1/chat/completions",
            json={
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.7,
                "max_tokens": 512,
            },
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    def stream_answer(
        self,
        conversation: list[dict[str, str]],
    ) -> str:
        logger.info(conversation)

        with requests.post(
            f"{LLAMA_SERVER_URL}/v1/vhat/completion",
            json=conversation
            | {
                "temperature": self.settings.TEMP,
                "max_tokens": self.settings.MAX_TOKENS,
            },
            stream=True,
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

        # 		logger.info(
        # 		"LLM response generated, tokens=%s", data["usage"]["completion_tokens"]
        # 		)

        # 		return data["choices"][0]["message"]["content"]

        return
