"""
LLM service for integrating with Google's Gemini.
"""
import logging
from typing import Dict, Any, Optional
import httpx
from ..config import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMService:
    """Service for interacting with Google's Gemini."""
    
    def __init__(self):
        """Initialize the LLM service with configuration from settings."""
        self.settings = get_settings()
        self.max_tokens = self.settings.MAX_TOKENS
        self.temperature = self.settings.TEMPERATURE
        
        # Create HTTP client for API requests
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def get_response(self, query: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get a response from Gemini based on the user's query.
        
        Args:
            query: The user's question or prompt
            conversation_id: Optional conversation ID for maintaining context
            
        Returns:
            Dictionary containing the response text and metadata
        """
        try:
            return await self._get_gemini_response(query)
        except Exception as e:
            logger.error(f"Error getting Gemini response: {str(e)}")
            return {"response": "Error: Failed to get response from Gemini", "tokens_used": 0}
    
    async def _get_gemini_response(self, query: str) -> Dict[str, Any]:
        """Get response from Google's Gemini."""
        if not self.settings.GOOGLE_API_KEY:
            return {"response": "Error: Google API key not configured", "tokens_used": 0}
        
        try:
            # Prepare the prompt for Gemini
            prompt = f"""
            You are a helpful AI assistant providing accurate, detailed information.
            When answering questions, provide well-structured, factual responses.
            For travel-related questions, include visa requirements, necessary documentation,
            and relevant travel advisories when applicable.
            Format your responses clearly using markdown where appropriate.
            
            User query: {query}
            """
            
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": self.temperature,
                    "maxOutputTokens": self.max_tokens,
                    "topP": 0.8,
                    "topK": 40
                }
            }
            
            response = await self.client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.settings.GOOGLE_API_KEY}",
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            
            # Extract the response text
            response_text = result["candidates"][0]["content"]["parts"][0]["text"].strip()
            
            return {
                "response": response_text
            }
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error with Gemini: {e.response.text}")
            return {"response": f"Error: Gemini API returned status code {e.response.status_code}", "tokens_used": 0}
        except Exception as e:
            logger.error(f"Error with Gemini API: {str(e)}")
            return {"response": "Error: Failed to get response from Gemini", "tokens_used": 0}
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()