"""
Helper utilities for the application.
"""
import re
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def sanitize_input(text: str) -> str:
    """
    Sanitize user input to prevent potential issues.
    
    Args:
        text: The input text to sanitize
        
    Returns:
        Sanitized text
    """
    # Remove any script tags or potentially harmful HTML
    text = re.sub(r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>', '', text)
    
    # Trim whitespace
    text = text.strip()
    
    return text

def format_response_markdown(response: str) -> str:
    """
    Ensure response is properly formatted with markdown.
    
    Args:
        response: Raw response from LLM
        
    Returns:
        Properly formatted response
    """
    # Ensure headers have space after #
    response = re.sub(r'(#{1,6})([^ #])', r'\1 \2', response)
    
    # Ensure code blocks have proper syntax
    if "```" in response and not re.search(r'```[a-zA-Z0-9]*\n', response):
        response = response.replace("```", "```text")
    
    return response

def extract_travel_details(response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract structured travel details from an LLM response.
    Useful for travel-related queries to organize information better.
    
    Args:
        response: The LLM response dictionary
        
    Returns:
        Dictionary with structured travel information
    """
    text = response.get("response", "")
    structured_info = {
        "visa_requirements": [],
        "passport_requirements": [],
        "additional_documents": [],
        "travel_advisories": []
    }
    
    # Simple pattern matching to extract information
    # This is basic - could be enhanced with more sophisticated NLP
    
    # Visa requirements
    visa_section = re.search(r'(?:visa|visas).*?(?=\n\n|\n#|\Z)', text, re.IGNORECASE | re.DOTALL)
    if visa_section:
        visa_text = visa_section.group(0)
        # Extract bullet points or numbered items
        visa_items = re.findall(r'(?:\*|\-|\d+\.)\s+(.*?)(?=\n\*|\n\-|\n\d+\.|\Z)', visa_text, re.DOTALL)
        if visa_items:
            structured_info["visa_requirements"] = [item.strip() for item in visa_items]
    
    # Passport requirements
    passport_section = re.search(r'passport.*?(?=\n\n|\n#|\Z)', text, re.IGNORECASE | re.DOTALL)
    if passport_section:
        passport_text = passport_section.group(0)
        passport_items = re.findall(r'(?:\*|\-|\d+\.)\s+(.*?)(?=\n\*|\n\-|\n\d+\.|\Z)', passport_text, re.DOTALL)
        if passport_items:
            structured_info["passport_requirements"] = [item.strip() for item in passport_items]
    
    # Additional documents
    docs_section = re.search(r'(?:document|documents|additional).*?(?=\n\n|\n#|\Z)', text, re.IGNORECASE | re.DOTALL)
    if docs_section:
        docs_text = docs_section.group(0)
        docs_items = re.findall(r'(?:\*|\-|\d+\.)\s+(.*?)(?=\n\*|\n\-|\n\d+\.|\Z)', docs_text, re.DOTALL)
        if docs_items:
            structured_info["additional_documents"] = [item.strip() for item in docs_items]
    
    # Travel advisories
    advisory_section = re.search(r'(?:advisory|advisories|warning).*?(?=\n\n|\n#|\Z)', text, re.IGNORECASE | re.DOTALL)
    if advisory_section:
        advisory_text = advisory_section.group(0)
        advisory_items = re.findall(r'(?:\*|\-|\d+\.)\s+(.*?)(?=\n\*|\n\-|\n\d+\.|\Z)', advisory_text, re.DOTALL)
        if advisory_items:
            structured_info["travel_advisories"] = [item.strip() for item in advisory_items]
    
    return structured_info