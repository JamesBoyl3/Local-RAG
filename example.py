from localrag import settings, configure_logger, RAGModel

import logging

if __name__ == "__main__":
    configure_logger(logging.DEBUG)
    print(f"{settings.GEN_MODEL_PATH=}\n{settings.EMBED_MODEL_PATH}")

    assistant = RAGModel.create(
        settings.GEN_MODEL_PATH,
        dimension=384,
    )

    print("Entered RAG Application")
    while True:
        query = input(">> ")

        if query == "q":
            break

        cmd, *arguments = query.split(" ")

        if cmd == "add":
            assistant.ingest_src(arguments[0])

        else:
            print(assistant.generate_response(query))
