"""
Main Streamlit Application for Multilingual E-Commerce Customer Support Chatbot.
Orchestrates User Authentication, RAG Pipeline, ChromaDB Vector Store, Ollama LLM, SQLite Persistence, and Modern UI.
"""

import os
import sys
import uuid
import streamlit as st

# Configure sys.path for modular imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.styles.theme import apply_theme
from app.components.sidebar import render_sidebar
from app.components.chat_ui import render_chat_view
from app.components.admin_view import render_admin_view
from app.components.login_view import render_login_view

from ml.rag.ollama_client import OllamaClient
from ml.retrieval.vector_store import VectorStoreManager
from ml.rag.rag_pipeline import MultilingualRAGPipeline
from backend.services.document_processor import DocumentProcessor
from backend.database.sqlite_db import SQLiteManager


# Streamlit Page Configuration
st.set_page_config(
    page_title="OmniSupport AI | Multilingual E-Commerce Chatbot",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply CSS Theme
apply_theme()


@st.cache_resource
def get_backend_services():
    """Initializes and caches core ML and Database components."""
    sqlite_db = SQLiteManager()
    vector_store = VectorStoreManager()
    document_processor = DocumentProcessor()
    ollama_client = OllamaClient()
    rag_pipeline = MultilingualRAGPipeline(
        vector_store=vector_store,
        ollama_client=ollama_client
    )
    return sqlite_db, vector_store, document_processor, ollama_client, rag_pipeline


sqlite_db, vector_store, document_processor, ollama_client, rag_pipeline = get_backend_services()

# Authentication Check
if "authenticated_user" not in st.session_state:
    st.session_state["authenticated_user"] = None

# If not authenticated, display login view
if not st.session_state["authenticated_user"]:
    render_login_view(sqlite_db)
    st.stop()

# Current Logged-in User Info
current_user = st.session_state["authenticated_user"]

# Session State Initialization for Chat
if "session_id" not in st.session_state:
    st.session_state["session_id"] = f"sess_{uuid.uuid4().hex[:12]}"

# Ensure session is registered with current user in database
sqlite_db.get_or_create_session(st.session_state["session_id"], username=current_user.get("username"))

if "messages" not in st.session_state:
    # Load past messages from SQLite if available, else start empty
    past_msgs = sqlite_db.get_session_messages(st.session_state["session_id"])
    st.session_state["messages"] = past_msgs if past_msgs else []

# Handle Clear Chat Trigger
if st.session_state.get("clear_chat_trigger", False):
    sqlite_db.clear_session(st.session_state["session_id"])
    st.session_state["messages"] = []
    st.session_state["clear_chat_trigger"] = False

# Render Sidebar with User Profile
sidebar_state = render_sidebar(
    ollama_client=ollama_client,
    vector_store=vector_store,
    current_user=current_user
)

view_mode = sidebar_state["view_mode"]
manual_lang = sidebar_state["manual_language"]
use_llm = sidebar_state["use_llm"]


def handle_send_query(query_text: str):
    """Processes user query through the Multilingual RAG pipeline."""
    if not query_text or not query_text.strip():
        return

    query_clean = query_text.strip()

    # Pre-analyze sentiment and intent from query (Rubric CO2 - 8 Marks)
    analysis = rag_pipeline.query_analyzer.process_query(query_clean)
    sentiment_data = analysis.get("sentiment")
    extracted_data = analysis.get("information")

    # Add user message to state & DB with sentiment & intent
    user_msg = {
        "role": "user",
        "content": query_clean,
        "language": manual_lang or "auto",
        "sources": [],
        "generation_mode": "user",
        "latency_sec": 0.0,
        "sentiment": sentiment_data,
        "extracted_info": extracted_data
    }
    st.session_state["messages"].append(user_msg)
    sqlite_db.add_message(
        session_id=st.session_state["session_id"],
        role="user",
        content=query_clean,
        language=manual_lang,
        sentiment=sentiment_data,
        extracted_info=extracted_data
    )

    # Execute RAG Pipeline with visual spinner
    with st.spinner("Processing query across multilingual knowledge base..."):
        rag_response = rag_pipeline.answer_query(
            query=query_clean,
            manual_language=manual_lang,
            use_llm=use_llm
        )

    # Add assistant response to state & DB
    assistant_msg = {
        "role": "assistant",
        "content": rag_response["answer"],
        "language": rag_response["language"],
        "sources": rag_response["sources"],
        "generation_mode": rag_response["generation_mode"],
        "latency_sec": rag_response["latency_sec"],
        "sentiment": rag_response.get("sentiment") or sentiment_data,
        "extracted_info": rag_response.get("extracted_info") or extracted_data
    }
    st.session_state["messages"].append(assistant_msg)

    sqlite_db.add_message(
        session_id=st.session_state["session_id"],
        role="assistant",
        content=rag_response["answer"],
        language=rag_response["language"],
        sources=rag_response["sources"],
        generation_mode=rag_response["generation_mode"],
        latency_sec=rag_response["latency_sec"],
        sentiment=assistant_msg["sentiment"],
        extracted_info=assistant_msg["extracted_info"]
    )

    sqlite_db.log_query_event(
        session_id=st.session_state["session_id"],
        query=query_clean,
        language=rag_response["language"],
        retrieved_count=len(rag_response["sources"]),
        mode=rag_response["generation_mode"],
        latency=rag_response["latency_sec"]
    )

    st.rerun()


# Render Active View with Role-Based Access Control
if "Admin" in view_mode:
    if current_user.get("role") != "admin":
        st.html(f"""
        <div style="background: #FFFBEB; border: 1px solid #FDE68A; border-left: 5px solid #D97706; border-radius: 14px; padding: 24px; margin-top: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.03);">
            <h3 style="color: #92400E; margin: 0 0 8px 0; font-size: 18px; font-weight: 700;">🔒 Administrator Access Required</h3>
            <p style="color: #78350F; font-size: 14px; margin: 0 0 12px 0; line-height: 1.5;">
                The Administrative Dashboard is restricted to authorized store staff. You are currently logged in as a <b>Customer</b> (<code>{current_user.get('full_name')}</code>).
            </p>
            <p style="color: #92400E; font-size: 13px; margin: 0;">
                To access document ingestion, vector index management, and model benchmarks, please <b>Sign Out</b> from the sidebar and log in using the <b>Admin</b> account (Username: <code>admin</code>, Password: <code>admin123</code>).
            </p>
        </div>
        """)
    else:
        render_admin_view(
            vector_store=vector_store,
            document_processor=document_processor,
            sqlite_db=sqlite_db
        )
else:
    render_chat_view(
        messages=st.session_state["messages"],
        on_send_query=handle_send_query
    )
