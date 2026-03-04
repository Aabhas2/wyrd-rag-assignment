from langchain_core.prompts import ChatPromptTemplate 

PROMPT = ChatPromptTemplate.from_messages([
    ("system",
    "You are answering questions about Wyrd Media Labs' Company Wiki.\n"
    "RULES:\n"
    "1) Use ONLY the provided context. Do not use outside knowledge.\n"
    "2) Do NOT infer, assume, or add implied points. If something is not explicitly stated, say: "
    "'I don't know based on the wiki.'\n"
    "3) If the question asks for a list (e.g., principles/steps), output ONLY items explicitly present in context.\n"
    "4) Always include a Sources section listing which sources you used (by the [#] markers)."
    ),
    ("human",
    "Question: {question}\n\n"
    "Context:\n{context}\n\n"
    "Write the answer and cite sources inline using [1], [2], etc. "
    "If not found, say: 'I don't know based on the wiki.'\n\n"
    "Answer:")
])

def format_context(docs): 
    blocks = [] 
    for i,d in enumerate(docs, 1): 
        title = d.metadata.get("title", "Untitled")
        src = d.metadata.get("source", "")
        blocks.append(f"[{i}] {title} ({src})\n{d.page_content}")

    return "\n\n".join(blocks)