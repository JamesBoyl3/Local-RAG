# Local RAG Assistant

A local-first RAG (Retrieval-Augmented Generation) application for building fully offline document Q&A systems — a local, self-hosted alternative to services like delphi.ai.

<!--
Badges go here once there's something real to report, e.g.:
![Tests](https://github.com/<user>/locrag/actions/workflows/tests.yml/badge.svg)
![Coverage](https://codecov.io/gh/<user>/locrag/branch/main/graph/badge.svg)
See https://shields.io/ for how these are generated.
-->

---

## Installation

This project uses [uv](https://docs.astral.sh/uv/) as its build backend and package manager.

```bash
git clone https://github.com/JamesBoyl3/locrag.git
cd locrag
uv sync
```

If you don't have `uv` installed, see the [uv installation guide](https://docs.astral.sh/uv/getting-started/installation/).

---

## Setup

LocRAG loads configuration from an environment file at import/runtime (you can see configuration at [localrag/core/config.py](https://github.com/JamesBoyl3/Local-RAG/blob/master/localrag/core/config.py). You'll need to create the following before running anything:

<table>
  <tr>
      <td>Enviroment File (NEEDED)</td>
      <td>Specific Config</td>
      <td>Variables</td>
  </tr>
  <tr>
    <td rowspan="3">.env</td>
    <td><code>LLMConfig</code></td>
    <td><code>llm__TEMP</code>, <code>llm__MAX_TOKENS</code>, <code>llm__N_CTX</code></td>
  </tr>
  <tr>
    <td><code>ServerConfig</code></td>
    <td><code>server__HOST_IP</code>,<code>server__HOST_PORT</code></td>
  </tr>
    <tr>
        <td><code>Settings</code></td>
        <td><code>GEN_MODEL_PATH</code>, <code>EMBED_MODEL_PATH</code></td>
    </tr>
</table>

**NOTE:** Some of the variables are not needed, as they have defaults. See [.env.example](https://github.com/JamesBoyl3/Local-RAG/blob/master/.env.example) for the bare minimum. 

You'll also need a local [llama.cpp](https://github.com/ggml-org/llama.cpp) build, plus a GGUF generative model and a GGUF embedding model on disk, since `GEN_MODEL_PATH` and `EMBED_MODEL_PATH` need to point at real files.

---

## Quick start

```python
from localrag import settings, configure_logger, RAGModel

import logging

configure_logger(logging.DEBUG)

assistant = RAGModel.create(
    settings.GEN_MODEL_PATH,
    dimension=384,  # must match your embedding model's output dimension
)

# ingest a document
assistant.ingest_src("path/to/document.pdf")

# ask a question
print(assistant.generate_response("What is district heating?"))
```

See `example.py` in the repo root for a runnable CLI loop version of this.

---

## Running as an API

The API also ships a [FastAPI](https://fastapi.tiangolo.com/) server (`localrag/server.py`):

```bash
uv run uvicorn localrag.server:app --host 127.0.0.1 --port 8000
```

| Endpoint | Method | Purpose |
|---|---|---|
| `/health` | GET | Reports whether the generative/embedding llama.cpp servers are reachable |
| `/ingest` | POST | Ingest a document (`{"src": "path/or/url"}`) |
| `/query` | POST | Ask a question, get a full response (`{"query": "..."}`) |
| `/stream` | POST | Same as `/query` but streams tokens back |
| `/history` | GET | Returns the current conversation history |

---

## Deployment

Systemd unit files and a setup script for running the generative server, embedding server, and API server as background services are in [`localrag/deploy/`](./localrag/deploy/). Run `sudo localrag/deploy/llama-server-setup.sh` to install them.

---

## Used technologies

See [`pyproject.toml`](./pyproject.toml) for the full, versioned dependency list. At a high level:
- [llama.cpp](https://github.com/ggml-org/llama.cpp) — running the LLM and embedding models locally
- [FAISS](https://github.com/facebookresearch/faiss) — vector storage and similarity search
- SQLite (via the standard library) — document metadata storage
- [PyMuPDF (fitz)](https://pymupdf.readthedocs.io/) + [langchain-text-splitters](https://python.langchain.com/docs/how_to/#text-splitters) — PDF parsing and chunking
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) + [Requests](https://requests.readthedocs.io/) — web page crawling
- [FastAPI](https://fastapi.tiangolo.com/) — the HTTP API layer

---

### Short-term roadmap
- [ ] Get the Embedding Dimension Synamically (test response) 
- [ ] Utilise FAISS & llama_cpp.server GPU capabilities

---

## License

This project is licensed under the [GNU GPLv3](./LICENSE).
