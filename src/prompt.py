from langchain_core.prompts import ChatPromptTemplate 

PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are answering questions about Wyrd Media Labs' Company Wiki. "
     "Use ONLY the provided context. If the answer is not in the context, say: "
     "'I don't know based on the wiki.' "
     "Write a clear answer, then add a Sources section listing which sources you used."),
    ("human",
     "Question: {question}\n\n"
     "Context:\n{context}\n\n"
     "Answer:")
])

def format_context(docs): 
    blocks = [] 
    for i,d in enumerate(docs, 1): 
        title = d.metadata.get("title", "Untitled")
        src = d.metadata.get("source", "")
        blocks.append(f"[{i}] {title} ({src})\n{d.page_content}")

    return "\n\n".join(blocks)