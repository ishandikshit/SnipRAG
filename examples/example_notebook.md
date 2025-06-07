# Using SnipRAG in a Jupyter Notebook

This document illustrates how to use SnipRAG in a Jupyter notebook environment.

## Installation

```python
!pip install sniprag matplotlib
```

## Import Libraries

```python
import base64
import io
from PIL import Image
import matplotlib.pyplot as plt
from IPython.display import display, HTML
from sniprag import SnipRAGEngine
```

## Initialize the SnipRAG Engine

```python
# Initialize the engine
engine = SnipRAGEngine()
```

## Process a PDF Document

```python
# Path to your PDF document
pdf_path = "path/to/your/document.pdf"

# Process the PDF
document_id = "example-doc"
success = engine.process_pdf(pdf_path, document_id)

if success:
    print("PDF processed successfully!")
else:
    print("Error processing PDF")
```

## Search for Information with Image Snippets

```python
# Define a search query
query = "invoice total amount"

# Search with image snippets
results = engine.search_with_snippets(query, top_k=3)

print(f"Found {len(results)} results")
```

## Display Results with Image Snippets

```python
def display_results(results):
    """Display search results with image snippets in a notebook."""
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
                plt.figure(figsize=(8, 4))
                plt.imshow(img)
                plt.title(f"Match {i+1}: {text[:50]}...")
                plt.axis('off')
                plt.show()
                
            except Exception as e:
                print(f"Error displaying image: {str(e)}")
        else:
            print("No image snippet available")
            if "image_error" in result:
                print(f"Error: {result['image_error']}")

# Display the results
display_results(results)
```

## Working with Multiple Documents

```python
# Process additional documents
engine.process_pdf("path/to/another/document.pdf", "doc-2")
engine.process_pdf("path/to/third/document.pdf", "doc-3")

# Search across all documents
all_results = engine.search_with_snippets("payment terms", top_k=5)

# Search in a specific document
doc2_results = engine.search_with_snippets(
    "payment terms", 
    top_k=3,
    filter_metadata={"document_id": "doc-2"}
)

# Display results from specific document
display_results(doc2_results)
```

## Adjusting Snippet Size

```python
# Search with larger padding around text matches
large_snippets = engine.search_with_snippets(
    "invoice date", 
    top_k=2,
    snippet_padding=50  # Larger padding (default is 20)
)

# Display results with larger snippets
display_results(large_snippets)
```

## Creating a Reusable Search Function

```python
def search_documents(query, top_k=3, document_id=None, padding=20):
    """Search for information in documents with image snippets."""
    filter_metadata = {"document_id": document_id} if document_id else None
    
    results = engine.search_with_snippets(
        query,
        top_k=top_k,
        filter_metadata=filter_metadata,
        snippet_padding=padding
    )
    
    display_results(results)
    return results

# Use the function
financial_results = search_documents("financial statement", top_k=3)
```

## Clearing the Index

```python
# Clear the index when done or to start fresh
engine.clear_index()
print("Index cleared")
``` 