#!/usr/bin/env python
"""
Script to create a simple architecture diagram for SnipRAG.
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path

def create_architecture_diagram(output_path="docs/sniprag_architecture.png"):
    """Create a simple architecture diagram for SnipRAG."""
    # Set up the figure with a clean style
    plt.style.use('seaborn-v0_8-white')
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis('off')
    
    # Define colors
    colors = {
        'blue': '#4287f5',
        'green': '#42c5a0',
        'pink': '#e06377',
        'arrow': '#555555',
        'background': '#f9f9f9',
        'text': '#333333'
    }
    
    # Title
    ax.text(5, 5.6, 'SnipRAG Architecture', 
            fontsize=24, fontweight='bold', color=colors['text'],
            ha='center', va='center')
    
    # Add boxes
    # PDF Processing Pipeline
    pdf_box = patches.FancyBboxPatch((0.7, 3), 3.6, 2,
                                    boxstyle=patches.BoxStyle("Round", pad=0.3),
                                    facecolor=colors['background'], edgecolor=colors['blue'],
                                    linewidth=2, alpha=0.9)
    ax.add_patch(pdf_box)
    ax.text(2.5, 4.7, 'PDF Processing Pipeline',
            fontsize=14, fontweight='bold', color=colors['blue'],
            ha='center', va='center')
    
    # Search Pipeline
    search_box = patches.FancyBboxPatch((5.7, 3), 3.6, 2,
                                      boxstyle=patches.BoxStyle("Round", pad=0.3),
                                      facecolor=colors['background'], edgecolor=colors['blue'],
                                      linewidth=2, alpha=0.9)
    ax.add_patch(search_box)
    ax.text(7.5, 4.7, 'Search Pipeline',
            fontsize=14, fontweight='bold', color=colors['blue'],
            ha='center', va='center')
    
    # Page Images Storage
    storage_box = patches.FancyBboxPatch((0.7, 1), 3.6, 1,
                                       boxstyle=patches.BoxStyle("Round", pad=0.3),
                                       facecolor=colors['background'], edgecolor=colors['green'],
                                       linewidth=2, alpha=0.9)
    ax.add_patch(storage_box)
    ax.text(2.5, 1.5, 'Page Images Storage',
            fontsize=14, fontweight='bold', color=colors['green'],
            ha='center', va='center')
    
    # Results
    result_box = patches.FancyBboxPatch((5.7, 1), 3.6, 1,
                                      boxstyle=patches.BoxStyle("Round", pad=0.3),
                                      facecolor=colors['background'], edgecolor=colors['pink'],
                                      linewidth=2, alpha=0.9)
    ax.add_patch(result_box)
    ax.text(7.5, 1.5, 'Results: Text Match + Image Snippet',
            fontsize=14, fontweight='bold', color=colors['pink'],
            ha='center', va='center')
    
    # Add steps in the PDF Pipeline
    pdf_steps = [
        "PDF Document",
        "Text + Coordinates",
        "Text Chunks",
        "Text Embeddings",
        "Vector Index"
    ]
    
    # Add steps in the Search Pipeline
    search_steps = [
        "Query",
        "Query Embedding",
        "Vector Search",
        "Matching Text",
        "Coordinate Lookup"
    ]
    
    # Draw PDF steps
    for i, step in enumerate(pdf_steps):
        y_pos = 4.4 - i * 0.3
        ax.text(2.5, y_pos, step, fontsize=10, ha='center', va='center')
        if i < len(pdf_steps) - 1:
            ax.arrow(2.5, y_pos - 0.1, 0, -0.1, head_width=0.1, head_length=0.1,
                    color=colors['arrow'], linewidth=1)
    
    # Draw Search steps
    for i, step in enumerate(search_steps):
        y_pos = 4.4 - i * 0.3
        ax.text(7.5, y_pos, step, fontsize=10, ha='center', va='center')
        if i < len(search_steps) - 1:
            ax.arrow(7.5, y_pos - 0.1, 0, -0.1, head_width=0.1, head_length=0.1,
                    color=colors['arrow'], linewidth=1)
    
    # Connect the components with arrows
    # PDF Pipeline to Search Pipeline
    ax.arrow(4.4, 4, 1.1, 0, head_width=0.1, head_length=0.2,
            color=colors['arrow'], linewidth=1.5)
    
    # PDF Pipeline to Page Images Storage
    ax.arrow(2.5, 3, 0, -0.9, head_width=0.1, head_length=0.2,
            color=colors['arrow'], linewidth=1.5, linestyle='--')
    
    # Search Pipeline to Results
    ax.arrow(7.5, 3, 0, -0.9, head_width=0.1, head_length=0.2,
            color=colors['arrow'], linewidth=1.5)
    
    # Page Images Storage to Results
    ax.arrow(4.4, 1.5, 1.1, 0, head_width=0.1, head_length=0.2,
            color=colors['arrow'], linewidth=1.5, linestyle='--')
    
    # Save the figure
    plt.tight_layout(pad=1.2)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"Architecture diagram created at: {output_path}")
    return output_path

if __name__ == "__main__":
    create_architecture_diagram() 