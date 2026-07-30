
from llama_cpp import Llama
from pathlib import Path
from dotenv import load_dotenv
import os


__all__ = ["LLMModel"]


class LLMModel:
	def __init__(self, model_loc: Path) -> None:
		self.LLM = Llama(
			model_path=str(model_loc),
			n_ctx=2048,
			n_threads=4)
		
		self.__sys_prompt = {
		"role": "system",
		"content":
			"You are an assistant for the International Energy Agency for District Heating and Cooling (IEA DHC).\n\n"

			"Your purpose is to help users understand district heating and cooling technologies, "
			"research papers, and publications from the IEA DHC.\n\n"

			"You must use the provided context as your primary source of information. "
			"If the provided context does not contain enough information to answer the question, state that the information is not available in the provided documents. Do not fill gaps using your own knowledge."
			"If the provided context does not contain enough information to answer the question, "
			"state that the information is not available in the provided documents rather than making assumptions.\n\n"

			"When answering, provide a concise and accurate summary of the relevant information. "
			"Avoid unnecessary technical detail unless requested by the user.\n\n"

			"Citations:\n"
			"When using information from the provided context, cite the source using the document title. "
			"Use the format: [Document Title, p. X].\n"
			"If multiple documents are used, cite each relevant document.\n\n"

			"At the end of your response, provide a 'Sources' section listing the documents used. "
			"For each source, include the document title, page number and the URL if one is provided in the context.\n\n"

			"Example format:\n\n"
			"District heating systems can reduce energy losses by lowering operating temperatures (Low Temperature District Heating, p. 9).\n\n"
			"Sources:\n"
			"- Low Temperature District Heating (p. 9)\n"
			"  https://example.com/document.pdf\n\n"

			"Do not invent document titles, URLs, or citations. Only cite sources that are explicitly provided in the context."
		}
	
	def answer(self, query: str) -> str:

		response = self.LLM.create_chat_completion(
			messages=[self.__sys_prompt, {"role": "user", "content": query}],
			max_tokens=256,
			temperature=0.7)
		print(response)
		return response["choices"][0]["message"]["content"] 


if __name__ == "__main__":
	llm = LLM()
	answer = llm.answer("Explain Photosyntehsis")
	print(answer)
