import uuid
import os
from typing import List, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from app.config import settings
from app.embeddings.embedder import embed_texts, embed_query

# [OK][OK][OK][OK][OK][OK][OK][OK][OK] Singleton ChromaDB client [OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK]
_chroma_client = None  # chromadb client instance
_collection = None     # chromadb collection instance


def get_chroma_client():
    """Returns the singleton ChromaDB persistent client."""
    global _chroma_client
    if _chroma_client is None:
        os.makedirs(settings.chroma_persist_dir, exist_ok=True)
        print(f"[VectorStore] Connecting to ChromaDB at: {settings.chroma_persist_dir}")
        _chroma_client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
        print("[VectorStore] ChromaDB connected [OK][OK][OK]")
    return _chroma_client


def get_collection():
    """Returns the ChromaDB collection (creates if not exists)."""
    global _collection
    if _collection is None:
        client = get_chroma_client()
        _collection = client.get_or_create_collection(
            name=settings.chroma_collection_name,
            metadata={"hnsw:space": "cosine"},  # Use cosine distance
        )
        print(f"[VectorStore] Collection '{settings.chroma_collection_name}' ready [OK][OK][OK]")
    return _collection


class VectorStore:
    """
    Abstraction layer over ChromaDB.

    Why ChromaDB?
    - Persistent (saves to disk, survives restarts)
    - Simple Python API
    - Built-in cosine similarity search
    - Stores embeddings + metadata together
    """

    def __init__(self):
        self.collection = get_collection()

    def add_chunks(
        self,
        chunks: List[dict],
        document_id: int,
        document_name: str,
    ) -> List[str]:
        """
        Embed chunks and add them to ChromaDB.

        Each chunk is stored with:
        - embedding vector (384 dimensions)
        - document text (for retrieval)
        - metadata: document_id, document_name, page_number, chunk_index

        Returns list of ChromaDB IDs assigned to each chunk.
        """
        if not chunks:
            return []

        # Extract texts for batch embedding
        texts = [c["text"] for c in chunks]

        # Generate unique IDs for each chunk
        chroma_ids = [f"doc{document_id}_chunk{i}_{uuid.uuid4().hex[:8]}" for i in range(len(chunks))]

        # Build metadata list
        metadatas = [
            {
                "document_id": document_id,
                "document_name": document_name,
                "page_number": c.get("page", 1),
                "chunk_index": c.get("chunk_index", i),
            }
            for i, c in enumerate(chunks)
        ]

        # Generate embeddings (batch for efficiency)
        print(f"[VectorStore] Embedding {len(texts)} chunks for document '{document_name}'...")
        embeddings = embed_texts(texts)

        # Upsert into ChromaDB
        self.collection.upsert(
            ids=chroma_ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
        )
        print(f"[VectorStore] Stored {len(chroma_ids)} chunks in ChromaDB [OK][OK][OK]")
        return chroma_ids

    def search(
        self,
        query: str,
        top_k: int = 5,
        document_ids: Optional[List[int]] = None,
        min_score: float = 0.0,
    ) -> List[dict]:
        """
        Semantic search: embed query [OK][OK][OK] find top-k similar chunks.

        Returns list of:
        {
            "chroma_id": str,
            "text": str,
            "document_id": int,
            "document_name": str,
            "page_number": int,
            "similarity_score": float,  (0 to 1, higher = more similar)
        }
        """
        # Embed the query
        query_embedding = embed_query(query)

        # Build filter if document_ids provided
        where_filter = None
        if document_ids:
            if len(document_ids) == 1:
                where_filter = {"document_id": {"$eq": document_ids[0]}}
            else:
                where_filter = {"document_id": {"$in": document_ids}}

        # Query ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, self.collection.count() or 1),
            where=where_filter,
            include=["documents", "metadatas", "distances"],
        )

        # Parse results
        hits = []
        if not results["ids"] or not results["ids"][0]:
            return hits

        for i, chroma_id in enumerate(results["ids"][0]):
            distance = results["distances"][0][i]
            # ChromaDB cosine = 1 - similarity, convert back
            similarity = 1.0 - distance
            similarity = max(0.0, min(1.0, similarity))

            if similarity < min_score:
                continue

            metadata = results["metadatas"][0][i]
            hits.append({
                "chroma_id": chroma_id,
                "text": results["documents"][0][i],
                "document_id": metadata.get("document_id", 0),
                "document_name": metadata.get("document_name", "Unknown"),
                "page_number": metadata.get("page_number", 1),
                "similarity_score": round(similarity, 4),
            })

        # Sort by similarity descending
        hits.sort(key=lambda x: x["similarity_score"], reverse=True)
        return hits

    def delete_chunks(self, chroma_ids: List[str]) -> None:
        """Remove chunks from ChromaDB by their IDs."""
        self.collection.delete(ids=chroma_ids)
        print(f"[VectorStore] Deleted {len(chroma_ids)} chunks from ChromaDB")

    def count(self) -> int:
        """Total number of chunks stored."""
        return self.collection.count()


# [OK][OK][OK][OK][OK][OK][OK][OK][OK] Global singleton [OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK]
_vector_store = None  # VectorStore instance


def get_vector_store() -> VectorStore:
    """Returns the singleton VectorStore instance."""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store
