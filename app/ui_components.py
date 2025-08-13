"""
UI components and styling for the RBAC-Project Streamlit interface.

This module contains reusable UI components, styling, and layout functions
for the Streamlit-based user interface.
"""

import streamlit as st
from typing import List, Dict, Any, Optional
import time
import html
import re

# -------------------------
# CUSTOM CSS STYLING
# -------------------------
def load_custom_css():
    """Load custom CSS styling for the application."""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');
    
    .main {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        min-height: 100vh;
    }
    
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        font-family: 'Poppins', sans-serif;
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #00d4aa 0%, #0099cc 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 30px;
        font-weight: 600;
        font-size: 16px;
        transition: all 0.3s ease;
        box-shadow: 0 8px 25px rgba(0, 212, 170, 0.3);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 35px rgba(0, 212, 170, 0.4);
        background: linear-gradient(90deg, #00b894 0%, #00a8cc 100%);
    }
    
    .stTextInput > div > div > input {
        border-radius: 12px;
        border: 2px solid #2d3748;
        padding: 15px 20px;
        font-size: 16px;
        transition: all 0.3s ease;
        background: rgba(45, 55, 72, 0.8);
        color: #e2e8f0;
        backdrop-filter: blur(10px);
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #00d4aa;
        box-shadow: 0 0 0 3px rgba(0, 212, 170, 0.1);
        background: rgba(45, 55, 72, 0.9);
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #a0aec0;
    }
    
    .stSelectbox > div > div > div {
        border-radius: 12px;
        border: 2px solid #2d3748;
        background: rgba(45, 55, 72, 0.8);
        backdrop-filter: blur(10px);
    }
    
    .stFileUploader > div > div > div {
        border-radius: 12px;
        border: 2px solid #2d3748;
        background: rgba(45, 55, 72, 0.8);
        backdrop-filter: blur(10px);
    }
    
    .stTabs > div > div > div > div {
        background: rgba(45, 55, 72, 0.3);
        border-radius: 12px;
        padding: 5px;
        backdrop-filter: blur(10px);
    }
    
    .stTabs > div > div > div > div > button {
        background: transparent;
        color: #e2e8f0;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        margin: 2px;
        font-weight: 500;
        transition: all 0.3s ease;
        font-size: 14px;
    }
    
    .stTabs > div > div > div > div > button[aria-selected="true"] {
        background: linear-gradient(90deg, #00d4aa 0%, #0099cc 100%);
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 15px rgba(0, 212, 170, 0.3);
        color: white;
    }
    
    .stTabs > div > div > div > div > button:hover {
        background: rgba(0, 212, 170, 0.1);
        transform: translateY(-1px);
        color: #00d4aa;
    }
    
    /* Fixed Top Toolbar Styles */
    .fixed-toolbar {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 1000;
        background: rgba(26, 26, 46, 0.95);
        backdrop-filter: blur(20px);
        border-bottom: 1px solid rgba(0, 212, 170, 0.3);
        padding: 15px 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    
    .toolbar-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
        max-width: 1200px;
        margin: 0 auto;
    }
    
    .toolbar-brand {
        display: flex;
        align-items: center;
        gap: 15px;
    }
    
    .toolbar-brand h1 {
        color: #00d4aa;
        margin: 0;
        font-size: 1.8rem;
        font-weight: 700;
    }
    
    .toolbar-controls {
        display: flex;
        align-items: center;
        gap: 20px;
    }
    
    .role-badge-toolbar {
        background: linear-gradient(90deg, #00d4aa 0%, #0099cc 100%);
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        box-shadow: 0 4px 15px rgba(0, 212, 170, 0.3);
    }
    
    .toolbar-spacer {
        height: 80px;
    }
    
    /* Fixed Top Toolbar Styles */
    .fixed-toolbar {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 1000;
        background: rgba(26, 26, 46, 0.95);
        backdrop-filter: blur(20px);
        border-bottom: 1px solid rgba(0, 212, 170, 0.3);
        padding: 15px 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    
    .toolbar-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
        max-width: 1200px;
        margin: 0 auto;
    }
    
    .toolbar-brand {
        display: flex;
        align-items: center;
        gap: 15px;
    }
    
    .toolbar-brand h1 {
        color: #00d4aa;
        margin: 0;
        font-size: 1.8rem;
        font-weight: 700;
    }
    
    .toolbar-controls {
        display: flex;
        align-items: center;
        gap: 20px;
    }
    
    .role-badge-toolbar {
        background: linear-gradient(90deg, #00d4aa 0%, #0099cc 100%);
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        box-shadow: 0 4px 15px rgba(0, 212, 170, 0.3);
    }
    
    .toolbar-spacer {
        height: 80px;
    }
    
    /* Ensure main content is properly positioned */
    .main .block-container {
        padding-top: 20px;
    }
    
    /* Style the logout button to match the toolbar theme */
    .stButton > button[key="logout_btn"] {
        background: linear-gradient(90deg, #ff6b6b 0%, #ee5a52 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 8px 16px;
        font-weight: 600;
        font-size: 14px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stButton > button[key="logout_btn"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255, 107, 107, 0.4);
        background: linear-gradient(90deg, #ff5252 0%, #d32f2f 100%);
    }
    
    /* Style for the toolbar logout button */
    .stButton > button[key="toolbar_logout_btn"] {
        background: linear-gradient(90deg, #ff6b6b 0%, #ee5a52 100%);
        color: white;
        border: none;
        border-radius: 20px;
        padding: 8px 16px;
        font-weight: 600;
        font-size: 0.9rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        cursor: pointer;
        font-family: 'Poppins', sans-serif;
        margin: 0;
        min-width: 100px;
    }
    
    .stButton > button[key="toolbar_logout_btn"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255, 107, 107, 0.4);
        background: linear-gradient(90deg, #ff5252 0%, #d32f2f 100%);
    }
    
    .glass-card {
        background: rgba(45, 55, 72, 0.4);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        border: 1px solid rgba(0, 212, 170, 0.2);
        padding: 30px;
        margin: 20px 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    .hero-section {
        text-align: center;
        padding-top: 20px;
        margin-bottom: 40px;
    }
    
    .hero-title {
        font-size: 4rem;
        font-weight: 800;
        background: linear-gradient(135deg, #00d4aa 0%, #0099cc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 20px;
        text-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        letter-spacing: -1px;
    }
    
    .hero-subtitle {
        font-size: 1.4rem;
        color: rgba(226, 232, 240, 0.9);
        font-weight: 400;
        margin-bottom: 30px;
        line-height: 1.6;
    }
    
    .user-info-card {
        background: rgba(45, 55, 72, 0.6);
        backdrop-filter: blur(15px);
        border-radius: 20px;
        padding: 25px;
        border: 1px solid rgba(0, 212, 170, 0.3);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
    }
    
    .chat-container {
        background: rgba(45, 55, 72, 0.8);
        border-radius: 20px;
        padding: 30px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(0, 212, 170, 0.2);
        backdrop-filter: blur(15px);
    }
    
    .success-message {
        background: linear-gradient(135deg, #00d4aa 0%, #00b894 100%);
        color: white;
        padding: 20px 25px;
        border-radius: 15px;
        margin: 15px 0;
        box-shadow: 0 4px 15px rgba(0, 212, 170, 0.3);
        border-left: 4px solid #00b894;
    }
    
    .error-message {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
        color: white;
        padding: 20px 25px;
        border-radius: 15px;
        margin: 15px 0;
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
        border-left: 4px solid #ee5a52;
    }
    
    .role-badge {
        display: inline-block;
        background: linear-gradient(135deg, #00d4aa 0%, #0099cc 100%);
        color: white;
        padding: 10px 20px;
        border-radius: 25px;
        font-size: 14px;
        font-weight: 600;
        margin: 5px;
        box-shadow: 0 4px 15px rgba(0, 212, 170, 0.3);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .feature-card {
        background: rgba(45, 55, 72, 0.4);
        backdrop-filter: blur(15px);
        border-radius: 20px;
        padding: 25px;
        margin: 15px 0;
        border: 1px solid rgba(0, 212, 170, 0.2);
        transition: all 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.3);
        border-color: rgba(0, 212, 170, 0.4);
    }
    
    .upload-area {
        border: 2px dashed rgba(0, 212, 170, 0.5);
        border-radius: 20px;
        padding: 40px;
        text-align: center;
        background: rgba(45, 55, 72, 0.2);
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }
    
    .upload-area:hover {
        border-color: rgba(0, 212, 170, 0.8);
        background: rgba(45, 55, 72, 0.3);
    }
    
    .admin-section {
        background: rgba(45, 55, 72, 0.4);
        backdrop-filter: blur(15px);
        border-radius: 20px;
        padding: 30px;
        margin: 20px 0;
        border: 1px solid rgba(0, 212, 170, 0.2);
    }
    
    .stMarkdown {
        color: #e2e8f0;
    }
    
    .stSubheader {
        color: #00d4aa;
        font-size: 1.8rem;
        font-weight: 600;
        margin-bottom: 20px;
    }
    
    .stMarkdown p {
        color: rgba(226, 232, 240, 0.9);
        font-size: 1.1rem;
        line-height: 1.6;
    }
    
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #00d4aa;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(45, 55, 72, 0.3);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #00d4aa 0%, #0099cc 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #00b894 0%, #00a8cc 100%);
    }
    
    /* Animation for cards */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .glass-card, .chat-container, .user-info-card {
        animation: fadeInUp 0.6s ease-out;
    }
    
    /* Fixed toolbar styles */
    .fixed-toolbar {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 9999;
        background: rgba(26, 26, 46, 0.95);
        backdrop-filter: blur(20px);
        border-bottom: 1px solid rgba(0, 212, 170, 0.3);
        padding: 15px 30px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    
    .toolbar-brand {
        display: flex;
        align-items: center;
    }
    
    .toolbar-brand h1 {
        color: #00d4aa;
        margin: 0;
        font-size: 1.8rem;
        font-weight: 700;
        text-shadow: 0 2px 4px rgba(0, 212, 170, 0.3);
    }
    
    .toolbar-controls {
        display: flex;
        align-items: center;
        gap: 20px;
    }
    
    .role-badge-toolbar {
        background: linear-gradient(135deg, #00d4aa 0%, #0099cc 100%);
        color: white;
        padding: 10px 20px;
        border-radius: 25px;
        font-size: 14px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        box-shadow: 0 6px 20px rgba(0, 212, 170, 0.4);
        border: 2px solid rgba(255, 255, 255, 0.3);
        transition: all 0.3s ease;
        display: inline-block;
        min-width: 80px;
        text-align: center;
    }
    
    .role-badge-toolbar:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 212, 170, 0.5);
        border-color: rgba(255, 255, 255, 0.5);
    }
    
    .logout-btn-toolbar {
        background: rgba(255, 107, 107, 0.2);
        color: #ff6b6b;
        border: 1px solid #ff6b6b;
        padding: 8px 16px;
        border-radius: 12px;
        cursor: pointer;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
        font-weight: 500;
        font-size: 13px;
    }
    
    .logout-btn-toolbar:hover {
        background: rgba(255, 107, 107, 0.3);
        transform: translateY(-1px);
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
    }
    
    /* Ensure content doesn't overlap with fixed toolbar */
    .main-content {
        margin-top: 80px;
    }
    
    /* Compact mode overrides: reduce overall sizes */
    .fixed-toolbar { padding: 8px 16px; }
    .toolbar-spacer { height: 56px; }
    .toolbar-brand h1 { font-size: 1.3rem; }
    .role-badge-toolbar { padding: 6px 12px; font-size: 0.8rem; border-radius: 16px; min-width: 60px; }
    
    .stButton > button { padding: 8px 18px; font-size: 14px; border-radius: 10px; }
    .stTextInput > div > div > input { padding: 10px 14px; font-size: 14px; }
    .stTabs > div > div > div > div > button { padding: 8px 14px; font-size: 13px; }
    
    .hero-subtitle { font-size: 1.1rem; }
    .stMarkdown p { font-size: 1.0rem; line-height: 1.5; }
    .stMarkdown h1 { font-size: 2rem; }
    .stMarkdown h2 { font-size: 1.3rem; }
    .stMarkdown h3 { font-size: 1.15rem; }
    </style>
    """, unsafe_allow_html=True)

# -------------------------
# UI COMPONENTS
# -------------------------
def render_hero_section():
    """Render the hero section with title and subtitle."""
    st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">🌾 AgriTech</h1>
        <p class="hero-subtitle">Your Intelligent Agriculture Knowledge Assistant & Data Insights Platform</p>
        <div style="margin-top: 30px;">
            <span style="background: rgba(0, 212, 170, 0.2); padding: 8px 16px; border-radius: 20px; color: #00d4aa; font-size: 14px; margin: 0 10px;">🤖 AI-Powered</span>
            <span style="background: rgba(0, 153, 204, 0.2); padding: 8px 16px; border-radius: 20px; color: #0099cc; font-size: 14px; margin: 0 10px;">📊 Data Analytics</span>
            <span style="background: rgba(0, 212, 170, 0.2); padding: 8px 16px; border-radius: 20px; color: #00d4aa; font-size: 14px; margin: 0 10px;">🔐 Secure Access</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_login_form():
    username = st.text_input("👤 Username", placeholder="Enter your username")
    password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
    
    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_b:
        login_button = st.button("🚀 Access Platform", use_container_width=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    return username, password, login_button


def logout():
    """Logout function to clear session state and redirect to login."""
    st.session_state.auth = None
    st.session_state.role = None
    st.session_state.page = "login"
    st.rerun()
    

def render_fixed_top_toolbar(username: str, role: str):
    """Render a fixed top toolbar with branding and user controls."""
    
    # CSS for sticky toolbar
    st.markdown("""
    <style>
    .fixed-toolbar {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        background-color: #1a1b3b;
        padding: 6px 12px; /* compact */
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.3);
        z-index: 1000;
    }
    .toolbar-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
        width: 100%;
    }
    .toolbar-brand {
        display: flex;
        align-items: center;
        gap: 10px;
        color: #00c896;
        font-weight: bold;
    }
    .toolbar-controls {
        display: flex;
        gap: 15px;
        align-items: center;
    }
    .role-badge-toolbar {
        background: rgba(255, 255, 255, 0.1);
        padding: 6px 12px;
        border-radius: 6px;
        font-size: 14px;
        color: white;
    }
    .logout-btn {
        background: #ff4d4d;
        padding: 6px 14px;
        border-radius: 6px;
        font-size: 14px;
        color: white;
        cursor: pointer;
        border: none;
    }
    .logout-btn:hover {
        background: #cc0000;
    }
    .toolbar-spacer { height: 48px; }
    </style>
    """, unsafe_allow_html=True)
    
    # HTML toolbar (form for logout)
    toolbar_html = f"""
    <div class="fixed-toolbar">
        <div class="toolbar-content">
            <div class="toolbar-brand">
                <span style="font-size: 24px;">🌾</span>
                <h1>AgriTech</h1>
            </div>
            <div class="toolbar-controls">
                <div class="role-badge-toolbar">{role}</div>
            </div>
        </div>
    </div>
    <div class="toolbar-spacer"></div>
    """
    
    st.markdown(toolbar_html, unsafe_allow_html=True)
    button_logout()

def button_logout():
    # Unique wrapper for this button
    with st.container():
        st.markdown('<div class="logout-btn-container">', unsafe_allow_html=True)
        if st.button("Logout"):
            st.session_state.clear()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

def render_user_header(username: str, role: str):
    """Render the user header with role badge and logout button."""
    # Render the fixed top toolbar
    render_fixed_top_toolbar(username, role)
    

def render_chat_interface():
    """Render the chat interface."""
    question = st.text_input("💭 What would you like to know?", placeholder="Ask about farming techniques, crop management, market analysis, or any agriculture questions...")
    
    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_b:
        submit_button = st.button("🚀 Get AI Response", use_container_width=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    return question, submit_button

def render_upload_interface(roles: List[str]):
    """Render the document upload interface."""
    selected_role = st.selectbox("🎯 Select document access role", roles)
    
    doc_file = st.file_uploader("Choose files", type=["csv", "md"], accept_multiple_files=True)
    
    upload_button = st.button("📤 Upload Documents", use_container_width=True)
    
    st.markdown("</div></div>", unsafe_allow_html=True)
    
    return selected_role, doc_file, upload_button



def show_toast(message: str, variant: str = "error", duration: float = 3.0):
    """Show a temporary toast at the top-right of the screen.

    Args:
        message: Text to display inside the toast
        variant: One of "success", "error", "warning", "info"
        duration: Seconds before the toast auto-hides
    """
    # Inject toast CSS (idempotent)
    st.markdown(
        """
        <style>
        .toast-container { position: fixed; top: 16px; right: 16px; z-index: 10000; }
        .toast {
            min-width: 280px;
            max-width: 420px;
            padding: 12px 16px;
            border-radius: 12px;
            color: #fff;
            margin-top: 10px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.3);
            border-left: 4px solid rgba(255,255,255,0.4);
            backdrop-filter: blur(12px);
            animation: toast-slide-in 300ms ease-out;
        }
        .toast-success { background: linear-gradient(135deg, #00d4aa 0%, #00b894 100%); }
        .toast-error { background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%); }
        .toast-warning { background: linear-gradient(135deg, #ffb74d 0%, #fb8c00 100%); }
        .toast-info { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
        @keyframes toast-slide-in {
            from { opacity: 0; transform: translateX(16px); }
            to { opacity: 1; transform: translateX(0); }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Render toast
    placeholder = st.empty()
    icon = {
        "success": "✅",
        "error": "❌",
        "warning": "⚠️",
        "info": "ℹ️",
    }.get(variant, "ℹ️")

    safe_message = html.escape(message)
    placeholder.markdown(
        f"""
        <div class="toast-container">
            <div class="toast toast-{variant}">{icon} {safe_message}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Auto-hide
    try:
        time.sleep(max(0.1, float(duration)))
    except Exception:
        time.sleep(3)
    placeholder.empty()

def render_loading_indicator(message: str = "Generating AI response..."):
    """Render a compact loader card and return its placeholder for later clearing."""
    placeholder = st.empty()
    placeholder.markdown(
        f"""
        <style>
        .ai-loader {{
            display: inline-flex;
            align-items: center;
            gap: 10px;
            background: rgba(13,17,23,0.85);
            border: 1px solid rgba(0, 212, 170, 0.25);
            border-radius: 12px;
            padding: 12px 14px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.35);
        }}
        .ai-dot {{
            width: 9px;
            height: 9px;
            border-radius: 50%;
            background: #00d4aa;
            animation: dot-bounce 1.1s infinite ease-in-out;
        }}
        .ai-dot:nth-child(2) {{ animation-delay: 0.15s; }}
        .ai-dot:nth-child(3) {{ animation-delay: 0.30s; }}
        @keyframes dot-bounce {{
            0%, 80%, 100% {{ transform: scale(0.7); opacity: 0.6; }}
            40% {{ transform: scale(1); opacity: 1; }}
        }}
        .ai-loader-text {{ color: #e2e8f0; font-size: 0.95rem; }}
        </style>
        <div class=\"ai-loader\">
            <div class=\"ai-dot\"></div>
            <div class=\"ai-dot\"></div>
            <div class=\"ai-dot\"></div>
            <div class=\"ai-loader-text\">{message}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    return placeholder

def render_ai_response(answer: str, sql: Optional[str] = None):
    """Render the AI response in a dark card with a typing animation."""
    # Inject component-specific CSS once (idempotent)
    st.markdown(
        """
        <style>
        /* Style the markdown block immediately following the anchor */
        .ai-response-anchor + div {
            background: rgba(13, 17, 23, 0.85) !important;
            border: 1px solid rgba(0, 212, 170, 0.25);
            border-radius: 16px;
            padding: 18px 20px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.35);
            margin: 12px 0 6px 0;
        }
        .ai-response-anchor + div h1,
        .ai-response-anchor + div h2,
        .ai-response-anchor + div h3,
        .ai-response-anchor + div h4 { color: #00d4aa !important; margin: 0 0 8px 0; }
        .ai-response-anchor + div p { color: #e2e8f0 !important; margin: 4px 0; line-height: 1.35; }
        .ai-response-anchor + div ul,
        .ai-response-anchor + div ol { margin: 4px 0 4px 18px; padding-left: 1rem; }
        .ai-response-anchor + div li { margin: 2px 0; }
        .typing-cursor { display: inline-block; width: 8px; height: 1.1em; margin-left: 2px; background: #e2e8f0; animation: blink 1s step-start infinite; vertical-align: -2px; }
        @keyframes blink { 50% { opacity: 0; } }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Add an anchor so the next Markdown block can be styled as the response card
    st.markdown('<div class="ai-response-anchor"></div>', unsafe_allow_html=True)
    placeholder = st.empty()

    # Typewriter effect: progressively render Markdown (not escaped)
    compact = re.sub(r"\n\s*\n+", "\n", answer.strip())
    full_markdown = f"#### 🤖 AI Response\n\n{compact}"
    typed = ""
    for idx, ch in enumerate(full_markdown):
        typed += ch
        if idx % 2 == 0:
            placeholder.markdown(typed)
            time.sleep(0.01)

    # Final render to ensure complete Markdown is shown
    placeholder.markdown(full_markdown)

    if sql:
        st.markdown(
            """
            <div style="background: rgba(17, 24, 39, 0.9); border-radius: 12px; padding: 16px; margin-top: 12px; border: 1px solid rgba(0, 212, 170, 0.2);">
                <h4 style="color: #00d4aa; margin: 0 0 10px 0;">🔍 Generated SQL Query</h4>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.code(sql, language="sql")
