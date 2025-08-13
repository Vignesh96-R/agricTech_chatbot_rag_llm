import pytest
import re
from pathlib import Path

@pytest.mark.integration
def test_admin_full_flow(page):
    """Test complete admin user flow including document upload and chat functionality"""
    page.goto("http://localhost:8501", timeout=60000)

    #---------------------------------------
    # ---------- Login as Admin ----------
    #---------------------------------------
    page.get_by_role("textbox", name="Username").fill("admin")
    page.get_by_role("textbox", name="Password").fill("admin")
    page.get_by_role("button", name="Login").click()
    page.wait_for_selector("text=You have comprehensive access to all agriculture features", timeout=10000)

    # ---------- Switch to Document Management Tab ----------
    page.get_by_role("tab", name="📤 Document Management").click()
    page.wait_for_selector("text=🎯 Select document access role", timeout=15000)
    
    #---------------------------------------
    # ---------- Upload Document ----------
    #---------------------------------------
    page.get_by_text("🎯 Select document access role")
    
    # Choose role for document access
    dropdown = page.get_by_role("combobox")
    dropdown.wait_for(timeout=15000)
    dropdown.click()

    # Select "Admin" from dropdown using virtual dropdown container
    dropdown_popup = page.get_by_test_id("stSelectboxVirtualDropdown")
    dropdown_popup.get_by_text("Admin", exact=True).click()
    dropdown.wait_for(timeout=15000)

    page.get_by_text("Choose files")

    # Simulate file upload
    # Wait for upload area
    page.get_by_test_id("stFileUploaderDropzone").wait_for(timeout=5000)

    # Upload markdown file
    page.locator('input[type="file"]').set_input_files("tests/sample_docs/sample_hr.md")

    dropdown.wait_for(timeout=15000)
    
    page.get_by_role("button", name="📤 Upload Documents").click()
    page.wait_for_timeout(15000)
    page.wait_for_selector("text=sample_hr.md uploaded successfully for role 'Admin'", timeout=15000)

    # ---------- Switch to Chat Tab ----------
    page.get_by_role("tab", name="💬 AI Chat Assistant").click()
    
    # Ask a question
    page.get_by_text("💭 What would you like to know?")
    page.get_by_role("textbox", name="💭 What would you like to know?").fill("Tell me about agriculture best practices")
    page.get_by_role("button", name="🚀 Get AI Response").click()

    # Wait for response
    page.wait_for_selector("text=Answer:", timeout=10000)

    # ---------- Logout ----------
    page.get_by_role("button", name="Logout").click()
    page.wait_for_selector("text=Login", timeout=15000)

@pytest.mark.integration
def test_farmer_user_flow(page):
    """Test farmer user login and chat functionality"""
    page.goto("http://localhost:8501", timeout=60000)

    #---------------------------------------
    # Login with farmer user
    #---------------------------------------
    page.get_by_role("textbox", name="Username").fill("farmer")
    page.get_by_role("textbox", name="Password").fill("farmer")
    page.get_by_role("button", name="Login").click()

    # Validate role-specific access (Farmer, no Admin privileges)
    page.wait_for_selector("text=You have access to agriculture documents and features related", timeout=15000)
    page.wait_for_selector("text=You can ask questions about farming techniques, crop management, market analysis, and other agriculture-related topics.")
    
    # Assert Admin only tabs are not visible to regular user
    assert page.locator('text=📤 Document Management').count() == 0

    # Ask a question
    page.get_by_text("💭 What would you like to know?")
    page.get_by_role("textbox", name="💭 What would you like to know?").fill("What are the best farming practices for rice cultivation?")
    page.get_by_role("button", name="🚀 Get AI Response").click()

    # Wait for response
    page.wait_for_selector("text=Answer:", timeout=10000)

    # Logout
    page.get_by_role("button", name="Logout").click()
    page.wait_for_selector("text=Login", timeout=15000)

