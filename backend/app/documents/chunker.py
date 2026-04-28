from typing import List
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter


# ─── Chunker Configuration ───────────────────────────────────────────────────
# chunk_size:    max characters per chunk (~125 words)  — smaller = more precise
# chunk_overlap: characters shared between adjacent chunks
#                (preserves context at chunk boundaries)
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100


splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    # Split priority: paragraph → sentence → word → character
    separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""],
    length_function=len,
)


def split_into_chunks(pages: List[dict]) -> List[dict]:
    """
    Split extracted page texts into smaller overlapping chunks.

    Input:  [{"page": 1, "text": "...long text..."}, ...]
    Output: [{"chunk_index": 0, "page": 1, "text": "...chunk..."}, ...]

    Why we chunk:
    - Embedding models have token limits (~512 tokens)
    - Smaller chunks = more precise retrieval
    - Overlap ensures context isn't lost at boundaries
    """
    chunks = []
    chunk_index = 0

    for page_data in pages:
        page_num = page_data["page"]
        text = page_data["text"].strip()

        if not text:
            continue

        # Split this page's text into overlapping chunks
        page_chunks = splitter.split_text(text)

        for chunk_text in page_chunks:
            chunk_text = chunk_text.strip()
            if len(chunk_text) < 50:  # skip very short chunks (e.g., headers only)
                continue
            chunks.append({
                "chunk_index": chunk_index,
                "page": page_num,
                "text": chunk_text,
            })
            chunk_index += 1

    return chunks


def estimate_tokens(text: str) -> int:
    """Rough token count estimate (1 token ≈ 4 chars)."""
    return len(text) // 4
