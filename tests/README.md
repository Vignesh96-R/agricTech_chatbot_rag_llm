# RBAC Project Tests

This directory contains comprehensive tests for the RBAC (Role-Based Access Control) Project, an agriculture-focused application with role-based document access and AI-powered chat functionality.

## Test Structure

### `test_chatbot.py` - Unit Tests
Tests the FastAPI backend endpoints and business logic:
- **Authentication tests**: Login, role validation, access control
- **Document upload tests**: CSV and Markdown file handling
- **Chat functionality tests**: RAG and SQL query modes
- **Role-based access control tests**: Ensuring users can only access documents relevant to their role
- **Error handling tests**: Invalid file types, oversized files, unauthorized access

### `test_ui.py` - Integration Tests
Tests the Streamlit user interface using Playwright:
- **Admin user flow**: Document upload, chat functionality
- **Role-specific user flows**: Farmer, Finance Officer, HR, Agriculture Expert
- **Authentication flows**: Login, logout, invalid credentials
- **UI element validation**: Tab visibility, button functionality, form interactions

## Prerequisites

Before running the tests, ensure you have:

1. **Python dependencies installed**:
   ```bash
   pip install pytest pytest-playwright fastapi httpx pytest-html pytest-cov
   ```

2. **Playwright browsers installed**:
   ```bash
   playwright install
   ```

3. **Application running**: The FastAPI backend should be running on `localhost:8000` and Streamlit UI on `localhost:8501`

## Running Tests

### Option 1: Using the test runner script
```bash
# Run all tests
python run_tests.py

# Run only unit tests
python run_tests.py --type unit

# Run only integration tests
python run_tests.py --type integration

# Run fast tests (exclude slow ones)
python run_tests.py --type fast

# Verbose output
python run_tests.py --verbose

# Generate HTML report
python run_tests.py --html

# Generate coverage report
python run_tests.py --coverage

# Install dependencies
python run_tests.py --install-deps
```

### Option 2: Using the HTML report generator
```bash
# Generate comprehensive HTML report for all tests
python generate_report.py

# Generate unit test report only
python generate_report.py --type unit

# Generate integration test report only
python generate_report.py --type integration

# Generate summary report with all test types
python generate_report.py --type summary

# Generate report without coverage
python generate_report.py --no-coverage

# Generate report without custom styling
python generate_report.py --no-style
```

### Option 3: Using pytest directly
```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_chatbot.py

# Run tests with specific markers
pytest -m unit
pytest -m integration

# Run tests with coverage
pytest --cov=app tests/

# Generate HTML report
pytest --html=report.html tests/

# Generate HTML report with custom styling
pytest --html=report.html --self-contained-html tests/

# Generate HTML report with metadata
pytest --html=report.html --metadata Project "RBAC Project" --metadata Version "1.0.0" tests/
```

### Option 4: Using pytest with specific options
```bash
# Run tests in parallel (if pytest-xdist is installed)
pytest -n auto tests/

# Run tests and generate HTML report
pytest --html=report.html tests/

# Run tests and stop on first failure
pytest -x tests/

# Run tests with detailed output
pytest -v -s tests/
```

## HTML Report Generation

### Basic HTML Report
```bash
pytest --html=report.html tests/
```

### Enhanced HTML Report
```bash
pytest --html=report.html --self-contained-html tests/
```

### HTML Report with Metadata
```bash
pytest --html=report.html \
       --metadata Project "RBAC Agriculture Project" \
       --metadata Version "1.0.0" \
       --metadata Environment "Development" \
       tests/
```

### HTML Report with Coverage
```bash
pytest --html=report.html --cov=app --cov-report=html tests/
```

## Report Types Available

### 1. **Basic HTML Report** (`pytest --html`)
- Test results summary
- Pass/fail statistics
- Test execution details
- Basic styling

### 2. **Enhanced HTML Report** (`pytest --html --self-contained-html`)
- Self-contained (no external dependencies)
- Better styling and layout
- More detailed test information

### 3. **Custom HTML Report** (using `generate_report.py`)
- Project-specific branding
- Custom CSS styling
- Additional project information
- Navigation between sections
- Coverage integration

### 4. **Summary Report** (using `generate_report.py --type summary`)
- Overview of all test categories
- Links to detailed reports
- Status summary for each test type
- Coverage information

## Report Features

