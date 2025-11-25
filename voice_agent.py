"""
LiveKit Voice Agent for HVAC servicing with document context.
"""

import asyncio
import logging
from livekit import agents
from livekit.agents import (
    JobContext,
    WorkerOptions,
    cli,
    llm,
    AgentSession,
)
from livekit.plugins import openai

from document_processor import DocumentProcessor
from llm_service import LLMService

logger = logging.getLogger(__name__)


async def entrypoint(ctx: JobContext):
    """Entry point for the LiveKit agent job."""
    logger.info("Starting HVAC Voice Agent job")
    logger.info(f"Room: {ctx.room.name}, Room SID: {ctx.room.sid}")
    
    # Load documents FIRST - this is critical for the agent to have context
    logger.info("Loading HVAC manuals...")
    doc_processor = DocumentProcessor()
    document_text = doc_processor.load_documents(max_documents=2)
    
    if not document_text or len(document_text.strip()) == 0:
        logger.error("No documents found! Please add PDF files to the 'documents/' directory.")
        logger.warning("Agent will run without document context.")
        document_text = "No HVAC manuals are currently loaded. Please add PDF manuals to the documents/ directory."
    else:
        logger.info(f"Documents loaded successfully. Raw text length: {len(document_text)} characters")
    
    # Initialize LLM service
    llm_service = LLMService()
    available_tokens = llm_service.get_available_context_tokens()
    logger.info(f"Model context window: {available_tokens} tokens")
    
    # Truncate document text to fit context window (reserve space for conversation)
    if document_text and len(document_text.strip()) > 0:
        original_length = doc_processor.get_context_length(document_text)
        document_text = doc_processor.truncate_to_fit_context(
            document_text,
            max_tokens=available_tokens,
            reserved_tokens=4000  # Reserve tokens for system prompt, conversation history, and responses
        )
        final_length = doc_processor.get_context_length(document_text)
        logger.info(f"Document context: {final_length} tokens (was {original_length} tokens)")
        
        # Log a sample of the document to verify it loaded
        sample = document_text[:200] + "..." if len(document_text) > 200 else document_text
        logger.debug(f"Document sample: {sample}")
    
    # Create system prompt with document context
    system_prompt = llm_service.create_system_prompt(document_context=document_text)
    logger.info(f"System prompt created ({len(system_prompt)} characters)")
    
    def _log_conversation(event):
        item = getattr(event, "item", None)
        if not isinstance(item, llm.ChatMessage):
            return
        
        text = item.text_content
        if not text:
            return
        
        if item.role == "user":
            logger.info(f"👤 USER SAID: {text}")
        elif item.role == "assistant":
            logger.info(f"🤖 AGENT RESPONSE: {text}")
            logger.info(f"   Response length: {len(text)} characters")
            logger.info(f"   Response tokens (approx): {len(text) // 4}")
    
    hvac_agent = agents.Agent(
        instructions=system_prompt,
        stt=openai.STT(use_realtime=True),
        llm=openai.LLM(model=llm_service.model),
        tts=openai.TTS(voice="alloy"),
    )
    
    session = AgentSession()
    session.on("conversation_item_added", _log_conversation)
    
    logger.info("HVAC Voice Agent initialized with document context")
    logger.info("Agent is ready to answer questions using the loaded HVAC manuals")
    
    # Start the session - AgentSession will handle participant waiting
    await session.start(hvac_agent, room=ctx.room)
    logger.info("Voice agent started and listening")
    
    # Keep the agent running
    try:
        await asyncio.sleep(3600)  # Run for up to 1 hour (or until disconnected)
    except asyncio.CancelledError:
        logger.info("Agent session cancelled")
    finally:
        await session.aclose()
        logger.info("Agent session closed")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run the agent
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))