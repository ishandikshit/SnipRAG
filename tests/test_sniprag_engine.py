"""
Tests for the SnipRAG engine.
"""

import os
import sys
import pytest
import tempfile
import base64
from io import BytesIO
from PIL import Image
import fitz  # PyMuPDF

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sniprag import SnipRAGEngine

class TestSnipRAGEngine:
    """Tests for the SnipRAG engine."""
    
    @pytest.fixture
    def sample_pdf(self):
        """Create a sample PDF file for testing."""
        # Create a temporary PDF file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            temp_path = tmp.name
        
        # Create a new PDF with PyMuPDF
        doc = fitz.open()
        page = doc.new_page(width=612, height=792)  # Letter size
        
        # Add some text to the page
        font_size = 11
        text1 = "This is a sample invoice for SnipRAG testing."
        text2 = "The invoice total amount is $1,234.56."
        text3 = "This document was created on January 15, 2023."
        text4 = "Please make payment by February 15, 2023."
        
        # Position the text blocks
        page.insert_text((72, 72), text1, fontsize=font_size)
        page.insert_text((72, 144), text2, fontsize=font_size)
        page.insert_text((72, 216), text3, fontsize=font_size)
        page.insert_text((72, 288), text4, fontsize=font_size)
        
        # Save the PDF
        doc.save(temp_path)
        doc.close()
        
        yield temp_path
        
        # Clean up
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    def test_engine_initialization(self):
        """Test that the engine initializes correctly."""
        engine = SnipRAGEngine()
        assert engine is not None
        assert engine.embedding_model is not None
        assert engine.index is not None
        assert isinstance(engine.documents, list)
        assert isinstance(engine.document_metadata, list)
        assert isinstance(engine.text_coordinates, list)
        assert isinstance(engine.page_images, dict)
    
    def test_process_pdf(self, sample_pdf):
        """Test processing a PDF file."""
        engine = SnipRAGEngine()
        success = engine.process_pdf(sample_pdf, "test-document")
        
        assert success
        assert len(engine.documents) > 0
        assert len(engine.document_metadata) == len(engine.documents)
        assert len(engine.text_coordinates) == len(engine.documents)
        assert len(engine.page_images) > 0
    
    def test_search(self, sample_pdf):
        """Test searching for content in a processed PDF."""
        engine = SnipRAGEngine()
        engine.process_pdf(sample_pdf, "test-document")
        
        # Search for something in the document
        results = engine.search("invoice total", top_k=2)
        
        assert len(results) > 0
        assert "text" in results[0]
        assert "metadata" in results[0]
        assert "score" in results[0]
        
        # Verify metadata
        assert "document_id" in results[0]["metadata"]
        assert results[0]["metadata"]["document_id"] == "test-document"
        assert "page_number" in results[0]["metadata"]
    
    def test_search_with_snippets(self, sample_pdf):
        """Test searching with image snippets."""
        engine = SnipRAGEngine()
        engine.process_pdf(sample_pdf, "test-document")
        
        # Search with snippets
        results = engine.search_with_snippets("invoice total", top_k=2)
        
        assert len(results) > 0
        assert "text" in results[0]
        assert "metadata" in results[0]
        assert "score" in results[0]
        
        # Verify image data is present
        assert "image_data" in results[0]
        
        # Test decoding the image
        image_data = base64.b64decode(results[0]["image_data"])
        img = Image.open(BytesIO(image_data))
        
        # Verify image dimensions
        assert img.width > 0
        assert img.height > 0
    
    def test_filter_metadata(self, sample_pdf):
        """Test filtering search results by metadata."""
        engine = SnipRAGEngine()
        engine.process_pdf(sample_pdf, "test-document")
        
        # Add a second document with different ID
        engine.process_pdf(sample_pdf, "another-document")
        
        # Search with filter for first document
        results = engine.search(
            "invoice", 
            top_k=5, 
            filter_metadata={"document_id": "test-document"}
        )
        
        assert len(results) > 0
        for result in results:
            assert result["metadata"]["document_id"] == "test-document"
    
    def test_clear_index(self, sample_pdf):
        """Test clearing the index."""
        engine = SnipRAGEngine()
        engine.process_pdf(sample_pdf, "test-document")
        
        # Verify documents are added
        assert len(engine.documents) > 0
        
        # Clear the index
        engine.clear_index()
        
        # Verify everything is cleared
        assert len(engine.documents) == 0
        assert len(engine.document_metadata) == 0
        assert len(engine.text_coordinates) == 0
        assert len(engine.page_images) == 0 