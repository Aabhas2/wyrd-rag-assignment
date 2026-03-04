# Wyrd Wiki — Local RAG (Chroma + Ollama)

Local Q&A over a Notion-exported wiki using:
- Ollama (`llama3` + `nomic-embed-text`)
- LangChain
- ChromaDB (local vector store)
- Gradio UI

## Prerequisites
- Python 3.10+ (recommended)
- Ollama installed

Pull models:
```bash
ollama pull llama3
ollama pull nomic-embed-text
```
### 1) Export Notion wiki

Export the wiki from Notion as Markdown & CSV (include subpages), then place the exported folder here:
```
data/notion_export/
```
### 2) Install dependencies
```bash
pip install -r requirements.txt
```
### 3) Ingest (build the local vector DB)

If you already have an old data/chroma/, delete it first to avoid duplicates.

Run ingestion:
```bash
python -c "from src.ingest import ingest; ingest()"
```
This creates:

* `data/chroma/` (Chroma vector DB)

* `data/chunks.jsonl` (chunks cache for a small mission/vision fallback)

### 4) Run the app (Gradio)
```bash
python app.py
```
Open the local URL printed in the terminal and ask questions like:

* What is Wyrd’s mission?

* What are the 5 principles in Wyrd’s Doctrine?

* What is Wyrd?