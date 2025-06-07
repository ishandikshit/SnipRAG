"""
SnipRAG Engine - Retrieval Augmented Generation with image snippets from PDFs.
This module enables semantic searching of PDF documents and returns
relevant image snippets from the areas containing matching text.
"""

import os
import logging
import tempfile
import base64
from typing import List, Dict, Any, Optional, Tuple, Union
import json
import fitz  # PyMuPDF
import boto3
import faiss
import numpy as np
from PIL import Image
import io
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

logger = logging.getLogger(__name__)

class SnipRAGEngine:
    """
    SnipRAG Engine that can return image snippets from PDFs based on semantic text search.
    """
    
    def __init__(self, embedding_model_name: str = "all-MiniLM-L6-v2", aws_credentials: Optional[Dict[str, str]] = None):
        """
        Initialize the SnipRAG Engine.
        
        Args:
            embedding_model_name: Name of the sentence-transformers model to use for embeddings
            aws_credentials: Optional AWS credentials for accessing S3
        """
        self.aws_credentials = aws_credentials
        
        # Initialize the embedding model
        self.embedding_model = SentenceTransformer(embedding_model_name)
        self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
        
        # Initialize an in-memory FAISS index for vector storage
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        
        # Storage for document chunks and metadata
        self.documents = []
        self.document_metadata = []
        
        # Storage for text block coordinates and page images
        self.text_coordinates = []
        self.page_images = {}
        
        # Padding for image snippets (in pixels, applied to all sides)
        self.snippet_padding = 20
        
        # Text splitter for chunking documents
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def download_pdf_from_s3(self, s3_uri: str) -> str:
        """
        Download a PDF from S3 to a temporary file.
        
        Args:
            s3_uri: S3 URI of the PDF
            
        Returns:
            Path to the downloaded temporary file
        """
        # Parse the S3 URI
        if not s3_uri.startswith('s3://'):
            raise ValueError(f"Invalid S3 URI format: {s3_uri}")
            
        s3_parts = s3_uri[5:].split('/', 1)  # Remove 's3://' and split on first '/'
        if len(s3_parts) != 2:
            raise ValueError(f"Invalid S3 URI format: {s3_uri}")
            
        bucket_name = s3_parts[0]
        object_key = s3_parts[1]
        
        # Create a temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        temp_path = temp_file.name
        temp_file.close()
        
        # Download the file
        if self.aws_credentials:
            s3_client = boto3.client('s3', **self.aws_credentials)
        else:
            s3_client = boto3.client('s3')
            
        s3_client.download_file(bucket_name, object_key, temp_path)
        
        return temp_path
    
    def process_pdf(self, pdf_path: str, document_id: str) -> bool:
        """
        Process a PDF file and add it to the SnipRAG engine.
        
        Args:
            pdf_path: Path to the PDF file
            document_id: Unique identifier for the document
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Extract text from PDF
            chunks_with_metadata = self._extract_text_chunks(pdf_path, document_id)
            
            # Create embeddings and add to index
            self._add_chunks_to_index(chunks_with_metadata)
            
            return True
                
        except Exception as e:
            logger.error(f"Error processing document {document_id}: {str(e)}")
            return False
    
    def process_document_from_s3(self, s3_uri: str, document_id: str) -> bool:
        """
        Process a document from S3 and add it to the SnipRAG engine.
        
        Args:
            s3_uri: S3 URI of the document PDF
            document_id: Unique identifier for the document
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Download the PDF
            temp_path = self.download_pdf_from_s3(s3_uri)
            
            try:
                # Process the PDF
                return self.process_pdf(temp_path, document_id)
                
            finally:
                # Clean up the temporary file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
        except Exception as e:
            logger.error(f"Error processing document {document_id} from S3: {str(e)}")
            return False
    
    def _extract_text_chunks(self, pdf_path: str, document_id: str) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Extract text chunks from a PDF with metadata including text coordinates.
        
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
            self.page_images[page_key] = img_data
            
            # Extract text blocks with their coordinates
            text_blocks = page.get_text("blocks")
            
            for block_idx, block in enumerate(text_blocks):
                # Skip image blocks (blocks with type 1)
                if block[6] == 1:
                    continue
                    
                text = block[4]
                coordinates = block[:4]  # x0, y0, x1, y1
                
                # Scale coordinates to match the rendered image resolution
                scale_factor = 300/72
                scaled_coords = [c * scale_factor for c in coordinates]
                
                # Create metadata
                metadata = {
                    "document_id": document_id,
                    "page_number": page_idx,
                    "source": "pdf",
                    "block_index": block_idx,
                    "coordinates": scaled_coords
                }
                
                # Split the text into chunks
                if len(text) > 0:
                    # Create a document for langchain
                    langchain_doc = Document(
                        page_content=text,
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
    
    def _add_chunks_to_index(self, chunks_with_metadata: List[Tuple[str, Dict[str, Any]]]):
        """
        Create embeddings for chunks and add them to the index.
        
        Args:
            chunks_with_metadata: List of tuples (text_chunk, metadata)
        """
        if not chunks_with_metadata:
            return
        
        # Extract just the text chunks
        texts = [chunk[0] for chunk in chunks_with_metadata]
        
        # Create embeddings
        embeddings = self.embedding_model.encode(texts)
        
        # Add to FAISS index
        self.index.add(np.array(embeddings).astype('float32'))
        
        # Store documents, metadata, and coordinates
        current_idx = len(self.documents)
        self.documents.extend(texts)
        self.document_metadata.extend([meta for _, meta in chunks_with_metadata])
        
        # Store text coordinates for later use in image extraction
        self.text_coordinates.extend([meta.get("coordinates", [0, 0, 0, 0]) 
                                    for _, meta in chunks_with_metadata])
        
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
        coordinates = self.text_coordinates[result_idx]
        
        # Get page key
        document_id = metadata.get("document_id")
        page_number = metadata.get("page_number")
        page_key = f"{document_id}_{page_number}"
        
        # Check if we have the page image
        if page_key not in self.page_images:
            return {"error": "Page image not found"}
        
        # Set padding (use instance default if not specified)
        if padding is None:
            padding = self.snippet_padding
        
        # Extract coordinates
        x0, y0, x1, y1 = coordinates
        
        # Apply padding
        x0 = max(0, x0 - padding)
        y0 = max(0, y0 - padding)
        x1 += padding
        y1 += padding
        
        try:
            # Get the page image
            img_data = self.page_images[page_key]
            img = Image.open(io.BytesIO(img_data))
            
            # Crop the image to the text region
            snippet = img.crop((x0, y0, x1, y1))
            
            # Convert to base64
            buffered = io.BytesIO()
            snippet.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode()
            
            return {
                "image_data": img_base64,
                "page_number": page_number,
                "coordinates": [x0, y0, x1, y1],
                "text": self.documents[result_idx],
                "document_id": document_id
            }
            
        except Exception as e:
            logger.error(f"Error creating image snippet: {str(e)}")
            return {"error": f"Failed to create snippet: {str(e)}"}
    
    def search(self, query: str, top_k: int = 5, 
              filter_metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Search for documents similar to the query.
        
        Args:
            query: Search query
            top_k: Number of results to return
            filter_metadata: Optional metadata filters
            
        Returns:
            List of results with text and metadata
        """
        if len(self.documents) == 0:
            return []
        
        # Create query embedding
        query_embedding = self.embedding_model.encode([query])[0]
        
        # Search the index
        distances, indices = self.index.search(np.array([query_embedding]).astype('float32'), k=min(top_k * 2, len(self.documents)))
        
        # Prepare results
        results = []
        for i, idx in enumerate(indices[0]):
            # Skip if index is -1 (no result)
            if idx == -1:
                continue
                
            metadata = self.document_metadata[idx]
            
            # Apply metadata filters if provided
            if filter_metadata:
                skip = False
                for key, value in filter_metadata.items():
                    if key in metadata and metadata[key] != value:
                        skip = True
                        break
                if skip:
                    continue
            
            # Add to results
            results.append({
                "text": self.documents[idx],
                "metadata": metadata,
                "score": float(1.0 / (1.0 + distances[0][i]))  # Convert distance to a similarity score
            })
            
            # Stop once we have enough results
            if len(results) >= top_k:
                break
        
        return results
    
    def search_with_snippets(self, query: str, top_k: int = 5, 
                           filter_metadata: Optional[Dict[str, Any]] = None,
                           include_snippets: bool = True,
                           snippet_padding: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Search for documents similar to the query and return image snippets.
        
        Args:
            query: Search query
            top_k: Number of results to return
            filter_metadata: Optional metadata filters
            include_snippets: Whether to include image snippets in results
            snippet_padding: Optional padding override for snippets
            
        Returns:
            List of results with text, metadata, and image snippets
        """
        # Get text search results
        results = self.search(query, top_k, filter_metadata)
        
        # If not including snippets, just return the text results
        if not include_snippets:
            return results
        
        # Add image snippets to results
        for i, result in enumerate(results):
            # Find the original index in our documents list
            doc_text = result["text"]
            doc_metadata = result["metadata"]
            
            # Find the matching document in our stored documents
            for idx, (text, metadata) in enumerate(zip(self.documents, self.document_metadata)):
                if text == doc_text and metadata["page_number"] == doc_metadata["page_number"]:
                    # Get image snippet
                    snippet = self.get_image_snippet(idx, snippet_padding)
                    
                    # Add snippet data to result
                    if "error" not in snippet:
                        result["image_data"] = snippet["image_data"]
                        result["coordinates"] = snippet["coordinates"]
                    else:
                        result["image_error"] = snippet["error"]
                    
                    break
        
        return results
        
    def clear_index(self):
        """Clear the index and all stored documents."""
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        self.documents = []
        self.document_metadata = []
        self.text_coordinates = []
        self.page_images = {} 