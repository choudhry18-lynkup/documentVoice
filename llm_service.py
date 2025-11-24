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
        return f"""You are an expert HVAC (Heating, Ventilation, and Air Conditioning) service assistant. 
Your role is to help technicians diagnose, repair, and maintain HVAC systems.

You have access to the following HVAC service manuals and documentation:

{document_context}

Instructions:
- Use the information from the manuals to provide accurate, step-by-step guidance
- When referencing specific procedures, mention which manual or section you're referring to
- If information isn't in the provided manuals, say so clearly
- Provide clear, actionable instructions suitable for field technicians
- Prioritize safety warnings and precautions
- Use technical terminology appropriately but explain when necessary
- If asked about something not covered in the manuals, provide general HVAC knowledge but note the limitation

Respond in a conversational, helpful manner as if you're a knowledgeable colleague assisting in the field."""
    
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

