# ─── RAG Prompt Templates ─────────────────────────────────────────────────────
# These prompts are the KEY to preventing hallucination.
# We explicitly instruct the LLM to ONLY use the provided context.

RAG_SYSTEM_PROMPT = """You are an intelligent document assistant. Your job is to answer questions \
based STRICTLY on the document excerpts provided in the context below.

RULES you must ALWAYS follow:
1. Answer ONLY using information from the context. Do NOT use outside knowledge.
2. If the context does not contain enough information to answer, respond with:
   "I couldn't find relevant information in the uploaded documents to answer this question."
3. Always cite which document your answer comes from (use the document name).
4. Be concise but complete. Use bullet points for lists.
5. If multiple documents contain relevant info, synthesize them clearly.
6. Never make up facts, statistics, or details not present in the context.
"""

RAG_USER_TEMPLATE = """Context from uploaded documents:
{context}

---
Question: {question}

Please answer based only on the context above. Include the document source in your answer."""


CHAT_HISTORY_TEMPLATE = """Previous conversation:
{history}

---
New context from documents:
{context}

---
New question: {question}

Answer based on the context and conversation history above:"""


def format_context_block(chunks: list[dict]) -> str:
    """
    Format retrieved chunks into a readable context block for the LLM.

    Example output:
    [Source: machine_learning.pdf | Page 3 | Match: 89%]
    "Gradient descent is an optimization algorithm..."

    [Source: deep_learning.pdf | Page 7 | Match: 82%]
    "Neural networks consist of layers..."
    """
    if not chunks:
        return "No relevant context found."

    parts = []
    for i, chunk in enumerate(chunks, 1):
        score_pct = int(chunk["similarity_score"] * 100)
        parts.append(
            f'[Source: {chunk["document_name"]} | '
            f'Page {chunk.get("page_number", "?")} | '
            f'Match: {score_pct}%]\n'
            f'"{chunk["text"]}"'
        )
    return "\n\n".join(parts)


def format_conversation_history(messages: list) -> str:
    """Format chat history for inclusion in the prompt."""
    if not messages:
        return ""
    parts = []
    for msg in messages[-6:]:  # Only last 6 messages to avoid token overflow
        role = "User" if msg.role == "user" else "Assistant"
        parts.append(f"{role}: {msg.content}")
    return "\n".join(parts)
