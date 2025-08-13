import pytest
import os
from pathlib import Path
import sys

# Add the project root to Python path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure pytest for the RBAC project
def pytest_configure(config):
    """Configure pytest for the RBAC project"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )

def pytest_collection_modifyitems(config, items):
    """Automatically mark tests based on their names"""
    for item in items:
        if "test_ui" in item.name:
            item.add_marker(pytest.mark.integration)
        elif "test_chatbot" in item.name:
            item.add_marker(pytest.mark.unit)
        else:
            item.add_marker(pytest.mark.unit)

@pytest.fixture(scope="session")
def test_data_dir():
    """Provide test data directory path"""
    return Path(__file__).parent / "sample_docs"

@pytest.fixture(scope="session")
def sample_csv_content():
    """Provide sample CSV content for testing"""
    return """Name,Role,Department
John Doe,Farmer,Agriculture
Jane Smith,Field Worker,Operations
Bob Johnson,Finance Officer,Finance"""

@pytest.fixture(scope="session")
def sample_md_content():
    """Provide sample Markdown content for testing"""
    return """# Agriculture Guide
This is a sample agriculture document for testing purposes.

## Farming Techniques
- Crop rotation
- Soil management
- Pest control

## Best Practices
Follow sustainable farming methods."""
