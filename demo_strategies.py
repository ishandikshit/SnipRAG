#!/usr/bin/env python
"""
SnipRAG Strategy Demo - Demonstrates both semantic and OCR extraction strategies
"""

import os
import argparse
import tempfile
import fitz
import webbrowser
from sniprag.core import create_engine

def create_test_pdf(output_path="test_document.pdf"):
    """Create a simple test PDF with text content"""
    # Create a new PDF with one page
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)  # A4 size
    
    # Add some text content at different positions
    page.insert_text((50, 50), "Top section text.", fontsize=12)
    page.insert_text((50, 200), "Upper middle section text.", fontsize=12)
    page.insert_text((50, 400), "Middle section text.", fontsize=12)
    page.insert_text((50, 600), "Lower middle section text.", fontsize=12)
    page.insert_text((50, 800), "Bottom section text.", fontsize=12)
    
    # Save the document
    doc.save(output_path)
    doc.close()
    
    return output_path

def run_demo(strategy="semantic", pdf_path=None, query="middle", tesseract_path=None):
    """
    Run a demo of the SnipRAG engine with the specified strategy
    
    Args:
        strategy: Extraction strategy to use ('semantic' or 'ocr')
        pdf_path: Path to PDF file to process (if None, a test PDF will be created)
        query: Search query to use
        tesseract_path: Path to tesseract executable (only needed for OCR strategy)
    """
    print(f"\n===== SnipRAG Demo - {strategy.upper()} Strategy =====")
    
    # Create or use PDF
    if pdf_path is None:
        pdf_path = create_test_pdf()
        print(f"Created test PDF at: {os.path.abspath(pdf_path)}")
    else:
        print(f"Using PDF at: {os.path.abspath(pdf_path)}")
    
    # Create engine with specified strategy
    kwargs = {}
    if strategy.lower() == "ocr" and tesseract_path:
        kwargs["tesseract_cmd"] = tesseract_path
        print(f"Using Tesseract at: {tesseract_path}")
        
    # Create the engine
    print(f"Creating {strategy} engine...")
    engine = create_engine(strategy, **kwargs)
    
    # Process the PDF
    print(f"Processing PDF...")
    result = engine.process_pdf(pdf_path, "demo_doc")
    if not result:
        print("Failed to process PDF")
        return
    
    print(f"Extracted {len(engine.documents)} total text chunks")
    
    # Search with snippets
    print(f"Searching for: '{query}'")
    results = engine.search_with_snippets(query, top_k=3)
    print(f"Found {len(results)} results")
    
    # Display basic info about the results
    if results:
        for i, result in enumerate(results):
            source_type = "slice" if "slice_index" in result["metadata"] else "block"
            index = result["metadata"].get("slice_index" if source_type == "slice" else "block_index", -1)
            print(f"\nResult #{i+1} - Score: {result['score']:.4f}, {source_type.capitalize()}: {index}")
            print(f"Text: {result['text'][:100]}...")
    
    # Create a simple HTML to display the results
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>SnipRAG {strategy.upper()} Demo</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ background-color: #f5f5f5; padding: 10px; margin-bottom: 20px; }}
            .result {{ margin-bottom: 30px; border: 1px solid #ccc; padding: 15px; border-radius: 5px; }}
            .text {{ margin-bottom: 10px; white-space: pre-wrap; }}
            .meta {{ color: #666; font-size: 0.9em; margin-bottom: 10px; }}
            .score {{ font-weight: bold; }}
            img {{ max-width: 100%; border: 1px solid #eee; margin-top: 10px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>SnipRAG {strategy.upper()} Strategy Demo</h1>
            <p>Query: "{query}"</p>
            <p>PDF: {os.path.basename(pdf_path)}</p>
            <p>Extracted {len(engine.documents)} text chunks</p>
        </div>
        
        <h2>Search Results</h2>
    """
    
    # Add each result to the HTML
    for i, result in enumerate(results):
        source_type = "slice" if "slice_index" in result["metadata"] else "block"
        index = result["metadata"].get("slice_index" if source_type == "slice" else "block_index", -1)
        page_num = result["metadata"].get("page_number", 0) + 1
        
        html += f"""
        <div class="result">
            <div class="score">Result #{i+1} - Score: {result['score']:.4f}</div>
            <div class="meta">Page {page_num}, {source_type.capitalize()} {index}</div>
            <div class="text">{result['text']}</div>
        """
        
        # Add the image if available
        if 'image_data' in result:
            html += f"""
            <img src="data:image/png;base64,{result['image_data']}" alt="Snippet">
            """
        else:
            html += "<p>No image available</p>"
            
        html += "</div>"
    
    html += """
    </body>
    </html>
    """
    
    # Create a temporary HTML file
    with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as f:
        f.write(html.encode('utf-8'))
        temp_path = f.name
    
    # Open the HTML file in the default browser
    print(f"Opening results in browser...")
    webbrowser.open('file://' + temp_path)

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="SnipRAG Strategy Demo")
    parser.add_argument("--strategy", "-s", choices=["semantic", "ocr"], default="semantic",
                        help="Extraction strategy to use (default: semantic)")
    parser.add_argument("--pdf", "-p", help="Path to PDF file (default: create a test PDF)")
    parser.add_argument("--query", "-q", default="middle", help="Search query (default: 'middle')")
    parser.add_argument("--tesseract", "-t", help="Path to tesseract executable (needed for OCR strategy)")
    
    args = parser.parse_args()
    
    # Run the demo
    run_demo(args.strategy, args.pdf, args.query, args.tesseract) 