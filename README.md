# **Project Report**
## **AgriTech - Agriculture Knowledge Assistant - A Role-Based Access Control System**

## **Project Overview**
This project implements an advanced **Retrieval-Augmented Generation (RAG)** system tailored for multi-role agriculture environments. The system uses **static role-based access control (RBAC)** with pre-configured users and roles, eliminating the need for database setup. Users can upload documents (Markdown, CSV), and the system retrieves answers based on the user's role. Queries are classified and routed accordingly — SQL-type queries are translated to SQL using an LLM and executed on DuckDB, while RAG-type queries are answered via the retrieval-augmented generation pipeline, and responses are enhanced by reranking and evaluated for quality. The architecture includes:


# Key Points
* Use any of the pre-configured usernames and passwords to log in
* The system will automatically load and index documents from the resources_2 folder
* Users can only access documents based on their assigned role
* The project now has a centralized secrets management system located in `app/rag_utils/secrets.py` that provides: Secure storage of API keys, Environment variable support, Backward compatibility for existing code, Utility functions for key management
* if library installation fails with python use alternate solution as 'Conda'

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Virtual environment (recommended)

## Step-by-Step Installation
1. clone the project

2. Create and Activate Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate
```

2. Upgrade pip and setuptools

```bash
# Upgrade pip to latest version
pip install --upgrade pip

# Install/upgrade setuptools and wheel
pip install --upgrade setuptools wheel
```

3. Run setup script to configure environment
```bash
python setup_environment.py
```

This will create a `.env` file with all required configuration. You'll need to edit it and add your actual API keys.

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Verify Installation

```bash
# Check if packages are installed
pip list

# Test imports
python -c "import fastapi, streamlit, pandas, duckdb; print('All packages imported successfully!')"
```

### 6. Configure API Keys
Edit the `.env` file created by the setup script and add your actual API keys:

- **OpenAI API Key**: Get from [OpenAI Platform](https://platform.openai.com/api-keys)
- **Grow AI API Key**: Get from [Grow AI](https://grow.ai/)
- **Cohere API Key**: Get from [Cohere](https://cohere.ai/)
- **LangSmith API Key**: Get from [LangSmith](https://smith.langchain.com/)

**Optional**: Generate secure random keys for SECRET_KEY and JWT_SECRET_KEY:
```bash
python generate_keys.py
```

After editing the `.env` file, run the setup script again to validate your configuration:
```bash
python setup_environment.py
```

### 7. Validate Configuration
You can also check your configuration status at any time using the secrets module:
```bash
python -c "from app.backend.rag_utils.secrets import print_config_status; print_config_status()"
```

This will show you exactly which configuration values are missing or using default values.

### 8. Start the application
```bash
python run_app.py
```

### 9. Check if directories exist
```bash
ls -la static/ chroma_db/ resources_2/
```

### 10.0 TestCase Command (Optional)
```bash
# For --html, --self-contained-html
pip install pytest-html

# --video
pip install pytest-playwright
playwright install  # installs browser binaries

# Testcase command
pytest tests/test_rbac_application.py::test_rbac_application_login_and_navigation -v -s --html=report_rbac_final.html --self-contained-html

# Playwright Code
@pytest.fixture(scope="function")
def context(browser):
    return browser.new_context(record_video_dir="videos/")

# Video
pytest tests/test_rbac_application.py -v -s --html=report_rbac_final.html --self-contained-html
```

### 10.1 TestCase Command (Optional)
```bash
# Install dependencies
pip install pytest pytest-playwright fastapi httpx

# Install Playwright browsers
playwright install

# Run all tests
python run_tests.py

# Run only unit tests
python run_tests.py --type unit

# Run only integration tests  
python run_tests.py --type integration
```

### 10.2 TestCase Command (Optional) - For html report
```bash
# Install dependencies
pip install pytest-html

# Basic HTML report
pytest --html=report.html tests/

# HTML report with CSS styling
pytest --html=report.html --css=assets/style.css tests/

# HTML report with additional metadata
pytest --html=report.html --self-contained-html tests/
# -----
# Generate HTML report with the updated runner
python run_tests.py --html

# Generate HTML report with coverage
python run_tests.py --html --coverage

# Generate comprehensive HTML report
python test/generate_report.py

# Generate unit test report only
python test/generate_report.py --type unit

