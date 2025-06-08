#!/usr/bin/env python
"""
Basic demo for SnipRAG showing how to process a PDF and search for information
with image snippets.
"""

import os
import sys
import argparse
import base64
import io
from PIL import Image
import matplotlib.pyplot as plt

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sniprag import SnipRAGEngine

def display_results(results):
    """Display search results with image snippets."""
    # Set up matplotlib figure for displaying images
    n_results = len(results)
    print("Results:")
    print(results)
    if n_results == 0:
        print("No results found.")
        return
    
    fig, axes = plt.subplots(n_results, 1, figsize=(8, 4 * n_results))
    if n_results == 1:
        axes = [axes]  # Make it iterable when there's only one result
        
    # Display each result with its image snippet
    for i, result in enumerate(results):
        print(f"\n--- Match {i+1} (Page {result['metadata']['page_number']}) ---")
        print(f"Score: {result['score']:.4f}")
        
        # Truncate text if too long
        text = result['text']
        if len(text) > 300:
            text = text[:300] + "..."
        
        print(f"Text: {text}")
        
        # Display image snippet if available
        if "image_data" in result:
            try:
                # Decode the image
                image_data = base64.b64decode(result["image_data"])
                img = Image.open(io.BytesIO(image_data))
                
                # Display using matplotlib
                axes[i].imshow(img)
                axes[i].set_title(f"Match {i+1}: {text[:50]}...")
                axes[i].axis('off')
                
                print("Image snippet available - displaying with matplotlib")
            except Exception as e:
                print(f"Error displaying image: {str(e)}")
        else:
            print("No image snippet available")
            if "image_error" in result:
                print(f"Error: {result['image_error']}")
            
            # Display a placeholder
            axes[i].text(0.5, 0.5, "No image available", 
                      ha='center', va='center', transform=axes[i].transAxes)
            axes[i].axis('off')
    
    # Show the figure
    plt.tight_layout()
    plt.show()

def main():
    """Run the SnipRAG demo."""
    parser = argparse.ArgumentParser(description='SnipRAG Demo')
    parser.add_argument('--pdf', type=str, help='Path to PDF file')
    args = parser.parse_args()
    
    print("=== SnipRAG Demo ===")
    print("This demo shows how to use SnipRAG to search PDFs and extract image snippets.")
    
    # Get PDF path from command line or user input
    pdf_path = args.pdf
    if not pdf_path:
        pdf_path = input("Enter path to PDF file: ")
    
    if not os.path.exists(pdf_path):
        print(f"Error: File not found at {pdf_path}")
        return
    
    # Initialize the SnipRAG engine
    print("\nInitializing SnipRAG engine...")
    engine = SnipRAGEngine()
    
    # Process the PDF
    print(f"Processing PDF: {pdf_path}")
    success = engine.process_pdf(pdf_path, "demo-document")
    
    if not success:
        print("Error processing the PDF. Exiting.")
        return
    
    print("PDF processed successfully!")
    
    # Interactive search loop
    while True:
        # Get search query
        print("\n" + "-" * 50)
        query = input("Enter search query (or 'quit' to exit): ")
        if query.lower() in ('quit', 'exit', 'q'):
            break
        
        # Get snippet padding
        try:
            padding = int(input("Enter padding for image snippets (default: 20): ") or "20")
        except ValueError:
            padding = 20
            print("Invalid input, using default padding of 20 pixels")
        
        # Perform search with image snippets
        print(f"\nSearching for: '{query}'...")
        results = engine.search_with_snippets(query, top_k=3, snippet_padding=padding)
        
        # Display results
        display_results(results)
    
    print("\nThank you for using the SnipRAG Demo!")

if __name__ == "__main__":
    main() 