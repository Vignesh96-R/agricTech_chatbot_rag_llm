import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
import io
from unittest.mock import patch, MagicMock

# Add root directory to Python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.main import app

client = TestClient(app)

@pytest.fixture
def admin_auth():
    """Admin user credentials for testing"""
    return ("admin", "admin")

@pytest.fixture
def farmer_auth():
    """Farmer user credentials for testing"""
    return ("farmer", "farmer")

@pytest.fixture
def finance_officer_auth():
    """Finance Officer user credentials for testing"""
    return ("finance_officer", "finance_officer")

@pytest.fixture
def hr_auth():
    """HR user credentials for testing"""
    return ("hr_manager", "hr_manager")

def test_upload_csv_document(admin_auth):
    """Test uploading CSV document with admin access"""
    content = b"Name,Role,Department\nAdmin,Compliant,Agriculture\nFarmer,Active,Field"
    file = io.BytesIO(content)

    res = client.post(
        "/upload-docs",
        auth=admin_auth,
        files={"file": ("test.csv", file, "text/csv")},
        data={"role": "Admin"}
    )

    assert res.status_code == 200
    assert "uploaded successfully" in res.json()["message"]

def test_upload_markdown_document(admin_auth):
    """Test uploading Markdown document with admin access"""
    content = b"# Agriculture Policies\nFollow sustainable farming guidelines."
    file = io.BytesIO(content)

    res = client.post(
        "/upload-docs",
        auth=admin_auth,
        files={"file": ("guide.md", file, "text/markdown")},
        data={"role": "Admin"}
    )

    assert res.status_code == 200
    assert "uploaded successfully" in res.json()["message"]

@patch("app.main.detect_query_type_llm", return_value="RAG")
@patch("app.main.ask_rag", return_value={"answer": "This is a RAG response about agriculture"})
def test_chat_rag_mode(mock_ask_rag, mock_detect, admin_auth):
    """Test chat functionality in RAG mode"""
    res = client.post(
        "/chat",
        auth=admin_auth,
        json={"question": "What are the best farming practices?"}
    )
    assert res.status_code == 200
    assert res.json()["mode"] == "RAG"
    assert res.json()["answer"] == "This is a RAG response about agriculture"

@patch("app.main.detect_query_type_llm", return_value="SQL")
@patch("app.main.ask_csv", return_value={"answer": "Here is the agriculture data", "sql": "SELECT * FROM agriculture_table"})
def test_chat_sql_mode(mock_ask_csv, mock_detect, admin_auth):
    """Test chat functionality in SQL mode"""
    res = client.post(
        "/chat",
        auth=admin_auth,
        json={"question": "List all farmers in the system"}
    )
    assert res.status_code == 200
    assert res.json()["mode"] == "SQL"
    assert res.json()["answer"] == "Here is the agriculture data"
    assert "sql" in res.json()

def test_upload_docs_no_auth():
    """Test uploading documents without authentication"""
    content = b"test content"
    file = io.BytesIO(content)
    
    res = client.post(
        "/upload-docs",
        files={"file": ("test.txt", file, "text/plain")},
        data={"role": "testrole"}
    )
    assert res.status_code == 401

def test_chat_no_auth():
    """Test chat functionality without authentication"""
    res = client.post(
        "/chat",
        json={"question": "What is agriculture?"}
    )
    assert res.status_code == 401

def test_login_success():
    """Test successful login"""
    res = client.get("/login", auth=("admin", "admin"))
    assert res.status_code == 200
    data = res.json()
    assert "message" in data
    assert "role" in data
    assert "username" in data

def test_login_invalid_credentials():
    """Test login with invalid credentials"""
    res = client.get("/login", auth=("invalid", "invalid"))
    assert res.status_code == 401

def test_get_roles(admin_auth):
    """Test getting available roles"""
    res = client.get("/roles", auth=admin_auth)
    assert res.status_code == 200
    data = res.json()
    assert "roles" in data
    assert "Admin" in data["roles"]
    assert "Farmer" in data["roles"]

def test_get_available_docs(admin_auth):
    """Test getting available documents for admin user"""
    res = client.get("/available-docs", auth=admin_auth)
    assert res.status_code == 200
    data = res.json()
    assert "documents" in data
    assert "user_role" in data
    assert "allowed_roles" in data

def test_health_check():
    """Test health check endpoint"""
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert "status" in data
    assert "version" in data
    assert "timestamp" in data

# Test role-based access control
@patch("app.main.detect_query_type_llm", return_value="RAG")
@patch("app.main.ask_rag", return_value={"answer": "HR information here"})
def test_hr_user_access_hr_docs(mock_ask_rag, mock_detect, hr_auth):
    """Test HR user accessing HR documents"""
    res = client.post(
        "/chat",
        auth=hr_auth,
        json={"question": "What are the HR policies?"}
    )
    assert res.status_code == 200
    assert "answer" in res.json()

@patch("app.main.detect_query_type_llm", return_value="RAG")
@patch("app.main.ask_rag", return_value={"answer": "Finance information here"})
def test_finance_user_access_finance_docs(mock_ask_rag, mock_detect, finance_officer_auth):
    """Test Finance Officer accessing finance documents"""
    res = client.post(
        "/chat",
        auth=finance_officer_auth,
        json={"question": "What are the financial policies?"}
    )
    assert res.status_code == 200
    assert "answer" in res.json()

@patch("app.main.detect_query_type_llm", return_value="RAG")
@patch("app.main.ask_rag", return_value={"answer": "Agriculture information here"})
def test_farmer_user_access_agriculture_docs(mock_ask_rag, mock_detect, farmer_auth):
    """Test Farmer accessing agriculture documents"""
    res = client.post(
        "/chat",
        auth=farmer_auth,
        json={"question": "What are the best farming practices?"}
    )
    assert res.status_code == 200
    assert "answer" in res.json()

def test_upload_docs_invalid_file_type(admin_auth):
    """Test uploading document with invalid file type"""
    content = b"test content"
    file = io.BytesIO(content)
    
    res = client.post(
        "/upload-docs",
        auth=admin_auth,
        files={"file": ("test.exe", file, "application/x-executable")},
        data={"role": "Admin"}
    )
    assert res.status_code == 400
    assert "Unsupported file type" in res.json()["detail"]

def test_upload_docs_file_too_large(admin_auth):
    """Test uploading document that exceeds size limit"""
    # Create a large file content (over 50MB)
    large_content = b"x" * (51 * 1024 * 1024)  # 51MB
    file = io.BytesIO(large_content)
    
    res = client.post(
        "/upload-docs",
        auth=admin_auth,
        files={"file": ("large_file.txt", file, "text/plain")},
        data={"role": "Admin"}
    )
    assert res.status_code == 400
    assert "File too large" in res.json()["detail"]
