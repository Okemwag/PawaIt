"""
Pydantic models for query requests and responses.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class QueryRequest(BaseModel):
    """Model for incoming query requests."""

    query: str = Field(
        ..., description="The question or query from the user", min_length=1
    )
    user_id: Optional[str] = Field(
        None, description="Optional user identifier for tracking conversations"
    )
    conversation_id: Optional[str] = Field(
        None, description="Optional conversation identifier for maintaining context"
    )

    class Config:
        schema_extra = {
            "example": {
                "query": "What documents do I need to travel from Kenya to Ireland?",
                "user_id": "user123",
                "conversation_id": "conv456",
            }
        }


class QueryResponse(BaseModel):
    """Model for outgoing query responses."""

    response: str = Field(..., description="The response from the LLM")
    query: str = Field(..., description="The original query")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="The timestamp of the response"
    )
    conversation_id: Optional[str] = Field(None, description="Conversation identifier")
    tokens_used: Optional[int] = Field(
        None, description="Number of tokens used for this query"
    )

    class Config:
        schema_extra = {
            "example": {
                "response": "To travel from Kenya to Ireland, you need the following documents:\n\n1. A valid passport with at least 6 months validity...",
                "query": "What documents do I need to travel from Kenya to Ireland?",
                "timestamp": "2023-04-21T12:34:56.789Z",
                "conversation_id": "conv456",
                "tokens_used": 250,
            }
        }


class ErrorResponse(BaseModel):
    """Model for error responses."""

    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")

    class Config:
        schema_extra = {
            "example": {
                "error": "Failed to process query",
                "detail": "LLM service unavailable",
            }
        }


class QueryHistory(BaseModel):
    """Model for query history."""

    queries: List[QueryResponse] = Field(
        default_factory=list, description="List of previous queries and responses"
    )
