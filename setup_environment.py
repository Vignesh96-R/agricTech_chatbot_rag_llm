"""
Environment file generation with screat keys
"""
from pathlib import Path

# Check if environment is properly configured.
def check_environment():
    
    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found. Creating one...")
        create_env_file()
    else:
        print("✅ .env file found")
        print("   You can edit it manually or delete it to recreate with this script")
    
    # Check required directories
    required_dirs = [
        "static/uploads",
        "static/data", 
        "chroma_db",
        "resources_2"
    ]
    
    print("\n📁 Checking required directories...")
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"✅ {dir_path} directory exists")
        else:
            print(f"❌ {dir_path} directory missing")
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            print(f"   Created {dir_path} directory")

def create_env_file():
    """Create a comprehensive .env file with all required configuration."""
    env_content = """# Agriculture RBAC-Project Environment Configuration
# This file contains all sensitive configuration data including API keys
# DO NOT commit this file to version control

# =============================================================================
# API Configuration
# =============================================================================
API_HOST=localhost
API_PORT=8000

# =============================================================================
# Required API Keys (You MUST fill these in)
# =============================================================================

# OpenAI API Key - Get from: https://platform.openai.com/api-keys
OPENAI_API_KEY=your_openai_api_key_here

# Grow AI API Key - Get from: https://grow.ai/
GROW_API_KEY=your_grow_api_key_here

# Cohere API Key - Get from: https://cohere.ai/
COHERE_API_KEY=your_cohere_api_key_here

# LangSmith API Key - Get from: https://smith.langchain.com/
LANGSMITH_API_KEY=your_langsmith_api_key_here

# =============================================================================
# LangSmith Configuration
# =============================================================================
LANGSMITH_TRACING_V2=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_PROJECT=agriculture-rbac-project

# =============================================================================
# Environment Settings
# =============================================================================
ENVIRONMENT=development
DEBUG=true

# =============================================================================
# Security Settings (Generate secure keys for production)
# =============================================================================
SECRET_KEY=your_secret_key_here_change_in_production
JWT_SECRET_KEY=your_jwt_secret_key_here_change_in_production

# =============================================================================
# Database Configuration
# =============================================================================
DATABASE_URL=sqlite:///./agriculture_rbac.db

# =============================================================================
# RAG Configuration
# =============================================================================
CHROMA_PERSIST_DIRECTORY=./chroma_db
EMBEDDING_MODEL_NAME=text-embedding-ada-002
LLM_MODEL_NAME=gpt-4

# =============================================================================
# Rate Limiting
# =============================================================================
OPENAI_RATE_LIMIT=100
GROW_RATE_LIMIT=100
COHERE_RATE_LIMIT=100
"""
    
    with open(".env", "w") as f:
        f.write(env_content)
    print("✅ Created comprehensive .env file")
    print("   Please edit the file and add your actual API keys")

def main():
    check_environment()

if __name__ == "__main__":
    main()