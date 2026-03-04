import json 
from pathlib import Path 

from langchain_community.vectorstores import Chroma 
from langchain_ollama import OllamaEmbeddings, ChatOllama 

from .utils import filter_docs 
from .prompt import PROMPT, format_context 

def load_vectorstore(chroma_dir="data/chroma", collection_name="wyrd_wiki"): 
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    return Chroma(
        persist_directory=chroma_dir, 
        collection_name=collection_name,
        embedding_function=embeddings,
    )

def build_retriever(vectorstore): 
    return vectorstore.as_retriever(
        search_type="mmr", 
        search_kwargs={"k":8, "fetch_k": 30},
    )

def keyword_fallback_from_jsonl(chunks_jsonl: str, query: str, limit=2): 
    q = query.lower() 
    if not ("mission" in q or "vision" in q):
        return [] 
    
    hits = [] 
    path = Path(chunks_jsonl) 
    if not path.exists():
        return [] 
    
    with path.open("r", encoding="utf-8") as f: 
        for line in f: 
            obj = json.loads(line) 
            text = obj["text"].lower() 
            title = obj["metadata"].get("title", "").lower() 
            if "why wyrd" in title or "wyrd enough to matter" in text or "mission" in text or "vision" in text: 
                hits.append(obj) 
                if len(hits) >= limit: 
                    break 

    return hits 

def ask(question: str, chroma_dir="data/chroma", collection_name="wyrd_wiki", chunks_jsonl="data/chunks.jsonl", top_k=4): 
    vectorstore = load_vectorstore(chroma_dir, collection_name) 
    retriever = build_retriever(vectorstore) 

    docs_vec = filter_docs(retriever.invoke(question)) 

    # fallback 
    fallback = keyword_fallback_from_jsonl(chunks_jsonl, question, limit=2) 
    
    # build context 
    blocks = [] 
    idx = 1
    for obj in fallback: 
        title = obj["metadata"].get("title", "Untitled") 
        src = obj["metadata"].get("source", "") 
        blocks.append(f"[{idx}] {title} ({src})\n{obj['text']}") 
        idx += 1 

    docs_vec = docs_vec[:max(0, top_k - len(fallback))]
    for d in docs_vec:
        title = d.metadata.get("title", "Untitled")
        src = d.metadata.get("source", "")
        blocks.append(f"[{idx}] {title} ({src})\n{d.page_content}")
        idx += 1

    context = "\n\n".join(blocks)

    llm = ChatOllama(model="llama3", temperature=0)
    msg = PROMPT.format_messages(question=question, context=context)
    resp = llm.invoke(msg)

    return resp.content