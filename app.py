import gradio as gr 
from src.query import ask 

CHROMA_DIR = "data/chroma"
COLLECTION = "wyrd_wiki"
CHUNKS_JSONL = "data/chunks.jsonl" 

def answer_question(q: str): 
    q = (q or "").strip() 
    if not q: 
        return "Type a question." 
    return ask(
        q,
        chroma_dir=CHROMA_DIR, 
        collection_name=COLLECTION, 
        chunks_jsonl=CHUNKS_JSONL, 
        top_k=4, 
    )

demo = gr.Interface(
    fn=answer_question,
    inputs=gr.Textbox(lines=2, placeholder="Ask about the Wyrd wiki... :)"), 
    outputs=gr.Markdown(), 
    title="Wyrd Wiki - Local RAG (Chroma + Ollama)", 
    description="Runs fully locally. Retrieval: Chroma (MMR) + small mission/vision fallback. Generation: llama3 via Ollama.",
)

if __name__=="__main__": 
    demo.launch(share=True)