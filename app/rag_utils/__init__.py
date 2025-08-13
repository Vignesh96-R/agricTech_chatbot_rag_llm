"""
RAG Utilities Package for Agriculture RBAC-Project.

This package contains utilities for RAG (Retrieval-Augmented Generation) operations,
including query classification, CSV querying, and configuration management.
"""

from .secrets import (
    GROW_API_KEY,
    OPENAI_API_KEY,
    LANGSMITH_API_KEY,
    COHERE_API_KEY,
    get_api_key,
    validate_api_keys,
    get_config_summary
)

# Note: Individual RAG components can be imported directly as needed
# from .query_classifier import QueryClassifier
# from .csv_query import CSVQueryEngine
# from .rag_chain import RAGChain
# from .rag_module import RAGModule

__all__ = [
    # Secrets and configuration
    'GROW_API_KEY',
    'OPENAI_API_KEY',
    'LANGSMITH_API_KEY',
    'COHERE_API_KEY',
    'get_api_key',
    'validate_api_keys',
    'get_config_summary'
]

# Version information
__version__ = "1.0.0"
