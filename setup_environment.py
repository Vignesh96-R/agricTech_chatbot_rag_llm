#!/usr/bin/env python3
"""
Setup script for Agriculture RBAC-Project
This script helps configure the environment and check for common issues.
Run this script to create a .env file with all required API keys.
"""

import os
import sys
from pathlib import Path

def check_environment():
    """Check if environment is properly configured."""
    print("🔍 Checking environment configuration...")
    
    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found. Creating one...")
        create_env_file()
    else:
        print("✅ .env file found")
        print("   You can edit it manually or delete it to recreate with this script")
    
    # Check all required API keys
    required_keys = [
        "OPENAI_API_KEY",
        "GROW_API_KEY", 
        "COHERE_API_KEY",
        "LANGSMITH_API_KEY"
    ]
    
    missing_keys = []
    for key in required_keys:
        api_key = os.getenv(key)
        if not api_key or api_key.startswith("your_") or api_key.startswith("sk-") and len(api_key) < 20:
            print(f"❌ {key} not configured or invalid")
            missing_keys.append(key)
        else:
            print(f"✅ {key} configured")
    
    if missing_keys:
        print(f"\n⚠️  Missing or invalid API keys: {', '.join(missing_keys)}")
        print("   Please edit .env file and add your valid API keys")
        print("   Get your API keys from:")
        print("   - OpenAI: https://platform.openai.com/api-keys")
        print("   - Grow: https://grow.ai/")
        print("   - Cohere: https://cohere.ai/")
        print("   - LangSmith: https://smith.langchain.com/")
    else:
        print("\n✅ All required API keys are configured!")
    
    # Check other required configuration values
    print("\n🔧 Checking other configuration values...")
    
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
            print(f"❌ {config_key} not configured or using default value")
            missing_config.append(config_key)
        else:
            print(f"✅ {config_key} configured")
    
    if missing_config:
        print(f"\n⚠️  Missing or default configuration: {', '.join(missing_config)}")
        print("   Please edit .env file and configure these values")
        if "SECRET_KEY" in missing_config or "JWT_SECRET_KEY" in missing_config:
            print("   Use 'python generate_keys.py' to generate secure keys")
    else:
        print("\n✅ All configuration values are properly configured!")
    
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

def install_dependencies():
    """Install required dependencies."""
    print("📦 Installing dependencies...")
    os.system("pip install -r requirements.txt")

def validate_env_file():
    """Validate the .env file after user has edited it."""
    print("\n🔍 Validating .env file...")
    
    # Reload environment variables
    from dotenv import load_dotenv
    load_dotenv(override=True)
    
    # Import secrets module to check configuration
    try:
        from app.rag_utils.secrets import print_config_status
        print_config_status()
    except ImportError as e:
        print(f"❌ Error importing secrets module: {e}")
        print("   Make sure you're running from the project root directory")

def main():
    """Main setup function."""
    print("🌾 Agriculture RBAC-Project Setup")
    print("=" * 50)
    
    check_environment()
    
    print("\n📋 Next steps:")
    print("1. Edit .env file and add your actual API keys")
    print("2. Run this script again to validate your configuration")
    print("3. Run: python run_app.py")
    print("4. Open http://localhost:8501 in your browser")
    print("5. Login with username: admin, password: admin")
    
    print("\n💡 Tips:")
    print("- Keep your .env file secure and never commit it to version control")
    print("- For production, use environment variables instead of .env files")
    print("- Generate secure random keys for SECRET_KEY and JWT_SECRET_KEY")

if __name__ == "__main__":
    main()
