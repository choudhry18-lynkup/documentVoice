"""
LiveKit Voice Agent for HVAC servicing with document context.
"""

import asyncio
import logging
from typing import Annotated
from livekit import agents, rtc
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    WorkerOptions,
    cli,
    llm,
)
from livekit.agents.pipeline import VoicePipelineAgent
from livekit.plugins import openai

from document_processor import DocumentProcessor
from llm_service import LLMService

logger = logging.getLogger(__name__)


class HVACVoiceAgent(VoicePipelineAgent):
    """Voice agent for HVAC servicing with document context."""
    
    def __init__(
        self,
        *,
        ctx: JobContext,
        document_context: str,
        llm_service: LLMService,
    ):
        """
        Initialize the HVAC voice agent.
        
        Args:
            ctx: LiveKit job context
            document_context: Text from HVAC manuals
            llm_service: LLM service instance
        """
        self.llm_service = llm_service
        self.document_context = document_context
        
        # Create system prompt with document context
        system_prompt = llm_service.create_system_prompt(document_context)
        
        # Initialize voice pipeline with OpenAI STT, LLM, and TTS
        # The built-in OpenAI LLM will use the system prompt with document context
        super().__init__(
            vad=agents.VAD.load(sample_rate=16000),
            stt=openai.STT(),
            llm=openai.LLM(
                model=llm_service.model,
                # The chat_ctx will provide the system prompt with documents
            ),
            tts=openai.TTS(voice="alloy"),
            chat_ctx=llm.ChatContext().append(
                role="system",
                text=system_prompt,
            ),
        )
        
        logger.info("HVAC Voice Agent initialized")


async def entrypoint(ctx: JobContext):
    """Entry point for the LiveKit agent job."""
    logger.info("Starting HVAC Voice Agent job")
    
    # Wait for participant to connect
    await ctx.wait_for_participant()
    logger.info("Participant connected")
    
    # Initialize document processor and load documents
    doc_processor = DocumentProcessor()
    document_text = doc_processor.load_documents(max_documents=2)
    
    if not document_text:
        logger.warning("No documents loaded. Agent will run without document context.")
        document_text = "No HVAC manuals are currently loaded."
    
    # Truncate document text to fit context window
    llm_service = LLMService()
    available_tokens = llm_service.get_available_context_tokens()
    document_text = doc_processor.truncate_to_fit_context(
        document_text,
        max_tokens=available_tokens,
        reserved_tokens=3000  # Reserve tokens for system prompt, conversation, and response
    )
    
    logger.info(f"Loaded document context ({doc_processor.get_context_length(document_text)} tokens)")
    
    # Initialize and start the voice agent
    agent = HVACVoiceAgent(
        ctx=ctx,
        document_context=document_text,
        llm_service=llm_service,
    )
    
    agent.start(ctx.room)
    logger.info("Voice agent started")
    
    # Keep the agent running
    await asyncio.sleep(1)  # Give agent time to initialize


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run the agent
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
