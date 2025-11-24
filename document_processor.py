"""
Document Processor for extracting text from PDF HVAC manuals.
Handles PDF text extraction and prepares content for LLM context window.
"""

import os
from pathlib import Path
from typing import List, Optional
import PyPDF2
import logging

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Processes PDF documents and extracts text for LLM context."""
    
    def __init__(self, documents_dir: str = "./documents"):
        """
        Initialize the document processor.
        
        Args:
            documents_dir: Directory containing PDF documents
        """
        self.documents_dir = Path(documents_dir)
        self.documents_dir.mkdir(exist_ok=True)
        self._cached_texts = {}
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract all text from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text content
        """
        if pdf_path in self._cached_texts:
            return self._cached_texts[pdf_path]
        
        try:
            text_content = []
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                
                logger.info(f"Extracting text from {pdf_path} ({num_pages} pages)")
                
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    try:
                        text = page.extract_text()
                        if text.strip():
                            text_content.append(text)
                    except Exception as e:
                        logger.warning(f"Error extracting page {page_num}: {e}")
                        continue
            
            full_text = "\n\n".join(text_content)
            self._cached_texts[pdf_path] = full_text
            return full_text
            
        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path}: {e}")
            raise
    
    def load_documents(self, max_documents: int = 2) -> str:
        """
        Load and combine text from PDF documents in the documents directory.
        
        Args:
            max_documents: Maximum number of documents to load (default: 2)
            
        Returns:
            Combined text from all documents
        """
        pdf_files = list(self.documents_dir.glob("*.pdf"))
        
        if not pdf_files:
            logger.warning(f"No PDF files found in {self.documents_dir}")
            return ""
        
        # Sort by modification time (newest first) and take up to max_documents
        pdf_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        pdf_files = pdf_files[:max_documents]
        
        combined_texts = []
        
        for pdf_file in pdf_files:
            logger.info(f"Loading document: {pdf_file.name}")
            try:
                text = self.extract_text_from_pdf(str(pdf_file))
                combined_texts.append(f"=== {pdf_file.name} ===\n{text}")
            except Exception as e:
                logger.error(f"Failed to load {pdf_file.name}: {e}")
                continue
        
        return "\n\n" + "="*80 + "\n\n".join(combined_texts)
    
    def get_context_length(self, text: str) -> int:
        """Get approximate token count (rough estimate: 1 token ≈ 4 characters)."""
        return len(text) // 4
    
    def truncate_to_fit_context(
        self, 
        text: str, 
        max_tokens: int, 
        reserved_tokens: int = 2000
    ) -> str:
        """
        Truncate text to fit within context window.
        
        Args:
            text: Text to truncate
            max_tokens: Maximum tokens for the model
            reserved_tokens: Tokens to reserve for prompt and response
            
        Returns:
            Truncated text
        """
        available_tokens = max_tokens - reserved_tokens
        current_tokens = self.get_context_length(text)
        
        if current_tokens <= available_tokens:
            return text
        
        # Truncate to fit
        max_chars = available_tokens * 4
        truncated = text[:max_chars]
        
        # Try to cut at a sentence boundary
        last_period = truncated.rfind('.')
        if last_period > max_chars * 0.9:  # If we can cut near a sentence
            truncated = truncated[:last_period + 1]
        
        logger.warning(
            f"Document text truncated from {current_tokens} to "
            f"{self.get_context_length(truncated)} tokens"
        )
        
        return truncated

