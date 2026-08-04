
from llama_cpp import Llama

from pathlib import Path

import logging
logger = logging.getLogger(__name__)

class LLM:
	def __init__(self, model_loc: Path, *, sys_prompt: str|None=None, n_ctx: int=2048, n_threads: int=4) -> None:
		self._model = Llama(
				model_path=str(model_loc),
				n_ctx=n_ctx,
				n_threads=n_threads,
				verbose=False)
		
		self._sys_prompt = {
				"role": "system",
				"content": sys_prompt
				}

	def answer(self, conversation: list[dict[str, str]], max_tokens: int=1024, temp: float=0.7) -> str:
		logger.info(conversation)
		response = self._model.create_chat_completion(
				messages=conversation,
				max_tokens=max_tokens,
				temperature=temp)
		
		logger.info(
			"LLM response generated, tokens=%s",
			response["usage"]["completion_tokens"]
			)

		return response["choices"][0]["message"]["content"]

