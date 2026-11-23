"""
Sidebar Component for Navigation, Language Selection, User Profile, and System Health.
Linear & Stripe-inspired compact, premium SaaS dashboard sidebar.
"""

import streamlit as st
from typing import Dict, Any, Tuple, Optional
from ml.rag.ollama_client import OllamaClient
from ml.retrieval.vector_store import VectorStoreManager


def render_sidebar(
    ollama_client: OllamaClient,
    vector_store: VectorStoreManager,
    current_user: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    with st.sidebar:
        # 1. OmniSupport AI Logo and Branding
        st.html("""
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 20px; padding: 2px 0;">
            <div style="background: linear-gradient(135deg, #635BFF 0%, #8B5CF6 100%); color: #FFFFFF; width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 22px; font-weight: 800; box-shadow: 0 4px 14px rgba(99, 91, 255, 0.35);">
                🛍️
            </div>
            <div>
                <div style="display: flex; align-items: center; gap: 6px;">
                    <span style="font-size: 17px; font-weight: 800; color: #111827; letter-spacing: -0.4px;">OmniSupport</span>
                    <span style="font-size: 10px; font-weight: 800; background: rgba(99, 91, 255, 0.1); color: #635BFF; border: 1px solid rgba(99, 91, 255, 0.25); padding: 1px 6px; border-radius: 9999px;">AI</span>
                </div>
                <p style="margin: 0; font-size: 11.5px; color: #94A3B8; font-weight: 500;">Multilingual RAG Engine</p>
            </div>
        </div>
        """)

        # 2. Administrator / Customer Profile
        if current_user:
            role = current_user.get("role", "customer")
            is_admin = (role == "admin")
            role_label = "Administrator" if is_admin else "Customer"
            role_color = "#635BFF" if is_admin else "#059669"
            role_bg = "#EEF2FF" if is_admin else "#ECFDF5"
            role_border = "#C7D2FE" if is_admin else "#A7F3D0"
            full_name = current_user.get('full_name', 'User')
            initials = "".join([part[0].upper() for part in full_name.split()[:2]]) if full_name else "U"

            st.html(f"""
            <div class="sidebar-profile-card">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div class="sidebar-profile-avatar">{initials}</div>
                    <div style="flex: 1; min-width: 0;">
                        <div style="font-size: 13.5px; font-weight: 700; color: #111827; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{full_name}</div>
                        <div style="font-size: 11.5px; color: #94A3B8;">@{current_user.get('username')}</div>
                    </div>
                    <span style="font-size: 10px; font-weight: 700; background: {role_bg}; color: {role_color}; border: 1px solid {role_border}; padding: 2px 8px; border-radius: 9999px;">
                        {role_label}
                    </span>
                </div>
            </div>
            """)

            if st.button("🚪 Sign Out", use_container_width=True):
                st.session_state["authenticated_user"] = None
                st.rerun()

        st.markdown("---")

        # 3. Navigation View (Customer Chatbot vs Admin & Evaluation)
        st.html("""
        <div class="sidebar-section-title">
            <span>📌</span> Navigation Workspace
        </div>
        """)
        view_mode = st.radio(
            "Navigation",
            options=["💬 Customer Chatbot", "⚙️ Admin & Evaluation"],
            label_visibility="collapsed"
        )

        st.markdown("---")

        # 4. Language Selection Mode
        st.html("""
        <div class="sidebar-section-title">
            <span>🌐</span> Language Mode
        </div>
        """)
        lang_choice = st.selectbox(
            "Language Mode",
            options=["Auto-Detect (स्वयंचलित)", "English", "Hindi (हिंदी)", "Marathi (मराठी)"],
            index=0,
            help="Select Auto-Detect to automatically identify English, Hindi, or Marathi, or force a specific response language."
        )

        manual_lang_code = None
        if "English" in lang_choice:
            manual_lang_code = "en"
        elif "Hindi" in lang_choice:
            manual_lang_code = "hi"
        elif "Marathi" in lang_choice:
            manual_lang_code = "mr"

        st.markdown("---")

        # 5. Ollama Status & Open-Source LLM Engine
        st.html("""
        <div class="sidebar-section-title">
            <span>⚡</span> AI Engine & Health
        </div>
        """)
        
        conn_info = ollama_client.check_connection()
        is_online = conn_info.get("connected", False)
        display_model = conn_info.get("model_name", "Qwen2.5 LLM")

        if is_online:
            st.html(f"""
            <div class="status-pill online">
                <span class="pulse-indicator"></span> {display_model} Live
            </div>
            """)
            st.html("<div style='height: 8px;'></div>")
            use_llm = st.toggle(
                "Enable Open-Source LLM",
                value=True,
                help="Generates grounded answers using Qwen2.5. If disabled, uses Grounded Policy Synthesis."
            )
        else:
            st.html("""
            <div class="status-pill online">
                <span class="pulse-indicator"></span> Grounded RAG Engine Active
            </div>
            """)
            use_llm = False

        # 6. Vector Store Index (51 Chunks, 12 Policies)
        total_chunks = vector_store.get_total_chunks()
        doc_summary = vector_store.list_indexed_documents()
        total_policies = len(doc_summary)

        st.html(f"""
        <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 14px; margin-top: 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
            <div style="font-size: 10.5px; color: #94A3B8; font-weight: 700; text-transform: uppercase; letter-spacing: 0.6px; margin-bottom: 8px;">
                Vector Store Index (ChromaDB)
            </div>
            <div style="display: flex; gap: 8px;">
                <div style="flex: 1; background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 10px 8px; text-align: center;">
                    <div style="font-size: 20px; font-weight: 800; color: #635BFF;">{total_chunks}</div>
                    <div style="font-size: 10.5px; color: #64748b; font-weight: 600;">Chunks</div>
                </div>
                <div style="flex: 1; background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 10px 8px; text-align: center;">
                    <div style="font-size: 20px; font-weight: 800; color: #111827;">{total_policies}</div>
                    <div style="font-size: 10.5px; color: #64748b; font-weight: 600;">Policies</div>
                </div>
            </div>
            <div style="font-size: 10.5px; color: #94a3b8; text-align: center; margin-top: 8px;">
                Embedding: <code>multilingual-e5-small</code>
            </div>
        </div>
        """)

        st.markdown("---")

        # 7. Clear Conversation Action Button
        if st.button("🗑️ Clear Conversation", use_container_width=True):
            st.session_state["clear_chat_trigger"] = True
            st.rerun()

        # 8. Sidebar Footer
        st.html("""
        <div style="margin-top: 24px; text-align: center; font-size: 11px; color: #94A3B8; font-weight: 500;">
            OmniSupport AI v2.5 Enterprise<br>NLP & Retrieval-Augmented Generation
        </div>
        """)

        return {
            "view_mode": view_mode,
            "manual_language": manual_lang_code,
            "use_llm": use_llm,
            "ollama_online": is_online
        }
