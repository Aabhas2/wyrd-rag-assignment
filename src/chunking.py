import hashlib 
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter 

def chunk_documents(docs, min_chars: int = 200): 
    headers_to_split = [("#", "h1"), ("##", "h2"), ("###", "h3")]
    md_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split, strip_headers=False) 

    header_chunks = [] 
    for d in docs: 
        splits = md_splitter.split_text(d.page_content) 
        for s in splits: 
            s.metadata.update(d.metadata) 

        header_chunks.extend(splits) 

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=150, 
        separators=["\n## ", "\n### ", "\n#### ", "\n\n", "\n", " ", ""],
    )
    final_chunks = text_splitter.split_documents(header_chunks) 

    # add chunk_id and filter 
    kept = [] 
    for i,c in enumerate(final_chunks): 
        if len(c.page_content.strip()) < min_chars: 
            continue 
        base = f"{c.metadata.get('source','')}|{c.metadata.get('h1','')}|{c.metadata.get('h2','')}|{i}"
        c.metadata["chunk_id"] = hashlib.sha1(base.encode("utf-8")).hexdigest()[:12] 
        kept.append(c) 

    return kept 
