"""
This code contain reusable UI components, styling, and layout functions
"""

import streamlit as st
from typing import List, Dict, Any, Optional
import time
import html
import re
from pathlib import Path

# -------------------------
# CUSTOM CSS STYLING
# -------------------------
def load_custom_css():
    """Load external CSS files for the application UI."""
    def _inject_css_file(css_path: Path) -> None:
        try:
            css_text = css_path.read_text(encoding="utf-8")
            st.markdown(f"<style>{css_text}</style>", unsafe_allow_html=True)
        except Exception:
            pass

    project_root = Path(__file__).resolve().parents[2]
    styles_dir = project_root / "app" / "frontend" / "styles"
    for name in ["base.css", "toolbar.css", "toast.css", "ai_response.css", "loader.css"]:
        _inject_css_file(styles_dir / name)

# -------------------------
# UI COMPONENTS
# -------------------------
def render_hero_section():
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
        login_button = st.button("Sign In", use_container_width=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    return username, password, login_button


def logout():
    st.session_state.auth = None
    st.session_state.role = None
    st.session_state.page = "login"
    st.rerun()
    

def render_fixed_top_toolbar(username: str, role: str):
    # Styles for toolbar are loaded globally via load_custom_css()
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
        submit_button = st.button("🚀 Get Response", use_container_width=True)
    
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
    """Show a temporary toast at the top-right of the screen."""
    # Styles for toasts are loaded globally via load_custom_css()
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
        <div class="ai-loader">
            <div class="ai-dot"></div>
            <div class="ai-dot"></div>
            <div class="ai-dot"></div>
            <div class="ai-loader-text">{message}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    return placeholder

def render_ai_response(answer: str, sql: Optional[str] = None):
    """Render the AI response in a dark card with a typing animation."""
    # Styles for the response card are loaded globally via load_custom_css()
    st.markdown('<div class="ai-response-anchor"></div>', unsafe_allow_html=True)
    placeholder = st.empty()
    compact = re.sub(r"\n\s*\n+", "\n", answer.strip())
    full_markdown = f"#### 🤖 AI Response\n\n{compact}"
    typed = ""
    for idx, ch in enumerate(full_markdown):
        typed += ch
        if idx % 2 == 0:
            placeholder.markdown(typed)
            time.sleep(0.01)
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