# Generate summary report with all test types
python test/generate_report.py --type summary
```

### 11. Remove chroma db due to corruputed
```bash
rm -rf chroma_db/*
```


# USER LOGIN
- Username: `admin`, Password: `admin`
- Username: `agriculture_expert`, Password: `agriculture_expert`
- Username: `farmer`, Password: `farmer`
- Username: `field_worker`, Password: `field_worker`
- Username: `finance_officer`, Password: `finance_officer`
- Username: `hr_manager`, Password: `hr_manager`
- Username: `market_analyst`, Password: `market_analyst`
- Username: `sales_person`, Password: `sales_person`
- Username: `supply_chain_manager`, Password: `supply_chain_manager`


# Environment Configuration

The project uses a `.env` file for configuration. The setup script will create this file automatically, but you can also create it manually by copying `env.example` to `.env`.

## Required Environment Variables

### API Keys (Required)
- `OPENAI_API_KEY`: Your OpenAI API key
- `GROW_API_KEY`: Your Grow AI API key  
- `COHERE_API_KEY`: Your Cohere API key
- `LANGSMITH_API_KEY`: Your LangSmith API key

### Security Settings (Required)
- `SECRET_KEY`: Secret key for the application (generate a secure random key)
- `JWT_SECRET_KEY`: Secret key for JWT tokens (generate a secure random key)

### Application Configuration (Required)
- `ENVIRONMENT`: Environment name (e.g., "development", "production")
- `DEBUG`: Debug mode (true/false)
- `DATABASE_URL`: Database connection string
- `CHROMA_PERSIST_DIRECTORY`: Directory for ChromaDB persistence
- `EMBEDDING_MODEL_NAME`: Name of the embedding model to use
- `LLM_MODEL_NAME`: Name of the LLM model to use
- `OPENAI_RATE_LIMIT`: Rate limit for OpenAI API calls
- `GROW_RATE_LIMIT`: Rate limit for Grow AI API calls
- `COHERE_RATE_LIMIT`: Rate limit for Cohere API calls

## Security Notes

- **Never commit your `.env` file to version control**
- The `.env` file is already in `.gitignore`
- For production, use environment variables instead of `.env` files
- Generate secure random keys for SECRET_KEY and JWT_SECRET_KEY

## Generating Secure Keys

To generate secure random keys for SECRET_KEY and JWT_SECRET_KEY, use the provided script:

```bash
python generate_keys.py
```

This will generate cryptographically secure random keys that you can copy to your `.env` file.

# Reference Links
- [OpenAI Platform](https://platform.openai.com/api-keys)
- [LangSmith](https://smith.langchain.com/)
- [Cohere](https://cohere.ai/)
- [Grow AI](https://grow.ai/)



# Troubleshooting
### 1. OpenAI Key Error - 401 Unauthorized
### 2. Document Upload Issues or 500 Internal server error
**Possible Causes**:
- Missing OpenAI API key
- File size too large (max 50MB)
- Unsupported file type (only .csv, .md, .txt, .pdf allowed)

### 6. Database Issues
**Solution**:
1. Ensure `static/data` directory exists
2. Check file permissions
3. Restart the application

### Issue 2: Build errors for numpy/pandas

**Solution:**
```bash
# Install pre-compiled wheels
pip install --only-binary=all numpy pandas

# Or use conda instead of pip
conda install numpy pandas
```

### Issue 3: DuckDB installation fails

**Solution:**
```bash
# Try installing from conda
conda install -c conda-forge duckdb

# Or use pre-compiled wheel
pip install --only-binary=all duckdb
```

### Issue 4: Permission errors

**Solution:**
```bash
# Use --user flag
pip install --user -r requirements-simple.txt

# Or use virtual environment (recommended)
```

# Testing
* For Field worker
curl -X POST "http://localhost:8000/chat" -H "Content-Type: application/json" -d '{"question": "How to manage soil health for better crop production?"}' -u "field_worker:field_worker"

* For Finance officer
curl -X POST "http://localhost:8000/chat" -H "Content-Type: application/json" -d '{"question": "What are the financial considerations for crop investment?"}' -u "finance_officer:finance_officer"

* For Farmer
curl -X POST "http://localhost:8000/chat" -H "Content-Type: application/json" -d '{"question": "What are the employee salary records?"}' -u "farmer:farmer"

* Test import library
python -c "from app.backend.main import chat; import asyncio; print('Testing backend/main.py validation...')"

* Health check
curl -s http://localhost:8000/health

* 
pytest tests/test_chatbot.py --video=on -v
ls -la videos/
Now let's run this test with video recording enabled:
pytest tests/test_video.py::test_simple_video_recording --video=on -v
ls -lh videos/*.webm
playwright install
pytest tests/test_video.py::test_video_with_context --video=on -v
pytest tests/test_video.py --video=on --html=report_with_video.html --self-contained-html
pip install pytest-html
pytest tests/test_video.py --video=on --html=report_with_video.html --self-contained-html
ls -la report_with_video.html
pytest --help | grep -A 5 -B 5 video
pytest tests/test_video.py::test_video_with_context --video=on --html=report_with_video_fixed.html --self-contained-html
pytest tests/test_video.py::test_video_with_context --video=on --html=report_with_video_fixed.html --self-contained-html
pytest tests/test_video.py::test_video_with_context --video=on --html=report_with_video_fixed.html --self-contained-html
pytest tests/test_video.py::test_video_with_context --video=on --html=report_with_video_fixed.html --self-contained-html
ls -la videos/7e20c81b144f736c25823d4b9c340df8.webm
open report_with_video_fixed.html
-----
pytest tests/test_rbac_debug.py::test_debug_page_content --video=on -v -s
pytest tests/test_rbac_application.py::test_rbac_application_login_and_navigation --video=on --html=report_rbac_final.html --self-contained-html -v -s

pytest tests/test_rbac_application.py::test_rbac_application_login_and_navigation --video=on --html=report_rbac_final.html --self-contained-html -v -s


# Other commands
```bash
# Terminate the server
pkill -f "uvicorn" && pkill -f "python run_app.py" 

# Kill processes on specific ports
lsof -ti:8000 | xargs kill -9  # For FastAPI
lsof -ti:8501 | xargs kill -9  # For Streamlit

# Run both backend and frontend
python run_app.py

# Run only backend
python run_app.py --backend
# python -m uvicorn app.backend.main:app --host 0.0.0.0 --port 8000

# Run only frontend
python run_app.py --frontend
# streamlit run app/frontend/ui.py --server.port 8501 --server.address localhost

# Check dependencies
python run_app.py --check

# 
conda install -c conda-forge duckdb -y
```

# **Query Samples**
1. What are the best practices for rice cultivation in tropical regions? -- Agriculture Expert
2. How should I manage soil fertility for wheat farming? -- Farmer
3. What safety protocols should field workers follow during pesticide application? -- Field Worker
4. What is the current market price trend for corn in the region? -- Market Analysis
5. How can I optimize the supply chain for vegetable distribution? -- Supply Chain Manager
6. What are the financial implications of switching to organic farming? -- Finance Officer

# Roles and Permissions
- **Admin**: Access to all documents across all agriculture departments
- **Agriculture Expert**: Access to agriculture expert knowledge and technical farming guidance
- **Farmer**: Access to farming practices, crop management, and field operations
- **Field Worker**: Access to field operations, equipment maintenance, and safety protocols
- **Finance Officer**: Access to financial data, pricing, and cost analysis
- **HR**: Access to HR documents, employee management, and workforce data
- **Market Analysis**: Access to market trends, price analysis, and demand forecasting
- **Sales Person**: Access to sales data, customer information, and market insights
- **Supply Chain Manager**: Access to logistics, distribution, and supply chain information


# **Tech Stack**
 * AI/LLM: OpenAI GPT-4o, LangChain
 * Backend: FastAPI, DuckDB
 * Frontend: Streamlit
 * Vector DB: Chroma DB
 * File Support: Markdown, CSV
 * Access Control: Static RBAC (no database required)
 * Testing: Pytest, Playwright

# API Endpoints
- `GET /login` - User authentication
- `GET /roles` - List available roles
- `GET /available-docs` - Get documents accessible to the authenticated user
- `POST /upload-docs` - Upload new documents (Admin only)
- `POST /chat` - Chat with the RAG system


# Query Classification Module**
| Mode    | Triggered When              | Engine            | Example Query                     |
| ------- | --------------------------- | ----------------- | --------------------------------- |
| **RAG** | General, text-based queries | Chroma DB + LLM   | “Summarize this finance document” |
| **SQL** | Structured/tabular queries  | DuckDB SQL engine | “List employees earning over $50k”|

# Concepts 
## **RAG Agent Path**
* The **RAG Agent** retrieves relevant information from documents using **Vector Search** (e.g., via ChromaDB).
* The LLM then generates a coherent answer from the retrieved chunks.
* The final **RAG-based response** is sent back to the user.

## Module Responsibilities

### `app/backend/main.py`
- FastAPI application setup
- API route definitions
- Request/response handling
- Integration between different modules

### `app/config.py`
- Environment variables
- Configuration constants
- Path definitions
- Feature flags

### `app/models.py`
- Pydantic data models
- Request/response schemas
- Data validation rules
- Type definitions

### `app/auth.py`
- User authentication
- Role-based access control
- Password management
- Security utilities

### `app/database.py`
- Database connections
- Query execution
- Table management
- Data persistence

### `app/frontend/ui.py`
- Main Streamlit application
- Page routing
- State management
- API integration

### `app/frontend/ui_components.py`
- Reusable UI components
- CSS styling
- Layout functions
- Design system

### `app/utils.py`
- File operations
- Validation functions
- Formatting utilities
- Common helpers

### `app/rag_utils/`
- RAG implementation
- Vector database operations
- Query processing
- AI model integration