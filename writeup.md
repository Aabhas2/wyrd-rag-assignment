# Local RAG on Wyrd Media Lab's Wiki - Writeup 

## What I built 
A local RAG system that answers question related to Wyrd's company wiki.  

Stack used: **LangChain + ChromaDB + Ollama** (llama3 for generation, nomic-embed-text for embeddings) with a small **Gradio** interface.

--- 

## Why I chunked the way I did 
The source was a notion wiki, so I exported it as **Markdown & CSV** and indexed the **Markdown** files. Markdown is basically structured text (with headings, bullets, paragraphs), so it's easy to load reliably using a TextLoader (from langchain) and then split into chunks. 

For chunking, I wanted chunks which doesn't lose the meaning together, so I chunked in two stages: 
1) **Split by Markdown headings** first (so sections like "Why Wyrd?", "Wyrd's Doctrine", etc. stay grouped). 
2) If a seciton is still too large, I apply a **recursive splitter** to keep chunk sizes reasonable and add a small overlap so information near boundaries isn't lost. 

This made retrieval more consistent than just splitting every N characters. 

--- 

## How I understand the RAG pipeline 
The pipeline is basically: 

1) **Data Ingestion**: load markdown pages from the notion export 
2) **Cleanup**: remove obvious noise from Notion export (lie image-only lines and extra markup) so embeddings focus on the actual text 
3) **Chunking**: split text into smaller meaningful pieces
4) **Embeddings**: convert each chunk into a vector using `nomic-embed-text` (Ollama) 
5) **VectorDB**: store vectors in ChromaDB which is a vector database using SQLlite as its foundation
6) **Query time**: embed the user question -> retrieve the most relevant chunks -> send those chunks as context to `llama3` -> generate an answer + show sources 

So the model isn't "reading the whole wiki" every time, it's only reading the top retrieved chunks. 

---

## What I'd improve next 
I'm still early in RAG, but a few obvious improvements I noticed while building: 

- **Tune chunk parameters** (chunk size / overlap) based on real queries. Some pages are very structured and could use smaller chunks, while story-like pages which has more content, could use larger ones. 
- Add a **reranker** (or a hybrid search) so retrieval is stronger for short factual question and doesn't get distracted by index-like pages. 
- Add a small **evaluation set** (10-20 questions) so I can measure whether changes actually improve results instead of guessing and it will help me resolve possible hallucinations in the model's answer. 

--- 

## Where it breaks / issues I faced 
- **Hallucinations**: if the retrieved context is slightly off or incomplete, the LLM sometimes tries to "fill in" missing points. I tightened the prompt to reduce this, but it's still risk with local LLMs. 
- **Notion export quirks**: I saw cases where the export produced multiple "root/index" type pages and they could show up in retrieval even though they mostly contain links. I handled this by filtering/deduping based on metadata, but it's something which can be improved further.
- **Cross-page questions**: questions that require combining info from multiple distant sections can fail if the correct chunks don't land in the top-k retrieval. 

Overall, the system works end-to-end locally and answers most of the basic wiki questions with sources, but retrieval quality, time, hallucination control are the main areas I'd improve next. 