"""
Secrets and API keys configuration.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# API Keys - Must be loaded from environment variables
GROW_API_KEY = os.getenv("GROW_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

# LangSmith configuration
LANGSMITH_TRACING_V2 = os.getenv("LANGSMITH_TRACING_V2", "true")
LANGSMITH_ENDPOINT = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "agriculture-rbac-project")

# Additional configuration
ENVIRONMENT = os.getenv("ENVIRONMENT")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# Security settings
SECRET_KEY = os.getenv("SECRET_KEY")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

# Database secrets (if needed)
DATABASE_URL = os.getenv("DATABASE_URL")

# RAG-specific configuration
CHROMA_PERSIST_DIRECTORY = os.getenv("CHROMA_PERSIST_DIRECTORY")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME")
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME")

# Rate limiting and API quotas
OPENAI_RATE_LIMIT = os.getenv("OPENAI_RATE_LIMIT")
GROW_RATE_LIMIT = os.getenv("GROW_RATE_LIMIT")
COHERE_RATE_LIMIT = os.getenv("COHERE_RATE_LIMIT")

def get_api_key(service_name: str) -> str:
    """
    Get API key for a specific service.
    """
    api_keys = {
        'openai': OPENAI_API_KEY,
        'grow': GROW_API_KEY,
        'cohere': COHERE_API_KEY,
        'langsmith': LANGSMITH_API_KEY
    }
    
    return api_keys.get(service_name.lower())

def validate_api_keys() -> dict:
    """
    Validate that all required API keys are present.
    """
    validation_results = {
        'openai': bool(OPENAI_API_KEY),
        'grow': bool(GROW_API_KEY),
        'cohere': bool(COHERE_API_KEY),
        'langsmith': bool(LANGSMITH_API_KEY)
    }
    
    return validation_results

def check_required_keys() -> list:
    """
    Check which required API keys are missing.
    """
    required_keys = ['OPENAI_API_KEY', 'GROW_API_KEY', 'COHERE_API_KEY', 'LANGSMITH_API_KEY']
    missing_keys = []
    
    for key in required_keys:
        if not os.getenv(key):
            missing_keys.append(key)
    
    return missing_keys

def check_required_config() -> list:
    """
    Check which required configuration values are missing or using defaults.
    """
    config_checks = [
        ("ENVIRONMENT", "development"),
        ("DEBUG", "true"),
        ("SECRET_KEY", "your_secret_key_here_change_in_production"),
        ("JWT_SECRET_KEY", "your_jwt_secret_key_here_change_in_production"),
        ("DATABASE_URL", "sqlite:///./agriculture_rbac.db"),
        ("CHROMA_PERSIST_DIRECTORY", "./chroma_db"),
        ("EMBEDDING_MODEL_NAME", "text-embedding-ada-002"),
        ("LLM_MODEL_NAME", "gpt-4"),
        ("OPENAI_RATE_LIMIT", "100"),
        ("GROW_RATE_LIMIT", "100"),
        ("COHERE_RATE_LIMIT", "100")
    ]
    
    missing_config = []
    for config_key, default_value in config_checks:
        config_value = os.getenv(config_key)
        if not config_value or config_value == default_value:
            missing_config.append(config_key)
    
    return missing_config

def validate_all_configuration() -> dict:
    """
    Validate all configuration including API keys and other settings.
    """
    api_validation = validate_api_keys()
    missing_keys = check_required_keys()
    missing_config = check_required_config()
    
    return {
        'api_keys': api_validation,
        'missing_api_keys': missing_keys,
        'missing_config': missing_config,
        'all_valid': len(missing_keys) == 0 and len(missing_config) == 0
    }

def get_config_summary() -> dict:
    """
    Get a summary of the current configuration.
    """
    validation = validate_all_configuration()
    
    return {
        'environment': ENVIRONMENT,
        'debug': DEBUG,
        'api_keys_configured': validation['api_keys'],
        'missing_api_keys': validation['missing_api_keys'],
        'missing_config': validation['missing_config'],
        'all_valid': validation['all_valid'],
        'chroma_directory': CHROMA_PERSIST_DIRECTORY,
        'embedding_model': EMBEDDING_MODEL_NAME,
        'llm_model': LLM_MODEL_NAME
    }
