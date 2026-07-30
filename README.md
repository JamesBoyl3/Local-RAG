# Local RAG AI Assistant (LocRAG)

---

## Project Description
This project aims to create an interface to aid in building fully local RAG applications (think of a RAG equivalent of ollama or a local version of delphi). 

---

## Motivation
In the past, I helped develop a RAG application using [delphi.ai](https://www.delphi.ai/) for a company to aid in searching through research papers. Whilst this solution was satisfying, it had some downsides. 

You had no control over what delphi does with your data, meaning you could not use sensitive documents. Secondly it was subscription based, meaning you had constant expenditure to maintain the system. 

This solution aims to fix these problems. By allowing a similar process to run locally, you can invest in hardware (gets rid of subscription concerns and privacy) and install this software. Now you have a local RAG application and can use it for any document you want. 

---

## Used technologies 
- llama.cpp (for LLM models and Embedding Models)
- faiss (for storing and searching embeddings)
- sqlite3 (for storing meta-data of each document for references)
- fitz & langchain-text-splitters (for pdf processing)
- BeutifualSoup and requests (for crawling the web for documents)

---

### Short-term roadmap
- [ ] Fix ongoing bugs for basic application
- [ ] Introduce Multi-lingual models
- [ ] Intoruce Multi-modal models (iamges, videos etc.)
- [ ] Utilise faiss GPU capabilities