### 📊 **Test Results**
- Pass/fail statistics
- Execution time
- Error details and stack traces
- Test output and logs

### 🎨 **Custom Styling**
- Agriculture-themed color scheme
- Responsive design
- Professional layout
- Easy navigation

### 📈 **Coverage Information**
- Code coverage percentage
- Line-by-line coverage details
- Missing coverage highlights
- Branch coverage analysis

### 🔍 **Detailed Information**
- Test metadata
- Environment details
- Project information
- Generation timestamp

## Report Customization

### Custom CSS Styling
The HTML reports can be customized with your own CSS by modifying the `enhance_html_report` function in `generate_report.py`.

### Adding Metadata
```bash
pytest --html=report.html \
       --metadata Author "Your Name" \
       --metadata Team "Agriculture Team" \
       --metadata Branch "main" \
       tests/
```

### Custom Report Names
```bash
# Generate timestamped reports
python generate_report.py --type all

# This creates: full_test_report_20241201_143022.html
```

## Report Locations

After running tests with HTML reporting, you'll find:

- **HTML Test Reports**: `test_report_*.html` files in project root
- **Coverage Reports**: `htmlcov/` directory with detailed coverage
- **Summary Reports**: `test_summary_*.html` for comprehensive overview

## Continuous Integration

### GitHub Actions Example
```yaml
- name: Run Tests with HTML Report
  run: |
    pip install pytest pytest-html pytest-cov
    pytest --html=test_report.html --cov=app --cov-report=html tests/
    
- name: Upload Test Report
  uses: actions/upload-artifact@v2
  with:
    name: test-report
    path: test_report.html
```

### GitLab CI Example
```yaml
test:
  script:
    - pip install pytest pytest-html pytest-cov
    - pytest --html=test_report.html --cov=app --cov-report=html tests/
  artifacts:
    reports:
      junit: test_report.html
    paths:
      - test_report.html
      - htmlcov/
```

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure the project root is in your Python path
2. **Connection refused**: Make sure both FastAPI and Streamlit are running
3. **Playwright errors**: Reinstall browsers with `playwright install`
4. **Timeout errors**: Increase timeout values in test files if needed
5. **HTML report not generated**: Check if pytest-html is installed

### Debug Mode

Run tests with increased verbosity for debugging:
```bash
pytest -v -s tests/
```

### Isolated Testing

Test specific components in isolation:
```bash
# Test only authentication
pytest tests/test_chatbot.py::test_login_success

# Test only document upload
pytest tests/test_chatbot.py::test_upload_csv_document
```

## Adding New Tests

When adding new tests:

1. **Follow naming convention**: `test_*.py` for test files, `test_*` for test functions
2. **Use appropriate markers**: Mark tests as unit or integration
3. **Add docstrings**: Describe what each test validates
4. **Use fixtures**: Leverage existing fixtures or create new ones in `conftest.py`
5. **Mock external dependencies**: Use `unittest.mock` for external services

## Continuous Integration

These tests are designed to work with CI/CD pipelines:
- Fast execution for unit tests
- Comprehensive coverage of critical functionality
- Clear failure messages for debugging
- Markers for selective execution in different environments
- HTML report generation for easy review

## Performance Considerations

- **Unit tests**: Should complete in <1 second each
- **Integration tests**: May take 5-30 seconds each due to UI interactions
- **Total test suite**: Should complete in under 5 minutes for all tests
- **HTML report generation**: Adds minimal overhead

For performance testing, use the `--type fast` option to exclude slow tests during development.

## Report Examples

### Sample Report Structure
```
📊 Test Report: full_test_report_20241201_143022.html
├── 🌾 Project Header
├── 📋 Project Information
├── 🧪 Test Summary
│   ├── Total Tests: 25
│   ├── Passed: 23
│   ├── Failed: 2
│   └── Duration: 45.2s
├── 📈 Coverage Report
│   ├── Overall Coverage: 87%
│   ├── app/main.py: 92%
│   ├── app/auth.py: 85%
│   └── app/models.py: 78%
└── 🔍 Detailed Test Results
    ├── Unit Tests (15 tests)
    ├── Integration Tests (10 tests)
    └── Error Details for Failed Tests
```

### Report Navigation
- **Test Summary**: Overview of all test results
- **Test Details**: Individual test execution details
- **Coverage Report**: Code coverage analysis
- **Error Details**: Stack traces and failure information
