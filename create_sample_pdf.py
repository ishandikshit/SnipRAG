#!/usr/bin/env python
"""
Create a sample PDF file for testing SnipRAG.
"""

import os
import fitz  # PyMuPDF

def create_sample_pdf(output_path="samples/sample_document.pdf"):
    """Create a sample PDF with some text for testing."""
    # Create a new PDF
    doc = fitz.open()
    
    # Add a title page
    page = doc.new_page(width=612, height=792)  # Letter size
    
    # Add a title
    title = "Sample Document for SnipRAG Testing"
    # Calculate text width to center manually
    tw = fitz.get_text_length(title, fontname="Helvetica-Bold", fontsize=20)
    page.insert_text(
        (306 - tw/2, 200),
        title,
        fontsize=20,
        fontname="Helvetica-Bold",
        color=(0, 0, 0)
    )
    
    # Add author
    author = "Created for Demo Purposes"
    tw = fitz.get_text_length(author, fontname="Helvetica", fontsize=14)
    page.insert_text(
        (306 - tw/2, 250),
        author,
        fontsize=14,
        fontname="Helvetica",
        color=(0, 0, 0)
    )
    
    # Add date
    date = "June 2023"
    tw = fitz.get_text_length(date, fontname="Helvetica", fontsize=12)
    page.insert_text(
        (306 - tw/2, 280),
        date,
        fontsize=12,
        fontname="Helvetica",
        color=(0, 0, 0)
    )
    
    # Page 2 - Introduction
    page = doc.new_page(width=612, height=792)
    
    # Section title
    page.insert_text(
        (72, 72),
        "1. Introduction",
        fontsize=16,
        fontname="Helvetica-Bold",
        color=(0, 0, 0)
    )
    
    # Paragraph text
    intro_text = """This document is a sample PDF created for testing the SnipRAG system. SnipRAG is a specialized Retrieval Augmented Generation (RAG) system that not only finds semantically relevant text in PDF documents but also extracts precise image snippets from the areas containing the matching text.

The system is particularly useful for extracting visual context from documents, which helps in better understanding and interpretation of the information. This can be valuable in domains such as legal document analysis, financial report examination, and technical documentation review."""
    
    # Format the text into multiple lines
    for i, line in enumerate(wrap_text(intro_text, 60)):
        page.insert_text(
            (72, 100 + i * 20),
            line,
            fontsize=12,
            fontname="Helvetica",
            color=(0, 0, 0)
        )
    
    # Page 3 - Financial Information with Structured Table
    page = doc.new_page(width=612, height=792)
    
    # Section title
    page.insert_text(
        (72, 72),
        "2. Financial Information",
        fontsize=16,
        fontname="Helvetica-Bold",
        color=(0, 0, 0)
    )
    
    # Introduction to the financial data
    financial_intro = """Below is the quarterly financial performance of the company for the fiscal year 2022:"""
    page.insert_text(
        (72, 100),
        financial_intro,
        fontsize=12,
        fontname="Helvetica",
        color=(0, 0, 0)
    )
    
    # Create a structured table - Header
    headers = ["Quarter", "Revenue", "Expenses", "Profit", "Growth"]
    header_widths = [80, 100, 100, 100, 80]
    col_positions = [72]  # Starting position
    for width in header_widths[:-1]:
        col_positions.append(col_positions[-1] + width)
    
    # Draw table header with background
    header_rect = fitz.Rect(72, 130, 72 + sum(header_widths), 150)
    page.draw_rect(header_rect, color=(0.8, 0.8, 0.9), fill=(0.8, 0.8, 0.9))
    
    # Draw header text
    for i, header in enumerate(headers):
        page.insert_text(
            (col_positions[i] + 5, 145),
            header,
            fontsize=12,
            fontname="Helvetica-Bold",
            color=(0, 0, 0)
        )
    
    # Table data
    data = [
        ["Q1 2022", "$310,000", "$250,000", "$60,000", "4.2%"],
        ["Q2 2022", "$335,000", "$260,000", "$75,000", "5.3%"],
        ["Q3 2022", "$295,000", "$245,000", "$50,000", "3.1%"],
        ["Q4 2022", "$305,000", "$235,000", "$70,000", "4.8%"],
        ["Total", "$1,245,000", "$990,000", "$255,000", "12.3%"]
    ]
    
    # Draw table rows with alternating background
    for i, row in enumerate(data):
        y_pos = 150 + i * 25
        
        # Draw row background (alternating)
        if i % 2 == 0:
            row_rect = fitz.Rect(72, y_pos, 72 + sum(header_widths), y_pos + 25)
            page.draw_rect(row_rect, color=(0.95, 0.95, 0.95), fill=(0.95, 0.95, 0.95))
        
        # Draw border lines
        if i == len(data) - 1:  # Total row with heavier line
            line_y = y_pos
            page.draw_line((72, line_y), (72 + sum(header_widths), line_y), color=(0, 0, 0), width=1.5)
        
        # Highlight the Total row
        if i == len(data) - 1:
            for j, cell in enumerate(row):
                page.insert_text(
                    (col_positions[j] + 5, y_pos + 17),
                    cell,
                    fontsize=12,
                    fontname="Helvetica-Bold",
                    color=(0, 0, 0)
                )
        else:
            for j, cell in enumerate(row):
                page.insert_text(
                    (col_positions[j] + 5, y_pos + 17),
                    cell,
                    fontsize=12,
                    fontname="Helvetica",
                    color=(0, 0, 0)
                )
    
    # Draw table border
    table_rect = fitz.Rect(72, 130, 72 + sum(header_widths), 150 + len(data) * 25)
    page.draw_rect(table_rect, color=(0, 0, 0), width=1)
    
    # Add some explanatory text
    explanation = """The financial results presented above are for the fiscal year 2022. The company has shown strong performance despite market challenges, with a 12.3% growth compared to the previous year. The quarterly breakdown shows consistent performance throughout the year."""
    
    for i, line in enumerate(wrap_text(explanation, 60)):
        page.insert_text(
            (72, 300 + i * 20),
            line,
            fontsize=12,
            fontname="Helvetica",
            color=(0, 0, 0)
        )
    
    # Page 4 - Technical Specifications with Comparison Table
    page = doc.new_page(width=612, height=792)
    
    # Section title
    page.insert_text(
        (72, 72),
        "3. Technical Specifications",
        fontsize=16,
        fontname="Helvetica-Bold",
        color=(0, 0, 0)
    )
    
    # Introduction to the technical specs
    tech_intro = """The system architecture employs various technical components. Below is a comparison of the methods used:"""
    page.insert_text(
        (72, 100),
        tech_intro,
        fontsize=12,
        fontname="Helvetica",
        color=(0, 0, 0)
    )
    
    # Create a comparison table - Header
    comp_headers = ["Component", "Method Used", "Alternatives", "Benefits"]
    comp_widths = [120, 120, 120, 180]
    comp_positions = [72]  # Starting position
    for width in comp_widths[:-1]:
        comp_positions.append(comp_positions[-1] + width)
    
    # Draw table header with background
    header_rect = fitz.Rect(72, 130, 72 + sum(comp_widths), 150)
    page.draw_rect(header_rect, color=(0.9, 0.8, 0.8), fill=(0.9, 0.8, 0.8))
    
    # Draw header text
    for i, header in enumerate(comp_headers):
        page.insert_text(
            (comp_positions[i] + 5, 145),
            header,
            fontsize=12,
            fontname="Helvetica-Bold",
            color=(0, 0, 0)
        )
    
    # Table data - technical specifications
    tech_data = [
        ["Text Extraction", "PyMuPDF", "Tesseract OCR", "Precise coordinates for text blocks"],
        ["Semantic Search", "Sentence Transformers", "OpenAI Embeddings", "Accurate semantic matching"],
        ["Vector Database", "FAISS", "Pinecone, Weaviate", "Fast retrieval with similarity search"],
        ["Image Processing", "PIL", "OpenCV", "Simple integration with text coordinates"]
    ]
    
    # Draw table rows
    for i, row in enumerate(tech_data):
        y_pos = 150 + i * 30
        
        # Draw row background (alternating)
        if i % 2 == 0:
            row_rect = fitz.Rect(72, y_pos, 72 + sum(comp_widths), y_pos + 30)
            page.draw_rect(row_rect, color=(0.95, 0.95, 0.95), fill=(0.95, 0.95, 0.95))
        
        # Draw cells
        for j, cell in enumerate(row):
            # Wrap text for the Benefits column
            if j == 3:  # Benefits column
                wrapped = wrap_text(cell, 25)
                for k, line in enumerate(wrapped):
                    page.insert_text(
                        (comp_positions[j] + 5, y_pos + 12 + k * 12),
                        line,
                        fontsize=10,
                        fontname="Helvetica",
                        color=(0, 0, 0)
                    )
            else:
                page.insert_text(
                    (comp_positions[j] + 5, y_pos + 17),
                    cell,
                    fontsize=11,
                    fontname="Helvetica",
                    color=(0, 0, 0)
                )
    
    # Draw table border
    table_rect = fitz.Rect(72, 130, 72 + sum(comp_widths), 150 + len(tech_data) * 30)
    page.draw_rect(table_rect, color=(0, 0, 0), width=1)
    
    # Add vertical lines between columns
    for pos in comp_positions[1:]:
        page.draw_line((pos, 130), (pos, 150 + len(tech_data) * 30), color=(0, 0, 0), width=0.5)
    
    # Add horizontal lines between rows
    for i in range(len(tech_data) + 1):
        y = 150 + i * 30
        page.draw_line((72, y), (72 + sum(comp_widths), y), color=(0, 0, 0), width=0.5)
    
    # Additional technical explanation
    tech_explanation = """The implementation is in Python and leverages several open-source libraries. The key innovation is the precise mapping between semantic text matches and their visual location in the document, allowing for targeted image snippet extraction."""
    
    y_start = 150 + len(tech_data) * 30 + 30
    for i, line in enumerate(wrap_text(tech_explanation, 60)):
        page.insert_text(
            (72, y_start + i * 20),
            line,
            fontsize=12,
            fontname="Helvetica",
            color=(0, 0, 0)
        )
    
    # Save the document
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc.save(output_path)
    doc.close()
    
    print(f"Sample PDF created at: {output_path}")
    return output_path

def wrap_text(text, width):
    """Simple text wrapper to fit text within a given width."""
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        if len(' '.join(current_line + [word])) <= width:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return lines

if __name__ == "__main__":
    create_sample_pdf() 