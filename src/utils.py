import re 
import hashlib 
from pathlib import Path 
from typing import List 

IMG_LINE = re.compile(r'^\s*!\[.*?\]\(.*?\)\s*$')
ASIDE_TAG = re.compile(r'^\s*</?aside>\s*$', re.IGNORECASE)

def clean_title_from_filename(name: str) -> str: 
    name = name.replace(".md", "")
    name = re.sub(r"\s[0-9a-f]{8,}$", "", name.strip(), flags=re.IGNORECASE)
    return name.strip()

def stable_id_from_path(rel_path: str) -> str: 
    return hashlib.sha1(rel_path.encode("utf-8")).hexdigest()[:12]

def minimal_md_cleanup(text: str) -> str: 
    lines = text.splitlines() 
    cleaned = [] 
    in_code_block = False 

    for i, raw in enumerate(lines): 
        line = raw.rstrip("\n")

        if line.strip().startswith("```"): 
            in_code_block = not in_code_block
            cleaned.append(line) 
            continue    
        if in_code_block: 
            cleaned.append(line) 
            continue 

        if IMG_LINE.match(line):
            continue 
        if ASIDE_TAG.match(line): 
            continue

        s = line.strip() 
        if not s: 
            continue 

        if i < 25 and re.search(r'^\s*open in notion\s*$', s, re.IGNORECASE):
            continue
        if i < 25 and re.search(r'^\s*last updated\b', s, re.IGNORECASE):
            continue

        cleaned.append(line.rstrip())

    return "\n".join(cleaned) 

def filter_docs(docs):
    # Remove root index and dedupe by chunk id  
    seen = set()
    out = [] 
    for d in docs:
        if d.metadata.get("is_root_index"): 
            continue
        cid = d.metadata.get("chunk_id")
        if cid and cid in seen: 
            continue 
        if cid: 
            seen.add(cid) 
        out.append(d) 

    return out 