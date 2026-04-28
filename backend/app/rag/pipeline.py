import time
from google import genai
from google.genai import types
from typing import List, Optional
from app.config import settings
from app.search.retriever import semantic_search
from app.rag.prompts import (
    RAG_SYSTEM_PROMPT,
    RAG_USER_TEMPLATE,
    CHAT_HISTORY_TEMPLATE,
    format_context_block,
    format_conversation_history,
)

# Configure Gemini client (new SDK)
_client = None


def get_gemini_client():
    """Returns the singleton Gemini client."""
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.gemini_api_key)
        print(f"[RAG] Gemini client initialized with model '{settings.gemini_model}' [OK]")
    return _client


def _call_gemini_with_retry(prompt: str, max_retries: int = 3) -> str:
    """
    Call Gemini with exponential backoff on 429 rate-limit errors.

    Retry schedule: 5s -> 10s -> 20s
    Returns the answer string, or a user-friendly error message.
    """
    client = get_gemini_client()
    wait_seconds = 5

    for attempt in range(1, max_retries + 1):
        try:
            response = client.models.generate_content(
                model=settings.gemini_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=RAG_SYSTEM_PROMPT,
                    temperature=0.2,
                    max_output_tokens=1024,
                ),
            )
            return response.text.strip() if response.text else "No response generated."

        except Exception as e:
            error_str = str(e)

            # 429 rate-limit: wait and retry with exponential backoff
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                if attempt < max_retries:
                    print(
                        f"[RAG] Rate limit hit (attempt {attempt}/{max_retries}). "
                        f"Retrying in {wait_seconds}s..."
                    )
                    time.sleep(wait_seconds)
                    wait_seconds *= 2  # exponential backoff: 5s -> 10s -> 20s
                    continue
                else:
                    # All retries exhausted — return a friendly message
                    return (
                        "The AI service is temporarily rate-limited due to free tier usage limits. "
                        "Please wait 1-2 minutes and try again. "
                        "If this persists, consider upgrading your Gemini API plan at "
                        "https://ai.google.dev/gemini-api/docs/rate-limits"
                    )

            # Any other error — log and surface clearly (not raw stack trace)
            print(f"[RAG] Gemini error on attempt {attempt}: {error_str}")
            return f"An error occurred while generating a response. Please try again. (Detail: {error_str[:200]})"

    return "No response generated."


def run_rag_pipeline(
    question: str,
    conversation_history: Optional[List] = None,
    document_ids: Optional[List[int]] = None,
) -> dict:
    """
    Full RAG pipeline:
    1. Retrieve relevant chunks from ChromaDB
    2. Check similarity threshold (avoid hallucination on irrelevant queries)
    3. Format context into a prompt
    4. Send to Gemini (with retry) and get grounded answer
    5. Return answer + sources
    """
    start_time = time.time()

    # Step 1: Retrieve relevant chunks
    search_result = semantic_search(
        query=question,
        top_k=settings.top_k_results,
        document_ids=document_ids,
    )
    chunks = search_result["results"]

    # Step 2: Threshold check — avoid sending empty context to the LLM
    if not chunks:
        elapsed = round((time.time() - start_time) * 1000, 2)
        return {
            "answer": (
                "I couldn't find relevant information in the uploaded documents to answer this question. "
                "Please try rephrasing or upload documents related to your topic."
            ),
            "sources": [],
            "has_answer": False,
            "response_time_ms": elapsed,
        }

    # Step 3: Format context block
    context_text = format_context_block(chunks)

    # Step 4: Build the prompt
    if conversation_history:
        history_text = format_conversation_history(conversation_history)
        prompt = CHAT_HISTORY_TEMPLATE.format(
            history=history_text,
            context=context_text,
            question=question,
        )
    else:
        prompt = RAG_USER_TEMPLATE.format(
            context=context_text,
            question=question,
        )

    # Step 5: Call Gemini with automatic retry on rate-limit errors
    answer = _call_gemini_with_retry(prompt)

    # Step 6: Build sources list (top 3 chunks)
    sources = [
        {
            "document_name": chunk["document_name"],
            "document_id": chunk["document_id"],
            "page_number": chunk.get("page_number"),
            "chunk_preview": chunk["text"][:200] + "..." if len(chunk["text"]) > 200 else chunk["text"],
            "similarity_score": chunk["similarity_score"],
        }
        for chunk in chunks[:3]
    ]

    elapsed = round((time.time() - start_time) * 1000, 2)

    return {
        "answer": answer,
        "sources": sources,
        "has_answer": True,
        "response_time_ms": elapsed,
    }
