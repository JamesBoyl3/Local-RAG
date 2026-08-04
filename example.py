
from locrag import settings, configure_logger,  RAGModel

import os
import logging

if __name__ == "__main__":
	configure_logger(logging.DEBUG)
	print(f"{settings.GEN_MODEL_LOC=}\n{settings.HF_EMBEDDING_MODEL_LOC}\n{settings.LOC_EMBEDDING_MODEL_LOC}")

	if os.path.exists(settings.LOC_EMBEDDING_MODEL_LOC): 
		assistant = RAGModel.create(settings.GEN_MODEL_LOC, settings.LOC_EMBEDDING_MODEL_LOC)
	else: 
		assistant = RAGModel.create(settings.GEN_MODEL_LOC, settings.HF_EMBEDDING_MODEL_LOC)
		assistant.save_embedding_model(settings.LOC_EMBEDDING_MODEL_LOC)

	print("Entered RAG Application")
	while True:
		query = input(">>")
		
		if query == "q":
			break
		
		cmd, *arguments = query.split(" ")

		if cmd == "add":
			assistant.ingest_src(arguments[0])

		else: 
			print(assistant.generate_response(query))
