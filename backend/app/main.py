import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.auth.router import router as auth_router
from app.documents.router import router as documents_router
from app.search.router import router as search_router
from app.rag.router import router as rag_router


# ─── Lifespan (startup / shutdown) ───────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Runs on startup:
    1. Creates SQLite tables
    2. Ensures data directories exist
    3. Warms up embedding model (loads into RAM once)
    4. Connects to ChromaDB
    """
    print("=" * 50)
    print(f"  {settings.app_name} v{settings.app_version}")
    print("=" * 50)

    # Create directories
    os.makedirs("./data/uploads", exist_ok=True)
    os.makedirs("./data/chroma_db", exist_ok=True)

    # Initialize SQLite tables
    print("[Startup] Initializing database...")
    init_db()
    print("[Startup] Database ready [OK]")

    # Warm up embedding model (loads ~90MB model into memory)
    print("[Startup] Loading embedding model (first run downloads ~90MB)...")
    from app.embeddings.embedder import get_embedder
    get_embedder()
    print("[Startup] Embedding model loaded [OK]")

    # Warm up ChromaDB
    print("[Startup] Connecting to ChromaDB...")
    from app.embeddings.vector_store import get_vector_store
    vs = get_vector_store()
    print(f"[Startup] ChromaDB ready - {vs.count()} chunks indexed [OK]")

    print("[Startup] All systems ready!")
    print("[Startup] API Docs: http://localhost:8000/docs")
    print("=" * 50)

    yield  # Server runs here

    print("[Shutdown] Graceful shutdown complete.")


# ─── FastAPI App ──────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Semantic Document Search Engine with RAG-powered Chatbot",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ─── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ──────────────────────────────────────────────────────────────────
app.include_router(auth_router,      prefix="/api/v1")
app.include_router(documents_router, prefix="/api/v1")
app.include_router(search_router,    prefix="/api/v1")
app.include_router(rag_router,       prefix="/api/v1")


# ─── Health Check ─────────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"])
def health_check():
    """Quick health check endpoint for monitoring and Docker health checks."""
    from app.embeddings.vector_store import get_vector_store
    vs = get_vector_store()
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
        "total_chunks_indexed": vs.count(),
    }


@app.get("/", tags=["Root"])
def root():
    return {
        "message": f"Welcome to {settings.app_name}",
        "docs": "/docs",
        "health": "/health",
    }
