#!/usr/bin/env python
"""
Script to generate example snippets of tabular data for the README.
"""

import os
import sys
import base64
import io
from PIL import Image

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from sniprag import SnipRAGEngine

def save_snippet(image_data, filename):
    """Save a base64 encoded image to a file."""
    image_bytes = base64.b64decode(image_data)
    img = Image.open(io.BytesIO(image_bytes))
    img.save(filename)
    print(f"Saved snippet to {filename}")

def main():
    """Generate and save example snippets focusing on tabular data."""
    # Check if sample PDF exists
    sample_pdf = "samples/sample_document.pdf"
    if not os.path.exists(sample_pdf):
        print(f"Error: Sample PDF not found at {sample_pdf}")
        return
    
    # Create output directory
    os.makedirs("docs/examples", exist_ok=True)
    
    print("Initializing SnipRAG engine...")
    engine = SnipRAGEngine()
    
    print(f"Processing PDF: {sample_pdf}")
    success = engine.process_pdf(sample_pdf, "demo-document")
    
    if not success:
        print("Error processing the PDF. Exiting.")
        return
    
    print("PDF processed successfully!")
    
    # Define example queries for tabular data and output filenames
    examples = [
        ("quarterly financial performance table", "docs/examples/financial_table_snippet.png", 40),
        ("Q2 2022 revenue", "docs/examples/q2_revenue_snippet.png", 120),
        ("total profit", "docs/examples/total_profit_snippet.png", 120),
        ("technical components comparison", "docs/examples/tech_comparison_snippet.png", 140),
        ("semantic search method", "docs/examples/semantic_search_snippet.png", 120)
    ]
    
    # Generate and save snippets for each example
    for query, filename, padding in examples:
        print(f"\nSearching for: '{query}'...")
        results = engine.search_with_snippets(query, top_k=1, snippet_padding=padding)
        
        if results and "image_data" in results[0]:
            save_snippet(results[0]["image_data"], filename)
            print(f"Text match: {results[0]['text']}")
        else:
            print(f"No image snippet found for query: '{query}'")
    
    print("\nExample tabular data snippets generated successfully!")

if __name__ == "__main__":
    main() 