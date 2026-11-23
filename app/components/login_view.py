"""
Login and Registration View Component.
Handles user authentication, role assignment, demo logins, and account registration.
Modern, sleek card styling.
"""

import streamlit as st
from typing import Dict, Any, Optional
from backend.database.sqlite_db import SQLiteManager


def render_login_view(sqlite_db: SQLiteManager):
    """Renders the login and registration page."""
    
    # Outer layout container for clean centered look
    col_left, col_center, col_right = st.columns([1, 2, 1])

    with col_center:
        st.html("""
        <div style="text-align: center; margin-bottom: 24px; padding-top: 20px;">
            <div style="background: linear-gradient(135deg, #4338ca, #6366f1); width: 68px; height: 68px; border-radius: 18px; display: inline-flex; align-items: center; justify-content: center; font-size: 34px; box-shadow: 0 8px 24px rgba(79, 70, 229, 0.3);">
                🛍️
            </div>
            <h2 style="font-size: 26px; font-weight: 800; color: #0f172a; margin: 14px 0 4px 0; letter-spacing: -0.5px;">OmniSupport AI Portal</h2>
            <p style="font-size: 13.5px; color: #64748b; margin: 0;">Multilingual Customer Support & Grounded RAG Knowledge Base</p>
        </div>
        """)

        tab_signin, tab_signup = st.tabs(["🔐 Sign In", "📝 Create Account"])

        with tab_signin:
            st.html("<div style='height: 10px;'></div>")
            with st.form("signin_form"):
                username = st.text_input("Username", placeholder="e.g. admin or customer", key="login_username")
                password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_password")
                submit_login = st.form_submit_button("Sign In to Portal", type="primary", use_container_width=True)

                if submit_login:
                    if not username or not password:
                        st.error("Please enter both username and password.")
                    else:
                        success, message, user_info = sqlite_db.authenticate_user(username, password)
                        if success:
                            st.session_state["authenticated_user"] = user_info
                            st.success(f"Welcome back, {user_info['full_name']}!")
                            st.rerun()
                        else:
                            st.error(message)

            st.html("<div style='margin-top: 20px;'></div>")
            st.html("<p style='font-size: 11.5px; font-weight: 700; color: #64748b; text-align: center; text-transform: uppercase; letter-spacing: 0.5px;'>⚡ Quick Demo Logins (One-Click):</p>")
            
            c_adm, c_cust = st.columns(2)
            with c_adm:
                if st.button("🔑 Login as Admin", use_container_width=True, help="Username: admin | Full Access to Knowledge Base & Benchmarks"):
                    _, _, u = sqlite_db.authenticate_user("admin", "admin123")
                    st.session_state["authenticated_user"] = u
                    st.rerun()
            with c_cust:
                if st.button("👤 Login as Customer", use_container_width=True, help="Username: customer | Access to Multilingual Chatbot"):
                    _, _, u = sqlite_db.authenticate_user("customer", "customer123")
                    st.session_state["authenticated_user"] = u
                    st.rerun()

            st.html("""
            <div style="background: #f8fafc; border: 1px dashed #cbd5e1; border-radius: 12px; padding: 12px 14px; margin-top: 16px; font-size: 12px; color: #475569; line-height: 1.6;">
                <b>Default Demo Credentials:</b><br>
                • <b>Admin:</b> <code>admin</code> / <code>admin123</code> (Admin Panel & Document Ingestion)<br>
                • <b>Customer:</b> <code>customer</code> / <code>customer123</code> (Support Chat access)
            </div>
            """)

        with tab_signup:
            st.html("<div style='height: 10px;'></div>")
            with st.form("signup_form"):
                new_fullname = st.text_input("Full Name", placeholder="e.g. Rahul Sharma")
                new_username = st.text_input("Username", placeholder="Choose a unique username")
                new_password = st.text_input("Password", type="password", placeholder="At least 4 characters")
                new_role = st.selectbox(
                    "Account Role",
                    options=["customer", "admin"],
                    format_func=lambda x: "Customer (Support Chatbot User)" if x == "customer" else "Administrator (Document Ingestion & Benchmarks)"
                )
                submit_register = st.form_submit_button("Register New Account", type="primary", use_container_width=True)

                if submit_register:
                    if not new_username or not new_password:
                        st.error("Username and password are required.")
                    else:
                        success, message, user_info = sqlite_db.register_user(
                            username=new_username,
                            password=new_password,
                            role=new_role,
                            full_name=new_fullname
                        )
                        if success:
                            st.session_state["authenticated_user"] = user_info
                            st.success("Account created successfully! Logging you in...")
                            st.rerun()
                        else:
                            st.error(message)
