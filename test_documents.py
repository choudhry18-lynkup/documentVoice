"""
Test script to verify document processing works correctly.
Run this before starting the voice agent to ensure documents are loaded properly.
"""

import os
import logging
from dotenv import load_dotenv
from document_processor import DocumentProcessor
from llm_service import LLMService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Test document loading and processing."""
    load_dotenv()
    
    logger.info("Testing document processor...")
    
    # Initialize document processor
    doc_processor = DocumentProcessor()
    
    # Load documents
    document_text = doc_processor.load_documents(max_documents=2)
    
    if not document_text:
        logger.error("No documents found! Please add PDF files to the 'documents/' directory.")
        return
    
    # Get document info
    token_count = doc_processor.get_context_length(document_text)
    logger.info(f"Loaded documents: {len(document_text)} characters")
    logger.info(f"Approximate tokens: {token_count}")
    
    # Initialize LLM service to check context window
    try:
        llm_service = LLMService()
        available_tokens = llm_service.get_available_context_tokens()
        logger.info(f"Model: {llm_service.model}")
        logger.info(f"Available context window: {available_tokens} tokens")
        
        # Truncate if needed
        truncated = doc_processor.truncate_to_fit_context(
            document_text,
            max_tokens=available_tokens,
            reserved_tokens=3000
        )
        
        final_tokens = doc_processor.get_context_length(truncated)
        logger.info(f"Final document tokens (after truncation): {final_tokens}")
        
        if len(truncated) < len(document_text):
            logger.warning("Documents were truncated to fit context window")
        else:
            logger.info("Documents fit within context window")
        
        # Show a sample of the document text
        logger.info("\n" + "="*80)
        logger.info("Sample of document content (first 500 chars):")
        logger.info("="*80)
        logger.info(truncated[:500] + "...")
        
    except Exception as e:
        logger.error(f"Error initializing LLM service: {e}")
        logger.error("Make sure OPENAI_API_KEY is set in your .env file")


if __name__ == "__main__":
    main()

