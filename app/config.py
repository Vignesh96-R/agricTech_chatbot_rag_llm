"""
Configuration settings for the Agriculture RBAC-Project application.

This module contains all configuration constants, environment variables,
and settings used throughout the application.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory configuration
BASE_DIR = Path(__file__).parent.parent
APP_DIR = BASE_DIR / "app"
RESOURCES_DIR = BASE_DIR / "resources_2"  # Updated to use resources_2 for agriculture data
STATIC_DIR = BASE_DIR / "static"
UPLOADS_DIR = STATIC_DIR / "uploads"
CHROMA_DIR = BASE_DIR / "chroma_db"

# Database configuration
DUCKDB_DIR = STATIC_DIR / "data"
DUCKDB_PATH = DUCKDB_DIR / "structured_queries.duckdb"

# API configuration
API_HOST = os.getenv("API_HOST", "localhost")
API_PORT = int(os.getenv("API_PORT", "8000"))
API_URL = f"http://{API_HOST}:{API_PORT}"

# Import secrets - handle import gracefully for different contexts
try:
    # Try relative import first (when imported as part of app package)
    from .rag_utils.secrets import (
        OPENAI_API_KEY, 
        GROW_API_KEY, 
        LANGSMITH_API_KEY, 
        COHERE_API_KEY,
        LANGSMITH_TRACING_V2,
        LANGSMITH_ENDPOINT,
        LANGSMITH_PROJECT
    )
except ImportError:
    try:
        # Try absolute import (when running from app directory)
        from rag_utils.secrets import (
            OPENAI_API_KEY, 
            GROW_API_KEY, 
            LANGSMITH_API_KEY, 
            COHERE_API_KEY,
            LANGSMITH_TRACING_V2,
            LANGSMITH_ENDPOINT,
            LANGSMITH_PROJECT
        )
    except ImportError:
        # Fallback to environment variables only
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        GROW_API_KEY = os.getenv("GROW_API_KEY")
        LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
        COHERE_API_KEY = os.getenv("COHERE_API_KEY")
        LANGSMITH_TRACING_V2 = os.getenv("LANGSMITH_TRACING_V2", "true")
        LANGSMITH_ENDPOINT = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
        LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "agriculture-rbac-project")

# OpenAI configuration
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

# Authentication configuration - Updated for agriculture roles
STATIC_USERS = {
    "admin": {
        "password": "$2b$12$DBs822GpIKPeNm/8Ar6iCu9E807p4vd3xL1/1YAGBMAzy3QUqk08y",
        "role": "Admin"
    },
    "agriculture_expert": {
        "password": "$2b$12$lVrI3SUzq1jRJ9mwbWYmT.nk05cpnmoOFHcOcY6v6eKNh8KXvGVmq",
        "role": "Agriculture Expert"
    },
    "farmer": {
        "password": "$2b$12$OT4zKqURPlqKf1ElXhUzTuUVJtaPfGQoEH1YFTtgjp1gfxw5sdz3.",
        "role": "Farmer"
    },
    "field_worker": {
        "password": "$2b$12$35Yo1.ZaX6JlC6qubL4tt.Yud86QTW6BO8.tKO8JWkUP31p9xSqQK",
        "role": "Field Worker"
    },
    "finance_officer": {
        "password": "$2b$12$0qxESZb3AkKpNOeLjYPhWeOvR/s2BO9rQJLES/061pwt5Q/Ts.tfi",
        "role": "Finance Officer"
    },
    "hr_manager": {
        "password": "$2b$12$FHi5f.nh9NMEdLbI0y4svuxxkdBY3Bi54ijLK7TFDdLdeW07lS1Jq",
        "role": "HR"
    },
    "market_analyst": {
        "password": "$2b$12$s49At2lFtrxBFbQnJ4GDsefbyz5Rn9QcRuNQAcGt5G37GkopAB38O",
        "role": "Market Analysis"
    },
    "sales_person": {
        "password": "$2b$12$grTAbvMd4BS5IXQoAaTqBeG96sF/9YETa3zfPIVTfZM1/BkGfsW42",
        "role": "Sales Person"
    },
    "supply_chain_manager": {
        "password": "$2b$12$fG0Yu6vSvfy3e4wVsRUYVuvcFC9Sxl570X7NY0zfmVaKiwwb6WNfK",
        "role": "Supply Chain Manager"
    }
}

# Role configuration - Updated for agriculture roles
AVAILABLE_ROLES = [
    "Admin", 
    "Agriculture Expert", 
    "Farmer", 
    "Field Worker", 
    "Finance Officer", 
    "HR", 
    "Market Analysis", 
    "Sales Person", 
    "Supply Chain Manager"
]

# Role-based document access mapping - Updated for agriculture roles
ROLE_DOCS_MAPPING = {
    "Admin": ["Agriculture Expert", "Farmer", "Field Worker", "Finance Officer", "HR", "Market Analysis", "Sales Person", "Supply Chain Manager"],
    "Agriculture Expert": ["Agriculture Expert"],
    "Farmer": ["Farmer"],
    "Field Worker": ["Field Worker"],
    "Finance Officer": ["Finance Officer"],
    "HR": ["HR"],
    "Market Analysis": ["Market Analysis"],
    "Sales Person": ["Sales Person"],
    "Supply Chain Manager": ["Supply Chain Manager"]
}

# File upload configuration
ALLOWED_EXTENSIONS = [".csv", ".md", ".txt", ".pdf"]
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# RAG configuration
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")

# LangSmith configuration for tracing
LANGSMITH_TRACING_V2 = LANGSMITH_TRACING_V2
LANGSMITH_ENDPOINT = LANGSMITH_ENDPOINT
LANGSMITH_PROJECT = LANGSMITH_PROJECT

# SQL query configuration
FORBIDDEN_SQL_KEYWORDS = ["insert", "update", "delete", "drop", "alter", "create", "truncate"]

# Ensure directories exist
def ensure_directories():
    """Create necessary directories if they don't exist."""
    directories = [
        DUCKDB_DIR,
        UPLOADS_DIR,
        CHROMA_DIR,
        RESOURCES_DIR / "agriculture expert",
        RESOURCES_DIR / "farmer",
        RESOURCES_DIR / "field worker",
        RESOURCES_DIR / "finance officer",
        RESOURCES_DIR / "hr",
        RESOURCES_DIR / "market analysis",
        RESOURCES_DIR / "salesperson",
        RESOURCES_DIR / "supply chain manager"
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

# Initialize directories on import
ensure_directories()