@pytest.mark.integration
def test_finance_officer_user_flow(page):
    """Test finance officer user login and chat functionality"""
    page.goto("http://localhost:8501", timeout=60000)

    #---------------------------------------
    # Login with finance officer user
    #---------------------------------------
    page.get_by_role("textbox", name="Username").fill("finance_officer")
    page.get_by_role("textbox", name="Password").fill("finance_officer")
    page.get_by_role("button", name="Login").click()

    # Validate role-specific access
    page.wait_for_selector("text=You have access to agriculture documents and features related", timeout=15000)
    page.wait_for_selector("text=You can ask questions about farming techniques, crop management, market analysis, and other agriculture-related topics.")
    
    # Assert Admin only tabs are not visible to regular user
    assert page.locator('text=📤 Document Management').count() == 0

    # Ask a question
    page.get_by_text("💭 What would you like to know?")
    page.get_by_role("textbox", name="💭 What would you like to know?").fill("What are the financial considerations for crop insurance?")
    page.get_by_role("button", name="🚀 Get AI Response").click()

    # Wait for response
    page.wait_for_selector("text=Answer:", timeout=10000)

    # Logout
    page.get_by_role("button", name="Logout").click()
    page.wait_for_selector("text=Login", timeout=15000)

@pytest.mark.integration
def test_hr_user_flow(page):
    """Test HR user login and chat functionality"""
    page.goto("http://localhost:8501", timeout=60000)

    #---------------------------------------
    # Login with HR user
    #---------------------------------------
    page.get_by_role("textbox", name="Username").fill("hr_manager")
    page.get_by_role("textbox", name="Password").fill("hr_manager")
    page.get_by_role("button", name="Login").click()

    # Validate role-specific access
    page.wait_for_selector("text=You have access to agriculture documents and features related", timeout=15000)
    page.wait_for_selector("text=You can ask questions about farming techniques, crop management, market analysis, and other agriculture-related topics.")
    
    # Assert Admin only tabs are not visible to regular user
    assert page.locator('text=📤 Document Management').count() == 0

    # Ask a question
    page.get_by_text("💭 What would you like to know?")
    page.get_by_role("textbox", name="💭 What would you like to know?").fill("What are the HR policies for agricultural workers?")
    page.get_by_role("button", name="🚀 Get AI Response").click()

    # Wait for response
    page.wait_for_selector("text=Answer:", timeout=10000)

    # Logout
    page.get_by_role("button", name="Logout").click()
    page.wait_for_selector("text=Login", timeout=15000)

@pytest.mark.integration
def test_invalid_login(page):
    """Test login with incorrect credentials"""
    page.goto("http://localhost:8501", timeout=60000)
    
    #---------------------------------------
    # Attempt login with incorrect credentials
    #---------------------------------------
    page.get_by_role("textbox", name="Username").fill("invalid_user")
    page.get_by_role("textbox", name="Password").fill("wrong_password")
    page.get_by_role("button", name="Login").click()

    # Expect an error message or no redirect
    page.wait_for_selector("text=Invalid credentials", timeout=5000)

@pytest.mark.integration
def test_agriculture_expert_user_flow(page):
    """Test agriculture expert user login and chat functionality"""
    page.goto("http://localhost:8501", timeout=60000)

    #---------------------------------------
    # Login with agriculture expert user
    #---------------------------------------
    page.get_by_role("textbox", name="Username").fill("agriculture_expert")
    page.get_by_role("textbox", name="Password").fill("agriculture_expert")
    page.get_by_role("button", name="Login").click()

    # Validate role-specific access
    page.wait_for_selector("text=You have access to agriculture documents and features related", timeout=15000)
    page.wait_for_selector("text=You can ask questions about farming techniques, crop management, market analysis, and other agriculture-related topics.")
    
    # Assert Admin only tabs are not visible to regular user
    assert page.locator('text=📤 Document Management').count() == 0

    # Ask a question
    page.get_by_text("💭 What would you like to know?")
    page.get_by_role("textbox", name="💭 What would you like to know?").fill("What are the latest sustainable farming techniques?")
    page.get_by_role("button", name="🚀 Get AI Response").click()

    # Wait for response
    page.wait_for_selector("text=Answer:", timeout=10000)

    # Logout
    page.get_by_role("button", name="Logout").click()
    page.wait_for_selector("text=Login", timeout=15000)
    
