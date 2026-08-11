from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from localrag import RAGModel
from localrag.deploy import llama_server_settings
from localrag.core import configure_logger
from localrag.core.llama_server import check_generative_server, check_embedding_server

logger = logging.getLogger(__name__)


class IngestRequest(BaseModel):
    src: str


class QueryRequest(BaseModel):
    query: str


class HealthResponse(BaseModel):
    generative_server: bool
    embedding_server: bool
    status: str


rag_model: RAGModel | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global rag_model
    configure_logger(logging.INFO)

    gen_ok = check_generative_server(
        llama_server_settings.HOST_IP,
        llama_server_settings.LLAMA_GEN_PORT,
    )
    emb_ok = check_embedding_server(
        llama_server_settings.HOST_IP,
        llama_server_settings.LLAMA_EMBED_PORT,
    )

    if not gen_ok or not emb_ok:
        logger.warning(
            "llama.cpp servers not reachable at startup. "
            "Ensure systemd services are running."
        )

    rag_model = RAGModel.create(
        gen_model_path=Path("./model.gguf"),
        dimension=llama_server_settings.LLAMA_EMBED_DIM,
    )
    logger.info("RAG model initialized")

    yield

    logger.info("Shutting down")


app = FastAPI(title="Local RAG API", lifespan=lifespan)


@app.get("/health", response_model=HealthResponse)
def health():
    gen_ok = check_generative_server(
        llama_server_settings.HOST_IP,
        llama_server_settings.LLAMA_GEN_PORT,
    )
    emb_ok = check_embedding_server(
        llama_server_settings.HOST_IP,
        llama_server_settings.LLAMA_EMBED_PORT,
    )
    status = "ok" if gen_ok and emb_ok else "degraded"
    return HealthResponse(
        generative_server=gen_ok,
        embedding_server=emb_ok,
        status=status,
    )


@app.post("/ingest")
def ingest(request: IngestRequest):
    if rag_model is None:
        raise HTTPException(status_code=503, detail="RAG model not initialized")

    docs = rag_model._ingestion_pipeline.process_doc(request.src)
    if not docs:
        raise HTTPException(status_code=400, detail="No documents processed")

    for doc in docs:
        doc.embedding = rag_model._ingestion_pipeline.embed(doc.content)

    rag_model._db_manager.add_documents(docs)
    return {"chunks_added": len(docs)}


@app.post("/query")
def query(request: QueryRequest):
    if rag_model is None:
        raise HTTPException(status_code=503, detail="RAG model not initialized")

    try:
        answer = rag_model.generate_response(request.query)
        return {"response": answer}
    except Exception as exc:
        logger.exception("Query failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/stream")
def stream(request: QueryRequest):
    if rag_model is None:
        raise HTTPException(status_code=503, detail="RAG model not initialized")

    def generate():
        try:
            for token in rag_model.stream_response(request.query):
                yield token
        except Exception as exc:
            logger.exception("Stream failed")
            yield f"\n[ERROR] {exc}"

    return StreamingResponse(generate(), media_type="text/plain")


@app.get("/history")
def history():
    if rag_model is None:
        raise HTTPException(status_code=503, detail="RAG model not initialized")

    return {"messages": rag_model._conversation.messages}
