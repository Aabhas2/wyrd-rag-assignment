import json 
from pathlib import Path 

from langchain_community.document_loaders import DirectoryLoader, TextLoader 
from langchain_ollama import OllamaEmbeddings 
from langchain_community.vectorstores import Chroma 

from .utils import clean_title_from_filename, stable_id_from_path, minimal_md_cleanup 
from .chunking import chunk_documents 

def ingest(
        notion_export_dir: str = "data/notion_export", 
        chroma_dir: str = "data/chroma", 
        collection_name: str = "wyrd_wiki",
        chunks_jsonl: str = "data/chunks.jsonl"
): 
    notion_path = Path(notion_export_dir).resolve() 
    if not notion_path.exists(): 
        raise FileNotFoundError(f"Notion export folder not found: {notion_export_dir}")
    
    loader = DirectoryLoader(
        str(notion_path),
        glob="**/*.md",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
        show_progress=True 
    )
    docs = loader.load() 

    # add metadata + cleanup md files 
    for d in docs: 
        src = Path(d.metadata.get("source", "")).resolve() 
        rel = str(src.relative_to(notion_path)) if src.is_absolute() else d.metadata.get("source", "")
        filename = Path(rel).name 
        title = clean_title_from_filename(filename) 

        d.metadata.update({
            "source": rel, 
            "title": title, 
            "doc_id": stable_id_from_path(rel), 
            "notion_export": True, 
            "is_root_index": title.lower().startswith("wyrd media labs"),
        })
        d.page_content = minimal_md_cleanup(d.page_content) 

    chunks = chunk_documents(docs) 

    # save chunks for keyword fallback (jsonl) 
    chunks_path = Path(chunks_jsonl) 
    chunks_path.parent.mkdir(parents=True, exist_ok=True) 
    with chunks_path.open("w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps({"text": c.page_content, "metadata": c.metadata}, ensure_ascii=False) + "\n")

    # Build vectorstore 
    embeddings = OllamaEmbeddings(model="nomic-embed-text") 

    vectorstore = Chroma.from_documents(
        documents=chunks, 
        embedding=embeddings,
        persist_directory=chroma_dir, 
        collection_name=collection_name
    )

    print(f"Ingested {len(docs)} docs -> {len(chunks)} chunks")
    print(f"Chroma persisted at: {chroma_dir} (collection: {collection_name})") 
    print(f"Chunks saved at: {chunks_jsonl}")