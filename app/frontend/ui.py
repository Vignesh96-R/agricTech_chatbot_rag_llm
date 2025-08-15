import streamlit as st
import requests
from requests.auth import HTTPBasicAuth
from typing import List, Optional

from app.config import API_URL
from app.frontend.ui_components import (
    load_custom_css, render_hero_section, render_login_form,
    render_user_header, render_chat_interface, render_upload_interface,
    render_ai_response, render_loading_indicator, show_toast
)

# Page configuration
st.set_page_config(
    page_title="AgriTech Platform", 
    page_icon="🌾", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load custom CSS
load_custom_css()

# Hide Streamlit default menu, footer, and deploy button
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} /* Hides the menu */
    footer {visibility: hidden;}   /* Hides the footer */
    header {visibility: hidden;}   /* Hides "Deploy" button */
    </style>
""", unsafe_allow_html=True)

# -------------------------
# SESSION INIT
# -------------------------
if "auth" not in st.session_state:
    st.session_state.auth = None
if "role" not in st.session_state:
    st.session_state.role = None
if "page" not in st.session_state:
    st.session_state.page = "login"
if "username" not in st.session_state:
    st.session_state.username = None
if "password" not in st.session_state:
    st.session_state.password = None
if "roles" not in st.session_state:
    st.session_state.roles = []

# Load roles into session state if not present
def fetch_roles():
    try:
        role_res = requests.get(
            f"{API_URL}/roles",
            auth=HTTPBasicAuth(*st.session_state.auth),
            timeout=30,
        )
        return role_res.json().get("roles", [])
    except:
        return []

# -------------------------
# LOGIN PAGE
# -------------------------
if st.session_state.page == "login":
    # Hero Section
    render_hero_section()
    
    # Login Form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        username, password, login_button = render_login_form()
        
        if login_button:
            if not username or not password:
                show_toast("Please enter both username and password.", variant="error", duration=3)
            else:
                try:
                    res = requests.get(
                        f"{API_URL}/login",
                        auth=HTTPBasicAuth(username, password),
                        timeout=30,
                    )
                    if res.status_code == 200:
                        st.session_state.auth = (username, password)
                        st.session_state.username = username
                        st.session_state.password = password
                        st.session_state.role = res.json()["role"]
                        
                        # Fetch roles once login is successful
                        st.session_state.roles = fetch_roles()
                        st.session_state.page = "main"
                        st.rerun()
                    else:
                        try:
                            error_msg = res.json().get("detail", "Login failed. Please check your credentials.")
                            show_toast(error_msg, variant="error", duration=3)
                        except:
                            show_toast("Server error. Please check FastAPI logs.", variant="error", duration=3)
                except requests.exceptions.RequestException:
                    show_toast("Connection error. Please check if the server is running.", variant="error", duration=3)


# -------------------------
# MAIN APP AFTER LOGIN
# -------------------------
if st.session_state.page == "main":
    username = st.session_state.username
    role = st.session_state.role
    
    # Header with user info and fixed toolbar
    render_user_header(username, role)
   
    
    # Main content area
    if role == "Admin":
        st.markdown("""
        <div class="feature-card">
            <h3 style="color: #00d4aa; margin-bottom: -10px;">🌟 Global Access</h3>
            <p style="color: rgba(226, 232, 240, 0.8); margin: 0;">You have comprehensive access to all agriculture features, data analytics, and administrative functions.</p>
        </div>
        """, unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["💬 AI Chat Assistant", "📤 Document Management"])
        
        # Chat Tab
        with tab1:
            question, submit_button = render_chat_interface()
            
            if submit_button and question:
                try:
                    loader = render_loading_indicator()
                    res = requests.post(
                        f"{API_URL}/chat",
                        json={"question": question, "role": st.session_state.role},
                        auth=HTTPBasicAuth(*st.session_state.auth),
                        timeout=60,
                    )
                    
                    if res.status_code == 200:
                        response_data = res.json()
                        loader.empty()
                        render_ai_response(response_data["answer"], response_data.get("sql"))
                    else:
                        loader.empty()
                        show_toast("Something went wrong while processing your agriculture question.", variant="error", duration=3)
                except requests.exceptions.RequestException:
                    try:
                        loader.empty()
                    except Exception:
                        pass
                    show_toast("Connection error. Please check if the server is running.", variant="error", duration=3)
            elif submit_button and not question:
                show_toast("Please enter a question first.", variant="error", duration=3)
        
        # Upload Tab
        with tab2:
            selected_role, doc_file, upload_button = render_upload_interface(st.session_state.roles)
            
            if upload_button and doc_file:
                for file in doc_file:
                    try:
                        res = requests.post(
                            f"{API_URL}/upload-docs",
                            files={"file": file},
                            data={"role": selected_role},
                            auth=HTTPBasicAuth(*st.session_state.auth),
                            timeout=120,
                        )
                        
                        if res.ok:
                            show_toast(f"Successfully uploaded {file.name} for {selected_role} role", variant="success", duration=3)
                        else:
                            show_toast(f"Failed to upload {file.name}. Please try again.", variant="error", duration=3)
                    except requests.exceptions.RequestException:
                        show_toast(f"Connection error while uploading {file.name}", variant="error", duration=3)
            elif upload_button and not doc_file:
                show_toast("Please select at least one file to upload.", variant="warning", duration=3)
        
    else:
        # For non-Admin users
        st.markdown(f"""
        <div class="feature-card">
            <h3 style="color: #00d4aa; margin-bottom: 15px;">🎯 Role-Based Access</h3>
            <p style="color: rgba(226, 232, 240, 0.8); margin: 0;">You have access to agriculture documents and features related to the <strong>{role}</strong> role. Ask questions about farming techniques, crop management, market analysis, and other agriculture-related topics.</p>
        </div>
        """, unsafe_allow_html=True)
        
        tab1, = st.tabs(["💬 AI Chat Assistant"])
        
        with tab1:
            question, submit_button = render_chat_interface()
            
            if submit_button and question:
                try:
                    loader = render_loading_indicator()
                    res = requests.post(
                        f"{API_URL}/chat",
                        json={"question": question, "role": st.session_state.role},
                        auth=HTTPBasicAuth(*st.session_state.auth),
                        timeout=60,
                    )
                    
                    if res.status_code == 200:
                        response_data = res.json()
                        loader.empty()
                        render_ai_response(response_data["answer"], response_data.get("sql"))
                    else:
                        loader.empty()
                        show_toast("Something went wrong while processing your agriculture question.", variant="error", duration=3)
                except requests.exceptions.RequestException:
                    try:
                        loader.empty()
                    except Exception:
                        pass
                    show_toast("Connection error. Please check if the server is running.", variant="error", duration=3)
            elif submit_button and not question:
                show_toast("Please enter your question.", variant="error", duration=3)

