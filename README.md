# SnipRAG: Retrieval Augmented Generation with Image Snippets

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

SnipRAG is a specialized Retrieval Augmented Generation (RAG) system that not only finds semantically relevant text in PDF documents but also extracts precise image snippets from the areas containing the matching text.

<p align="center">
  <img src="docs/sniprag_architecture.png" alt="SnipRAG Architecture" width="600"/>
</p>

## Key Features

- **Semantic PDF Search**: Find information in PDF documents using natural language queries
- **Image Snippet Extraction**: Get visual context from the exact regions containing relevant information
- **Precise Coordinate Mapping**: Maps text matches to their exact visual location in the document
- **Customizable Snippet Size**: Adjust padding around text regions to control snippet size
- **S3 Integration**: Process documents stored in Amazon S3
- **Flexible Filtering**: Filter search results by document, page, or custom metadata

## Installation

### From PyPI

> ⚠️ **Note**: This package is not yet available on PyPI. Please use the source installation method below.

In the future, once published to PyPI:
```bash
pip install sniprag
```

### From Source

```bash
git clone https://github.com/ishandikshit/SnipRAG.git
cd SnipRAG
pip install -e .
```

For visualization support (recommended for demos):

```bash
pip install -e ".[viz]"
```

## Quick Start

```python
from sniprag import SnipRAGEngine

# Initialize the engine
engine = SnipRAGEngine()

# Process a PDF document
engine.process_pdf("path/to/document.pdf", "document-id")

# Search with image snippets
results = engine.search_with_snippets("your search query", top_k=3)

# Access results
for result in results:
    print(f"Text: {result['text']}")
    print(f"Page: {result['metadata']['page_number']}")
    print(f"Score: {result['score']}")
    
    # The image snippet is available as base64 data that can be displayed or saved
    if "image_data" in result:
        image_base64 = result["image_data"]
        # Use this to display or save the image
```

## Example Snippets

Here are some examples of SnipRAG in action, showing how it extracts image snippets from PDF documents based on semantic search queries:

### Financial Data Extraction

**Query:** "What is the total revenue?"

![Revenue Snippet](docs/examples/revenue_snippet.png)

*SnipRAG extracts the exact region containing revenue information, providing visual context alongside the text match.*

### Technical Specification Extraction

**Query:** "How does the system implement semantic search?"

![Semantic Search Snippet](docs/examples/semantic_search_snippet.png)

*When searching for technical details, SnipRAG locates and extracts the relevant section, preserving formatting and visual context.*

### Document Navigation

**Query:** "Show me the introduction section"

![Introduction Snippet](docs/examples/introduction_snippet.png)

*SnipRAG can help navigate to specific sections of a document based on semantic understanding of the content.*

> Note: To generate these snippets yourself, run the basic demo with a sample PDF as shown in the Demos section below.

## Demos

SnipRAG includes two demo applications:

### Basic Demo

Process a local PDF file and search for information with image snippets:

```bash
python examples/basic_demo.py --pdf path/to/document.pdf
```

### S3 Demo

Process a PDF stored in Amazon S3:

```bash
python examples/s3_demo.py --s3-uri s3://bucket/path/to/document.pdf --aws-profile your-profile
```

### Jupyter Notebook Example

For those working in Jupyter environments, there's also a notebook example available:

```bash
# View the notebook example
cat examples/example_notebook.md
```

This markdown file contains code snippets you can use in a Jupyter notebook to process PDFs and visualize search results with image snippets.

## How It Works

SnipRAG combines semantic search with coordinate mapping to provide visual context:

1. **PDF Processing**:
   - Extracts text blocks with their coordinates
   - Renders page images at high resolution
   - Creates text embeddings for semantic search

2. **Search Process**:
   - User submits a natural language query
   - System finds semantically similar text using embeddings
   - For each match, it identifies the exact location in the PDF
   - It extracts an image snippet from that location

3. **Result Delivery**:
   - Returns the matching text
   - Provides a visual snippet of the area containing the text
   - Includes metadata (page number, coordinates, etc.)

## API Reference

### `SnipRAGEngine`

Main class for the SnipRAG engine.

```python
engine = SnipRAGEngine(
    embedding_model_name="all-MiniLM-L6-v2",  # Model for text embeddings
    aws_credentials=None  # Optional AWS credentials for S3 access
)
```

#### Methods

- **`process_pdf(pdf_path, document_id)`**: Process a local PDF file
- **`process_document_from_s3(s3_uri, document_id)`**: Process a PDF from S3
- **`search(query, top_k=5, filter_metadata=None)`**: Search for text matches
- **`search_with_snippets(query, top_k=5, filter_metadata=None, include_snippets=True, snippet_padding=None)`**: Search with image snippets
- **`get_image_snippet(result_idx, padding=None)`**: Get an image snippet for a specific result
- **`clear_index()`**: Clear the search index and stored documents

## Use Cases

SnipRAG is particularly valuable for:

- **Financial Document Analysis**: Extract specific items from invoices or financial statements
- **Legal Document Review**: Find and visualize specific clauses in contracts
- **Technical Documentation**: Locate diagrams, tables, and code snippets
- **Research Papers**: Find equations, figures, and important text
- **Medical Records**: Identify specific sections, charts, or results

## Requirements

- Python 3.8+
- Required packages:
  - pymupdf (PyMuPDF)
  - sentence-transformers
  - faiss-cpu
  - pillow
  - numpy
  - boto3 (for S3 integration)
  - langchain (for text splitting)
  - matplotlib (for visualization, optional)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- This project was inspired by the need for more precise visual context in RAG systems
- Thanks to the developers of PyMuPDF, sentence-transformers, and FAISS for their excellent libraries 