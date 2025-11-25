"""
LLM Service for handling OpenAI API interactions with document context.
"""

import os
from typing import Optional
from openai import OpenAI
import logging

logger = logging.getLogger(__name__)


class LLMService:
    """Service for interacting with OpenAI LLM with document context."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o",
        max_tokens: int = 4096
    ):
        """
        Initialize the LLM service.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: OpenAI model to use (default: gpt-4o)
            max_tokens: Maximum tokens for the model context window
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        self.model = model
        self.max_tokens = max_tokens
        self.client = OpenAI(api_key=self.api_key)
        
        # Model context window sizes (approximate)
        self.context_windows = {
            "gpt-4o": 128000,
            "gpt-4-turbo": 128000,
            "gpt-4": 8192,
            "gpt-3.5-turbo": 16385,
        }
        
        self.available_context = self.context_windows.get(
            model, 
            128000  # Default to large context window
        )
        
        logger.info(f"Initialized LLM service with model: {model} (context: {self.available_context} tokens)")
    
    def create_system_prompt(self, document_context: str) -> str:
        """
        Create system prompt with document context for HVAC servicing.
        
        Args:
            document_context: Text from HVAC manuals
            
        Returns:
            System prompt string
        """
        # Check if documents were actually loaded
        if not document_context or "No HVAC manuals" in document_context:
            return """You are an expert HVAC (Heating, Ventilation, and Air Conditioning) service assistant. 
Your role is to help technicians diagnose, repair, and maintain HVAC systems.

IMPORTANT: No HVAC manuals are currently loaded. Please inform the user that manuals need to be added to the documents/ directory.

Provide general HVAC knowledge and guidance, but always mention that specific procedures should be verified against the equipment's service manual."""
        
        return f"""You are an expert HVAC (Heating, Ventilation, and Air Conditioning) service assistant. 
Your role is to help technicians diagnose, repair, and maintain HVAC systems.

You have access to the following HVAC service manuals and documentation. Use this information to provide accurate, detailed guidance:

{document_context}

CRITICAL INSTRUCTIONS:
1. ALWAYS reference the specific manual or section when providing information from the documents above
2. Use exact procedures, specifications, and safety warnings from the manuals
3. If the user asks about something not in the provided manuals, say: "That information is not in the loaded manuals. Please consult the equipment's service manual."
4. Prioritize safety warnings and precautions from the manuals
5. Provide step-by-step instructions exactly as described in the manuals
6. Use technical terminology from the manuals, but explain when necessary
7. When referencing procedures, mention the manual name (e.g., "According to [manual name]...")

Respond in a clear, professional manner suitable for field technicians. Be specific and reference the documentation when possible."""
    
    async def generate_response(
        self,
        user_message: str,
        document_context: str,
        conversation_history: Optional[list] = None
    ) -> str:
        """
        Generate a response using OpenAI API with document context.
        
        Args:
            user_message: User's question or message
            document_context: Text from HVAC manuals
            conversation_history: Previous conversation messages (optional)
            
        Returns:
            Generated response text
        """
        try:
            system_prompt = self.create_system_prompt(document_context)
            
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            # Add conversation history if provided
            if conversation_history:
                messages.extend(conversation_history)
            
            # Add current user message
            messages.append({"role": "user", "content": user_message})
            
            logger.debug(f"Calling OpenAI API with model: {self.model}")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000,  # Response length limit
            )
            
            assistant_message = response.choices[0].message.content
            logger.debug(f"Received response from OpenAI ({len(assistant_message)} chars)")
            
            return assistant_message
            
        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            return "I apologize, but I encountered an error processing your request. Please try again."
    
    def get_available_context_tokens(self) -> int:
        """Get the available context window size for the current model."""
        return self.available_context

