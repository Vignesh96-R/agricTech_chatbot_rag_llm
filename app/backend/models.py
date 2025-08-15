"""
Data models and schemas for the RBAC-Project application.

This module contains all Pydantic models used for request/response validation,
data transfer objects, and internal data structures.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from enum import Enum

class QueryType(str, Enum):
    """Enumeration of possible query types."""
    SQL = "SQL"
    RAG = "RAG"
    UNKNOWN = "UNKNOWN"

class ChatRequest(BaseModel):
    """Request model for chat queries."""
    question: str = Field(..., min_length=1, max_length=1000, description="The question to ask")
    
    @validator('question')
    def validate_question(cls, v):
        if not v.strip():
            raise ValueError('Question cannot be empty or whitespace only')
        return v.strip()

class ChatResponse(BaseModel):
    """Response model for chat queries."""
    user: str = Field(..., description="Username of the user")
    role: str = Field(..., description="Role of the user")
    mode: str = Field(..., description="Query mode used (SQL/RAG)")
    fallback: bool = Field(False, description="Whether fallback was used")
    answer: str = Field(..., description="The answer to the question")
    sql: Optional[str] = Field(None, description="SQL query if applicable")
    error: Optional[str] = Field(None, description="Error message if any")

class UserInfo(BaseModel):
    """Model for user information."""
    username: str = Field(..., description="Username")
    role: str = Field(..., description="User role")
    password_hash: str = Field(..., description="Hashed password")

class DocumentInfo(BaseModel):
    """Model for document information."""
    filename: str = Field(..., description="Name of the document")
    role: str = Field(..., description="Role that can access this document")
    filepath: str = Field(..., description="Path to the document")
    file_type: str = Field(..., description="Type/extension of the document")
    size: Optional[int] = Field(None, description="File size in bytes")
    uploaded_at: Optional[str] = Field(None, description="Upload timestamp")
    source: Optional[str] = Field(None, description="Source of the document (resources_2 or uploads)")

class UploadResponse(BaseModel):
    """Response model for document uploads."""
    message: str = Field(..., description="Upload status message")
    filename: str = Field(..., description="Name of uploaded file")
    role: str = Field(..., description="Role assigned to the document")
    filepath: str = Field(..., description="Path where file was saved")

class RoleInfo(BaseModel):
    """Model for role information."""
    name: str = Field(..., description="Role name")
    description: Optional[str] = Field(None, description="Role description")
    permissions: List[str] = Field(default_factory=list, description="List of permissions")

class LoginResponse(BaseModel):
    """Response model for login attempts."""
    message: str = Field(..., description="Login status message")
    role: str = Field(..., description="User's role")
    username: str = Field(..., description="Username")

class AvailableDocsResponse(BaseModel):
    """Response model for available documents."""
    documents: List[DocumentInfo] = Field(..., description="List of available documents")
    user_role: str = Field(..., description="Current user's role")
    allowed_roles: List[str] = Field(..., description="Roles the user can access")

class SQLQueryResult(BaseModel):
    """Model for SQL query results."""
    answer: str = Field(..., description="Formatted answer")
    sql: Optional[str] = Field(None, description="SQL query used")
    error: Optional[bool] = Field(False, description="Whether an error occurred")
    columns: Optional[List[str]] = Field(None, description="Column names")
    data: Optional[List[List[Any]]] = Field(None, description="Query result data")

class RAGQueryResult(BaseModel):
    """Model for RAG query results."""
    answer: str = Field(..., description="Generated answer")
    sources: Optional[List[str]] = Field(None, description="Source documents used")
    confidence: Optional[float] = Field(None, description="Confidence score")

class HealthCheck(BaseModel):
    """Model for health check responses."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Application version")
    timestamp: str = Field(..., description="Current timestamp")
