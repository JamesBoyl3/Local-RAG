
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
from contextlib import asynccontextmanager

from localRAG.LLM import LLMModel
import asyncio

from localRAG.RAG import RAGModel

from pathlib import Path

import pdb

from dotenv import load_dotenv
import os

load_dotenv(".env")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # app.state.rag = RAGModel(llm=LLMModel())
    
    # with DBManager("sites.db") as db:
        # pass

    yield

    del app.state.llm


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS"),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Request(BaseModel):
	prompt: str
    

@app.post("/chat")
async def chat(req: Request):
    try:
        result = await run_in_threadpool(
            	app.state.llm.answer,
		req.prompt
		)
        return {"answer": result}
    except Exception as e:
        return {"response": str(e)}
    

if __name__ == "__main__":
	
	print("Setting up RAG")
	model = RAGModel(llm=LLMModel(Path(os.getenv(model_path:="MODEL_PATH"))))
	print(model_path)

	print("Indexing")
	model.index_pdf("https://www.iea-dhc.org/fileadmin/documents/Annex_XIV/IEA_DHC_XIV-07_Social_Sustainability_Summary_Report.pdf")

	query = "What is the IEA?"

	print(f"Answering query: {query}")
	answer = model.answer(query=query)

	print(f"{answer=}")
     
