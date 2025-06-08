"""
Semantic SnipRAG Engine - Uses horizontal block chunking with PyMuPDF text extraction.
"""

from typing import List, Dict, Any, Optional, Tuple
import fitz
import io
from PIL import Image
from langchain.docstore.document import Document

from .base_engine import BaseSnipRAGEngine, logger

class SemanticSnipRAGEngine(BaseSnipRAGEngine):
    """
    SnipRAG Engine that uses horizontal blocks with semantic chunking.
    This implementation divides pages into horizontal blocks and extracts
    text using PyMuPDF's built-in text extraction.
    """
    
    def __init__(self, num_blocks: int = 20, block_overlap: float = 0.2, **kwargs):
        """
        Initialize the Semantic SnipRAG Engine.
        
        Args:
            num_blocks: Number of horizontal blocks per page
            block_overlap: Overlap between blocks as a fraction (0.0-1.0)
            **kwargs: Additional arguments to pass to the base class
        """
        super().__init__(**kwargs)
        self.num_blocks = num_blocks
        self.block_overlap = block_overlap
    
    def _extract_text_chunks(self, pdf_path: str, document_id: str) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Extract text chunks from a PDF with metadata using horizontal block chunking.
        
        Args:
            pdf_path: Path to the PDF file
            document_id: Unique identifier for the document
            
        Returns:
            List of tuples (text_chunk, metadata)
        """
        result = []
        
        # Open the PDF
        doc = fitz.open(pdf_path)
        
        # Process each page
        for page_idx in range(len(doc)):
            page = doc[page_idx]
            
            # Store key for this page
            page_key = f"{document_id}_{page_idx}"
            
            # Render the page to an image at 300 DPI and store it
            pix = page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72))
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))
            self.page_images[page_key] = img_data
            
            # Get page dimensions
            page_rect = page.rect
            page_width = page_rect.width
            page_height = page_rect.height
            
            # Calculate block height (1/num_blocks of page height)
            block_height = page_height / self.num_blocks
            overlap = block_height * self.block_overlap  # Overlap between blocks
            
            # Extract whole page text
            page_text = page.get_text()
            
            # Create horizontal blocks with overlap
            for block_idx in range(self.num_blocks):
                # Calculate block coordinates
                y0 = block_idx * block_height - overlap if block_idx > 0 else 0
                y1 = (block_idx + 1) * block_height if block_idx < self.num_blocks - 1 else page_height
                
                if y0 >= page_height:
                    break
                    
                if y1 > page_height:
                    y1 = page_height
                
                # Define block rectangle
                block_rect = fitz.Rect(0, y0, page_width, y1)
                
                # Extract text from this region
                block_text = page.get_text("text", clip=block_rect)
                
                if not block_text.strip():
                    continue
                
                # Coordinates in format expected by the rest of the code (x0, y0, x1, y1)
                coordinates = [0, y0, page_width, y1]
                
                # Scale coordinates to match the rendered image resolution
                scale_factor = 300/72
                scaled_coords = [c * scale_factor for c in coordinates]
                
                # Create metadata
                metadata = {
                    "document_id": document_id,
                    "page_number": page_idx,
                    "source": "semantic_blocks",
                    "block_index": block_idx,
                    "coordinates": scaled_coords
                }
                
                # Create a document for langchain
                langchain_doc = Document(
                    page_content=block_text,
                    metadata=metadata
                )
                
                # Split the text into chunks
                chunks = self.text_splitter.split_documents([langchain_doc])
                
                # Add each chunk with its metadata
                for chunk in chunks:
                    result.append((chunk.page_content, chunk.metadata))
        
        # Close the document
        doc.close()
        
        return result 