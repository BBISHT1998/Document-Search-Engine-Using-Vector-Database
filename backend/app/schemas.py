from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime


# ─── Auth Schemas ───────────────────────────────────────────────────────────

class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v):
        if not v.replace("_", "").isalnum():
            raise ValueError("Username must be alphanumeric (underscores allowed)")
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenData(BaseModel):
    user_id: Optional[int] = None
    role: Optional[str] = None


# ─── Document Schemas ────────────────────────────────────────────────────────

class DocumentResponse(BaseModel):
    id: int
    filename: str
    original_name: str
    file_type: str
    file_size: int
    status: str
    total_chunks: int
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse]
    total: int


# ─── Search Schemas ──────────────────────────────────────────────────────────

class SearchRequest(BaseModel):
    query: str
    limit: int = 5
    document_ids: Optional[List[int]] = None  # filter by specific docs

    @field_validator("query")
    @classmethod
    def query_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Query cannot be empty")
        return v.strip()


class SearchResult(BaseModel):
    chunk_id: str
    content: str
    document_name: str
    document_id: int
    page_number: Optional[int]
    similarity_score: float
    relevance_percent: int  # score as 0-100


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    total_results: int
    search_time_ms: float


# ─── RAG / Chat Schemas ──────────────────────────────────────────────────────

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class RAGRequest(BaseModel):
    question: str
    conversation_history: Optional[List[ChatMessage]] = []
    document_ids: Optional[List[int]] = None

    @field_validator("question")
    @classmethod
    def question_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Question cannot be empty")
        return v.strip()


class RAGSource(BaseModel):
    document_name: str
    document_id: int
    page_number: Optional[int]
    chunk_preview: str
    similarity_score: float


class RAGResponse(BaseModel):
    question: str
    answer: str
    sources: List[RAGSource]
    has_answer: bool
    response_time_ms: float


# ─── Stats Schemas ───────────────────────────────────────────────────────────

class StatsResponse(BaseModel):
    total_documents: int
    total_chunks: int
    total_queries: int
    avg_similarity_score: Optional[float]
