from locrag import settings, configure_logger,  RAGModel



if __name__ == "__main__":
	configure_logger()
	print(settings.RAG_API_URL)
	assistant = RAGModel.create()

	print("Entered RAG Application")
	while True:
		query = input(">>")
		
		if query == "q":
			break
		
		cmd, *arguments = query.split(" ")

		if cmd == "add":
			assistant.ingest_src(arguments[0])

		else: 
			print(assistant.answer(cmd))
