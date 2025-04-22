"""
API routes for handling user queries and LLM responses.
"""
import logging
import uuid
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from datetime import datetime

from app.models.query import QueryRequest, QueryResponse, ErrorResponse
from app.core.llm_service import LLMService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create API router
router = APIRouter(
    prefix="/queries",
    tags=["queries"],
    responses={404: {"model": ErrorResponse}},
)

# In-memory storage for query history (replace with database in production)
query_history = {}


async def get_llm_service():
    """Dependency to get LLM service instance."""
    service = LLMService()
    try:
        yield service
    finally:
        await service.close()


@router.post("/", response_model=QueryResponse, status_code=200)
async def create_query(
    query_request: QueryRequest, 
    background_tasks: BackgroundTasks,
    llm_service: LLMService = Depends(get_llm_service)
):
    """
    Create a new query and get a response from the LLM.
    
    Args:
        query_request: The query request containing the user's question
        background_tasks: FastAPI background tasks
        llm_service: LLM service instance
        
    Returns:
        QueryResponse: The LLM's response to the user's query
    """
    try:
        logger.info(f"Received query: {query_request.query}")
        
        # Generate a conversation ID if not provided
        conversation_id = query_request.conversation_id or str(uuid.uuid4())
        
        # Get response from LLM service
        llm_response = await llm_service.get_response(
            query_request.query,
            conversation_id
        )
        
        # Create response object
        response = QueryResponse(
            query=query_request.query,
            response=llm_response["response"],
            conversation_id=conversation_id,
            timestamp=datetime.now(),
            tokens_used=llm_response.get("tokens_used", 0)
        )
        
        # Store in query history (in background to avoid blocking)
        background_tasks.add_task(
            store_query_history,
            conversation_id,
            response
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process query: {str(e)}"
        )


@router.get("/history/{conversation_id}", status_code=200)
async def get_query_history(conversation_id: str):
    """
    Get the query history for a specific conversation.
    
    Args:
        conversation_id: The ID of the conversation
        
    Returns:
        List of QueryResponse objects for the conversation
    """
    if conversation_id not in query_history:
        return JSONResponse(
            status_code=404,
            content={"error": f"No history found for conversation ID: {conversation_id}"}
        )
    
    return query_history[conversation_id]


def store_query_history(conversation_id: str, response: QueryResponse):
    """
    Store query response in the query history.
    
    Args:
        conversation_id: The ID of the conversation
        response: The query response to store
    """
    if conversation_id not in query_history:
        query_history[conversation_id] = []
    
    query_history[conversation_id].append(response)
    
    # Limit history to last 20 queries per conversation
    query_history[conversation_id] = query_history[conversation_id][-20:]