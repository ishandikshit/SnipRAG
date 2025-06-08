"""
SnipRAG Core module - Retrieval Augmented Generation with image snippets from PDFs.
"""

from .base_engine import BaseSnipRAGEngine
from .semantic_engine import SemanticSnipRAGEngine
from .ocr_engine import OCRSnipRAGEngine

def create_engine(strategy: str = "semantic", **kwargs):
    """
    Factory function to create a SnipRAG engine with the specified strategy.
    
    Args:
        strategy: The extraction strategy to use, either "semantic" or "ocr"
        **kwargs: Additional arguments to pass to the engine constructor
        
    Returns:
        A SnipRAG engine instance
        
    Raises:
        ValueError: If an invalid strategy is specified
    """
    if strategy.lower() == "semantic":
        return SemanticSnipRAGEngine(**kwargs)
    elif strategy.lower() == "ocr":
        return OCRSnipRAGEngine(**kwargs)
    else:
        raise ValueError(f"Invalid strategy: {strategy}. Must be 'semantic' or 'ocr'.") 