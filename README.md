# SnipRAG: Retrieval Augmented Generation with Image Snippets

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://badge.fury.io/py/sniprag.svg)](https://badge.fury.io/py/sniprag)

SnipRAG is a specialized Retrieval Augmented Generation (RAG) system that not only finds semantically relevant text in PDF documents but also extracts precise image snippets from the areas containing the matching text.

<p align="center">
  <img src="docs/sniprag_architecture.png" alt="SnipRAG Architecture" width="600"/>
</p>

## Key Features

- **Semantic PDF Search**: Find information in PDF documents using natural language queries
- **Image Snippet Extraction**: Get visual context from the exact regions containing relevant information
- **Multiple Extraction Strategies**: Choose between semantic text extraction or OCR-based processing
- **Precise Coordinate Mapping**: Maps text matches to their exact visual location in the document
- **Customizable Snippet Size**: Adjust padding around text regions to control snippet size
- **S3 Integration**: Process documents stored in Amazon S3
- **Flexible Filtering**: Filter search results by document, page, or custom metadata

## Installation

### From PyPI

```bash
pip install sniprag
```

For visualization support (recommended for demos):

```bash
pip install sniprag[viz]
```

For OCR support:

```bash
pip install sniprag[ocr]
```

For all features:

```bash
pip install sniprag[all]
```

### From Source

```bash
git clone https://github.com/ishandikshit/SnipRAG.git
cd SnipRAG
pip install -e .
```

### From GitHub

You can install directly from GitHub using pip:

```bash
pip install git+https://github.com/ishandikshit/SnipRAG.git
```

For visualization and OCR support:

```bash
pip install "git+https://github.com/ishandikshit/SnipRAG.git#egg=sniprag[all]"
```

## Quick Start

```python
from sniprag import create_engine

# Initialize the engine with semantic strategy (default)
engine = create_engine("semantic", num_blocks=20, block_overlap=0.2)

# Or use OCR-based strategy
# engine = create_engine("ocr", num_slices=10, tesseract_cmd="/path/to/tesseract")

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

## Extraction Strategies

SnipRAG offers two different text extraction strategies:

### Semantic Strategy

The semantic strategy uses PyMuPDF's built-in text extraction:

- Divides each page into configurable horizontal blocks (default: 20)
- Extracts text directly from the PDF structure
- Works best with native digital PDFs
- More precise for well-structured documents

```python
engine = create_engine("semantic", num_blocks=20, block_overlap=0.2)
```

### OCR Strategy

The OCR strategy uses Tesseract OCR:

- Divides each page into configurable horizontal slices (default: 10)
- Performs OCR on each slice to extract text
- Better for scanned documents or images
- More resilient to poor quality documents

```python
engine = create_engine("ocr", num_slices=10, tesseract_cmd="/path/to/tesseract")
```

## Example Snippets

Here are some examples of SnipRAG in action, showing how it extracts image snippets from PDF documents based on semantic search queries:

### Structured Table Extraction

**Query:** "quarterly financial performance table"

![Financial Table Snippet](docs/examples/financial_table_snippet.png?v=1)

*SnipRAG preserves the entire table structure, making it possible to understand relationships between rows and columns that would be lost in text-only extraction.*

### Specific Table Cell Data

**Query:** "Q2 2022 revenue"

![Q2 Revenue Snippet](docs/examples/q2_revenue_snippet.png?v=1)

*When searching for specific data points within tables, SnipRAG extracts not just the matching cell but also the surrounding context, showing related row and column data.*

### Financial Data with Context

**Query:** "total profit"

![Total Profit Snippet](docs/examples/total_profit_snippet.png?v=1)

*For financial documents, seeing the numbers in their original tabular format provides critical context that would be lost in pure text extraction.*

### Technical Comparison Charts

**Query:** "technical components comparison"

![Technical Comparison Snippet](docs/examples/tech_comparison_snippet.png?v=1)

*Complex comparison tables maintain their structure in the extracted snippets, making it easier to understand the relationships between different items.*

> Note: To generate these snippets yourself, run the basic demo with a sample PDF as shown in the Demos section below.

## Demos

SnipRAG includes several demo applications:

### Strategy Demo

Compare different extraction strategies with a test document:

```bash
python demo_strategies.py --strategy semantic  # Default strategy
python demo_strategies.py --strategy ocr --tesseract /path/to/tesseract
```

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
   - Extracts text using the selected strategy (semantic or OCR)
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

### Factory Function

The main entry point for creating SnipRAG engines.

```python
from sniprag import create_engine

engine = create_engine(
    strategy="semantic",  # "semantic" or "ocr"
    **kwargs  # Strategy-specific parameters
)
```

### `BaseSnipRAGEngine`

Base class for all SnipRAG engines.

### `SemanticSnipRAGEngine`

Engine that uses PyMuPDF's text extraction.

```python
engine = create_engine(
    "semantic",
    num_blocks=20,  # Number of horizontal blocks per page
    block_overlap=0.2,  # Overlap between blocks (0.0-1.0)
    embedding_model_name="all-MiniLM-L6-v2",  # Model for text embeddings
    aws_credentials=None  # Optional AWS credentials for S3 access
)
```

### `OCRSnipRAGEngine`

Engine that uses Tesseract OCR for text extraction.

```python
engine = create_engine(
    "ocr",
    num_slices=10,  # Number of horizontal slices per page
    tesseract_cmd="/path/to/tesseract",  # Path to Tesseract executable
    embedding_model_name="all-MiniLM-L6-v2",  # Model for text embeddings
    aws_credentials=None  # Optional AWS credentials for S3 access
)
```

#### Common Methods

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
- **Scanned Documents**: Process historical or legacy documents with OCR capabilities

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
  - pytesseract (for OCR support)
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
- Thanks to the developers of PyMuPDF, sentence-transformers, FAISS, and Tesseract for their excellent libraries 