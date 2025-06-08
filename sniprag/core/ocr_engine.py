"""
OCR-based SnipRAG Engine - Uses OCR on horizontal slices for text extraction.
"""

import base64
from typing import List, Dict, Any, Optional, Tuple
import fitz
import io
from PIL import Image
import pytesseract
from langchain.docstore.document import Document

from .base_engine import BaseSnipRAGEngine, logger

class OCRSnipRAGEngine(BaseSnipRAGEngine):
    """
    SnipRAG Engine that uses OCR on horizontal slices.
    This implementation divides pages into horizontal slices and performs
    OCR on each slice to extract text.
    """
    
    def __init__(self, num_slices: int = 10, tesseract_cmd: Optional[str] = None, **kwargs):
        """
        Initialize the OCR-based SnipRAG Engine.
        
        Args:
            num_slices: Number of horizontal slices per page
            tesseract_cmd: Path to tesseract executable, if not in PATH
            **kwargs: Additional arguments to pass to the base class
        """
        super().__init__(**kwargs)
        self.num_slices = num_slices
        
        # Configure Tesseract path if provided
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
            
        # Storage for slice images
        self.slice_images = {}
    
    def _extract_text_chunks(self, pdf_path: str, document_id: str) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Extract text chunks from a PDF with metadata using OCR on horizontal slices.
        
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
            width, height = img.size
            
            # Calculate slice height
            slice_height = height // self.num_slices
            
            # Create and process slices
            for slice_idx in range(self.num_slices):
                # Calculate slice coordinates
                y0 = slice_idx * slice_height
                y1 = (slice_idx + 1) * slice_height if slice_idx < self.num_slices - 1 else height
                
                # Extract the slice image
                slice_img = img.crop((0, y0, width, y1))
                
                # Generate a key for this slice
                slice_key = f"{page_key}_slice_{slice_idx}"
                
                # Store the slice image
                slice_buffer = io.BytesIO()
                slice_img.save(slice_buffer, format="PNG")
                self.slice_images[slice_key] = slice_buffer.getvalue()
                
                # Perform OCR on the slice
                ocr_text = pytesseract.image_to_string(slice_img)
                
                # Skip if no text was found
                if not ocr_text.strip():
                    continue
                
                # Create metadata for this slice
                metadata = {
                    "document_id": document_id,
                    "page_number": page_idx,
                    "slice_index": slice_idx,
                    "slice_key": slice_key,
                    "source": "ocr_slices",
                    "coordinates": [0, y0, width, y1]
                }
                
                # Create a document for langchain
                langchain_doc = Document(
                    page_content=ocr_text,
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
    
    def get_image_snippet(self, result_idx: int, padding: int = None) -> Dict[str, Any]:
        """
        Extract an image snippet for a specific search result.
        
        Args:
            result_idx: Index of the search result
            padding: Optional padding around the text (in pixels)
            
        Returns:
            Dictionary with image data and metadata
        """
        if result_idx < 0 or result_idx >= len(self.documents):
            return {"error": "Invalid result index"}
        
        # Get metadata for this result
        metadata = self.document_metadata[result_idx]
        
        # Check if this is from OCR processing
        if "slice_key" in metadata:
            # Get the slice image directly
            slice_key = metadata["slice_key"]
            if slice_key not in self.slice_images:
                return {"error": "Slice image not found"}
            
            try:
                # Get the slice image
                img_data = self.slice_images[slice_key]
                
                # Convert to base64
                img_base64 = base64.b64encode(img_data).decode()
                
                return {
                    "image_data": img_base64,
                    "page_number": metadata.get("page_number"),
                    "slice_index": metadata.get("slice_index"),
                    "text": self.documents[result_idx],
                    "document_id": metadata.get("document_id")
                }
            except Exception as e:
                logger.error(f"Error creating image snippet from slice: {str(e)}")
                return {"error": f"Failed to create snippet: {str(e)}"}
        
        # Fall back to base class implementation for non-OCR results
        return super().get_image_snippet(result_idx, padding)
    
    def _is_matching_document(self, metadata1: Dict[str, Any], metadata2: Dict[str, Any]) -> bool:
        """
        Check if two document metadata entries refer to the same document.
        For OCR results, we also check the slice index.
        
        Args:
            metadata1: First metadata dictionary
            metadata2: Second metadata dictionary
            
        Returns:
            True if the metadata entries match, False otherwise
        """
        # Check page number first
        if metadata1.get("page_number") != metadata2.get("page_number"):
            return False
            
        # If both have slice_index, they must match
        if "slice_index" in metadata1 and "slice_index" in metadata2:
            return metadata1["slice_index"] == metadata2["slice_index"]
            
        # If only one has slice_index, they're different types
        if "slice_index" in metadata1 or "slice_index" in metadata2:
            return False
            
        # Otherwise, they match if page numbers match
        return True
        
    def clear_index(self):
        """Clear the index and all stored documents."""
        super().clear_index()
        self.slice_images = {} 