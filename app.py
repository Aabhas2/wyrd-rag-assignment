import gradio as gr 
from src.query import ask 

CHROMA_DIR = "data/chroma"
COLLECTION = "wyrd_wiki"
CHUNKS_JSONL = "data/chunks.jsonl" 

def answer_question(q: str): 
    q = (q or "").strip() 
    if not q: 
        return "Type a question." 
    try:
        return ask(
        q,
        chroma_dir=CHROMA_DIR, 
        collection_name=COLLECTION, 
        chunks_jsonl=CHUNKS_JSONL, 
        top_k=4, 
    )
    except Exception as e: 
        return f"**Error:** {type(e).__name__}: {e}"

with gr.Blocks(title="Wyrd Wiki - Local RAG", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# Wyrd Wiki - Local RAG")
    gr.Markdown(
        "Ask questions about the Wyrd company wiki. "
        "Retrieval uses ChromaDB, embeddings via nomic-embed-text (Ollama), "
        "generation via llama3 (Ollama). Fully local."
    )

    with gr.Row():
        question = gr.Textbox(
            lines=3,
            label="Question",
            placeholder="Try: What does Wyrd stand for?",
            scale=5,
        )
        with gr.Column(scale=1, min_width=150):
            ask_btn = gr.Button("Ask", variant="primary")
            clear_btn = gr.Button("Clear")

    answer = gr.Markdown(label="Answer")

    gr.Examples(
        examples=[
            "What is Wyrd?",
            "Who are we fighting against?",
            "What are Wyrd's values?",
            "Summarize our mission in 3 bullet points.",
        ],
        inputs=question,
    )

    ask_btn.click(fn=answer_question, inputs=question, outputs=answer)
    question.submit(fn=answer_question, inputs=question, outputs=answer)
    clear_btn.click(
        fn=lambda: ("", ""),
        inputs=None,
        outputs=[question, answer],
        queue=False,
    )

if __name__=="__main__": 
    demo.queue()
    demo.launch(share=True)