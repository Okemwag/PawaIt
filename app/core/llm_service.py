"""
LLM service for integrating with various LLM providers.
Supports OpenAI (ChatGPT), Anthropic (Claude), Google (Gemini), and DeepSeek.
"""
import logging
from typing import Dict, Any, Optional
import httpx
from ..config import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMService:
    """Service for interacting with different LLM providers."""
    
    def __init__(self):
        """Initialize the LLM service with configuration from settings."""
        self.settings = get_settings()
        self.provider = self.settings.LLM_PROVIDER.lower()
        self.max_tokens = self.settings.MAX_TOKENS
        self.temperature = self.settings.TEMPERATURE
        
        # Create HTTP client for API requests
        self.client = httpx.AsyncClient(timeout=30.0)
        
        # Validate the selected provider
        valid_providers = ["chatgpt", "claude", "gemini", "deepseek"]
        if self.provider not in valid_providers:
            logger.warning(f"Invalid LLM provider: {self.provider}. Defaulting to claude.")
            self.provider = "claude"
    
    async def get_response(self, query: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get a response from the LLM based on the user's query.
        
        Args:
            query: The user's question or prompt
            conversation_id: Optional conversation ID for maintaining context
            
        Returns:
            Dictionary containing the response text and metadata
        """
        try:
            if self.provider == "chatgpt":
                return await self._get_chatgpt_response(query)
            elif self.provider == "gemini":
                return await self._get_gemini_response(query)
            elif self.provider == "deepseek":
                return await self._get_deepseek_response(query)
            else:
                # This should never happen due to validation in __init__
                logger.error(f"Unsupported LLM provider: {self.provider}")
                return {"response": "Error: Unsupported LLM provider", "tokens_used": 0}
                
        except Exception as e:
            logger.error(f"Error getting LLM response: {str(e)}")
            return {"response": "Error: Failed to get response from LLM service", "tokens_used": 0}
    
    async def _get_chatgpt_response(self, query: str) -> Dict[str, Any]:
        """Get response from OpenAI's ChatGPT."""
        if not self.settings.OPENAI_API_KEY:
            return {"response": "Error: OpenAI API key not configured", "tokens_used": 0}
        
        try:
            # Prepare the prompt with instructions for the specific use case
            system_prompt = """
            You are a helpful AI assistant providing accurate, detailed information.
            When answering questions, provide well-structured, factual responses.
            For travel-related questions, include visa requirements, necessary documentation,
            and relevant travel advisories when applicable.
            Format your responses clearly using markdown where appropriate.
            """
            
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                "max_tokens": self.max_tokens,
                "temperature": self.temperature
            }
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.settings.OPENAI_API_KEY}"
            }
            
            response = await self.client.post(
                "https://api.openai.com/v1/chat/completions",
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            result = response.json()
            
            return {
                "response": result["choices"][0]["message"]["content"].strip(),
                "tokens_used": result.get("usage", {}).get("total_tokens", 0)
            }
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error with OpenAI: {e.response.text}")
            return {"response": f"Error: OpenAI API returned status code {e.response.status_code}", "tokens_used": 0}
        except Exception as e:
            logger.error(f"Error with OpenAI API: {str(e)}")
            return {"response": "Error: Failed to get response from OpenAI", "tokens_used": 0}
    
    
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
                "response": response_text,
                "tokens_used": 0  # Gemini API doesn't provide token usage in the free tier
            }
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error with Gemini: {e.response.text}")
            return {"response": f"Error: Gemini API returned status code {e.response.status_code}", "tokens_used": 0}
        except Exception as e:
            logger.error(f"Error with Gemini API: {str(e)}")
            return {"response": "Error: Failed to get response from Gemini", "tokens_used": 0}
    
    async def _get_deepseek_response(self, query: str) -> Dict[str, Any]:
        """Get response from DeepSeek."""
        if not self.settings.DEEPSEEK_API_KEY:
            return {"response": "Error: DeepSeek API key not configured", "tokens_used": 0}
        
        try:
            # Prepare system prompt for DeepSeek
            system_prompt = """
            You are a helpful AI assistant providing accurate, detailed information.
            When answering questions, provide well-structured, factual responses.
            For travel-related questions, include visa requirements, necessary documentation,
            and relevant travel advisories when applicable.
            Format your responses clearly using markdown where appropriate.
            """
            
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                "temperature": self.temperature,
                "max_tokens": self.max_tokens
            }
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.settings.DEEPSEEK_API_KEY}"
            }
            
            response = await self.client.post(
                "https://api.deepseek.com/v1/chat/completions",
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            result = response.json()
            
            return {
                "response": result["choices"][0]["message"]["content"].strip(),
                "tokens_used": result.get("usage", {}).get("total_tokens", 0)
            }
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error with DeepSeek: {e.response.text}")
            return {"response": f"Error: DeepSeek API returned status code {e.response.status_code}", "tokens_used": 0}
        except Exception as e:
            logger.error(f"Error with DeepSeek API: {str(e)}")
            return {"response": "Error: Failed to get response from DeepSeek", "tokens_used": 0}
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()