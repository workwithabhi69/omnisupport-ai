"""
OmniSupport AI - Visual Design System & Custom CSS.
Full Adaptive Dark/Light Mode + Perfectly Centered & Aligned Chat Composer.
Enterprise AI SaaS styling inspired by Linear, Stripe, Intercom, and ChatGPT.
"""

CUSTOM_CSS = """
<style>
/* -------------------------------------------------------------
   1. GLOBAL TYPOGRAPHY & THEME VARIABLES (ADAPTIVE DARK/LIGHT)
   ------------------------------------------------------------- */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Noto+Sans+Devanagari:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
    --primary: #635BFF;
    --primary-light: #8B5CF6;
    --primary-gradient: linear-gradient(135deg, #635BFF 0%, #8B5CF6 100%);
    --accent-blue: #3B82F6;
    --success: #10B981;
    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 18px;
    --radius-xl: 24px;
    
    /* Default Dark Mode Values (Matches .streamlit/config.toml) */
    --bg-canvas: #0F172A;
    --card-bg: #1E293B;
    --card-border: #334155;
    --border-subtle: #334155;
    --text-main: #F8FAFC;
    --text-muted: #94A3B8;
    --sidebar-bg: #111827;
    --input-bg: #1E293B;
    --input-border: #475569;
    --shadow-card: 0 4px 16px -2px rgba(0, 0, 0, 0.35);
    --shadow-glow: 0 0 20px rgba(99, 91, 255, 0.3);
}

/* Light Theme Overrides (if user explicitly chooses Light in Streamlit menu) */
[data-base-theme="light"],
[data-theme="light"],
body[data-base-theme="light"] {
    --bg-canvas: #F8FAFC;
    --card-bg: #FFFFFF;
    --card-border: #E2E8F0;
    --border-subtle: #E2E8F0;
    --text-main: #1E293B;
    --text-muted: #64748B;
    --sidebar-bg: #FFFFFF;
    --input-bg: #FFFFFF;
    --input-border: #CBD5E1;
    --shadow-card: 0 4px 14px -2px rgba(17, 24, 39, 0.06);
    --shadow-glow: 0 0 20px rgba(99, 91, 255, 0.2);
}

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', 'Noto Sans Devanagari', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    color: var(--text-main);
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

/* App Canvas Background */
.stApp {
    background-color: var(--bg-canvas) !important;
    background-image: 
        radial-gradient(at 0% 0%, rgba(99, 91, 255, 0.05) 0px, transparent 50%),
        radial-gradient(at 100% 100%, rgba(139, 92, 246, 0.05) 0px, transparent 50%) !important;
}

.main .block-container {
    max-width: 1040px;
    padding-top: 1.25rem;
    padding-bottom: 7rem;
}

/* -------------------------------------------------------------
   2. SIDEBAR - COMPACT, MODERN SAAS DASHBOARD (DARK-FIRST)
   ------------------------------------------------------------- */
section[data-testid="stSidebar"] {
    background-color: var(--sidebar-bg) !important;
    border-right: 1px solid var(--border-subtle) !important;
    box-shadow: 2px 0 16px rgba(0, 0, 0, 0.2) !important;
}

section[data-testid="stSidebar"] hr {
    margin: 1.1rem 0 !important;
    border-color: var(--border-subtle) !important;
}

/* Ensure all sidebar radio, selectbox, and toggle labels are visible */
section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
    color: var(--text-main) !important;
    font-weight: 500 !important;
    font-size: 13px !important;
}

/* Sidebar Section Headers */
.sidebar-section-title {
    font-size: 10.5px;
    font-weight: 700;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.6px;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 6px;
}

/* Profile Card */
.sidebar-profile-card {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: var(--radius-md);
    padding: 12px 14px;
    box-shadow: var(--shadow-card);
    transition: all 0.2s ease;
}

.sidebar-profile-avatar {
    width: 36px;
    height: 36px;
    border-radius: 10px;
    background: var(--primary-gradient);
    color: #FFFFFF;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 13px;
    box-shadow: 0 2px 8px rgba(99, 91, 255, 0.35);
}

/* Status Pill */
.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    padding: 7px 14px;
    border-radius: 9999px;
    font-size: 11.5px;
    font-weight: 600;
    width: 100%;
    justify-content: center;
}

.status-pill.online {
    background-color: rgba(16, 185, 129, 0.15);
    color: #6EE7B7;
    border: 1px solid rgba(16, 185, 129, 0.35);
}

.status-pill.offline {
    background-color: rgba(245, 158, 11, 0.15);
    color: #FCD34D;
    border: 1px solid rgba(245, 158, 11, 0.35);
}

.pulse-indicator {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background-color: #10B981;
    box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
    70% { transform: scale(1); box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }
    100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
}

/* -------------------------------------------------------------
   3. HERO SECTION - STRIPE & LINEAR INSPIRED
   ------------------------------------------------------------- */
.hero-card {
    background: linear-gradient(135deg, #0B0F19 0%, #111827 45%, #1E1B4B 100%);
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: #FFFFFF;
    padding: 28px 34px;
    border-radius: var(--radius-xl);
    margin-bottom: 22px;
    box-shadow: 0 16px 36px -6px rgba(0, 0, 0, 0.45);
    position: relative;
    overflow: hidden;
}

.hero-card::after {
    content: '';
    position: absolute;
    top: -60px;
    right: -40px;
    width: 280px;
    height: 280px;
    background: radial-gradient(circle, rgba(99, 91, 255, 0.3) 0%, rgba(139, 92, 246, 0.05) 60%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
}

.hero-brand {
    display: flex;
    align-items: center;
    gap: 14px;
}

.hero-logo-box {
    width: 48px;
    height: 48px;
    border-radius: var(--radius-md);
    background: var(--primary-gradient);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    box-shadow: var(--shadow-glow);
}

.hero-title {
    font-size: 27px;
    font-weight: 800;
    letter-spacing: -0.6px;
    margin: 0;
    color: #FFFFFF !important;
    display: flex;
    align-items: center;
    gap: 10px;
}

.hero-version-badge {
    font-size: 11px;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 9999px;
    background: rgba(99, 91, 255, 0.25);
    color: #C7D2FE;
    border: 1px solid rgba(139, 92, 246, 0.4);
    letter-spacing: 0.3px;
    text-transform: uppercase;
}

.hero-tagline {
    font-size: 14.5px;
    font-weight: 600;
    color: #E2E8F0;
    margin: 6px 0 4px 0;
}

.hero-desc {
    font-size: 13.5px;
    color: #94A3B8;
    margin: 0 0 14px 0;
    max-width: 720px;
    line-height: 1.5;
}

.hero-indicators-bar {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.hero-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 5px 12px;
    border-radius: 9999px;
    font-size: 11.5px;
    font-weight: 600;
    background: rgba(255, 255, 255, 0.08);
    color: #F1F5F9;
    border: 1px solid rgba(255, 255, 255, 0.12);
    backdrop-filter: blur(8px);
}

/* -------------------------------------------------------------
   4. WELCOME & EMPTY STATE
   ------------------------------------------------------------- */
.welcome-container {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: var(--radius-xl);
    padding: 32px 36px;
    text-align: center;
    box-shadow: var(--shadow-card);
    margin-bottom: 24px;
}

.welcome-badge-icon {
    width: 60px;
    height: 60px;
    border-radius: 18px;
    background: linear-gradient(135deg, rgba(99, 91, 255, 0.2), rgba(139, 92, 246, 0.25));
    color: #A78BFA;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 30px;
    margin-bottom: 14px;
    box-shadow: 0 4px 16px rgba(99, 91, 255, 0.2);
}

.welcome-title {
    font-size: 22px;
    font-weight: 800;
    color: var(--text-main);
    letter-spacing: -0.4px;
    margin-bottom: 6px;
}

.welcome-subtitle {
    font-size: 14px;
    color: var(--text-muted);
    max-width: 620px;
    margin: 0 auto 24px auto;
    line-height: 1.5;
}

.welcome-feature-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin-top: 18px;
}

.welcome-feature-card {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid var(--card-border);
    border-radius: var(--radius-md);
    padding: 16px 14px;
    text-align: left;
    transition: all 0.2s ease;
}

.welcome-feature-card:hover {
    border-color: var(--primary);
    transform: translateY(-2px);
}

.welcome-feature-heading {
    font-size: 13px;
    font-weight: 700;
    color: var(--text-main);
    margin-bottom: 3px;
}

.welcome-feature-desc {
    font-size: 11.5px;
    color: var(--text-muted);
    line-height: 1.4;
}

/* -------------------------------------------------------------
   5. QUICK INQUIRY CARDS (ADAPTIVE BUTTONS)
   ------------------------------------------------------------- */
.quick-inquiry-header {
    font-size: 12px;
    font-weight: 700;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.6px;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 6px;
}

.stButton button {
    border-radius: var(--radius-md) !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    padding: 11px 16px !important;
    background: var(--card-bg) !important;
    border: 1px solid var(--card-border) !important;
    color: var(--text-main) !important;
    box-shadow: var(--shadow-card) !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    text-align: left !important;
    width: 100% !important;
}

.stButton button:hover {
    border-color: var(--primary) !important;
    color: #A78BFA !important;
    background: rgba(99, 91, 255, 0.1) !important;
    transform: translateY(-2px) !important;
}

/* -------------------------------------------------------------
   6. CHAT THREAD & MESSAGES
   ------------------------------------------------------------- */
.user-row {
    display: flex;
    justify-content: flex-end;
    align-items: flex-start;
    gap: 12px;
    margin-bottom: 14px;
}

.user-bubble-box {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    max-width: 78%;
}

.user-bubble {
    background: var(--primary-gradient);
    color: #FFFFFF !important;
    padding: 14px 20px;
    border-radius: 20px 20px 4px 20px;
    box-shadow: 0 4px 16px rgba(99, 91, 255, 0.35);
    font-size: 14.5px;
    line-height: 1.55;
    font-weight: 500;
}

.user-avatar {
    width: 34px;
    height: 34px;
    border-radius: 50%;
    background: linear-gradient(135deg, #334155, #1E293B);
    color: #FFFFFF;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 13px;
    font-weight: 700;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
    flex-shrink: 0;
    margin-top: 4px;
}

.user-meta-bar {
    display: flex;
    gap: 6px;
    margin-top: 6px;
    align-items: center;
}

/* Assistant Message Block */
.assistant-row {
    display: flex;
    justify-content: flex-start;
    align-items: flex-start;
    gap: 12px;
    margin-bottom: 18px;
}

.assistant-avatar {
    width: 36px;
    height: 36px;
    border-radius: 12px;
    background: var(--primary-gradient);
    color: #FFFFFF;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    box-shadow: var(--shadow-glow);
    flex-shrink: 0;
    margin-top: 4px;
}

.assistant-bubble-box {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    max-width: 86%;
}

.assistant-bubble {
    background: var(--card-bg);
    color: var(--text-main) !important;
    padding: 20px 24px;
    border-radius: 4px 20px 20px 20px;
    border: 1px solid var(--card-border);
    box-shadow: var(--shadow-card);
    font-size: 14.5px;
    line-height: 1.65;
    width: 100%;
}

.assistant-card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--border-subtle);
}

.assistant-name {
    font-size: 13px;
    font-weight: 700;
    color: var(--text-main);
    display: flex;
    align-items: center;
    gap: 6px;
}

.verified-badge {
    font-size: 11px;
    font-weight: 700;
    color: #6EE7B7;
    background: rgba(16, 185, 129, 0.15);
    border: 1px solid rgba(16, 185, 129, 0.35);
    padding: 2px 8px;
    border-radius: 9999px;
    display: inline-flex;
    align-items: center;
    gap: 4px;
}

.assistant-body {
    color: var(--text-main);
    font-size: 14.5px;
    line-height: 1.65;
}

/* -------------------------------------------------------------
   7. METADATA PILL BADGES (GLOWING DARK COMPATIBLE)
   ------------------------------------------------------------- */
.meta-footer-bar {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-top: 14px;
    padding-top: 10px;
    border-top: 1px dashed var(--border-subtle);
    align-items: center;
}

.pill-badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 3px 9px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: -0.1px;
    line-height: 1.3;
}

.pill-badge.lang-en { background: rgba(59, 130, 246, 0.15); color: #93C5FD; border: 1px solid rgba(59, 130, 246, 0.35); }
.pill-badge.lang-hi { background: rgba(249, 115, 22, 0.15); color: #FDBA74; border: 1px solid rgba(249, 115, 22, 0.35); }
.pill-badge.lang-mr { background: rgba(236, 72, 153, 0.15); color: #F472B6; border: 1px solid rgba(236, 72, 153, 0.35); }

.pill-badge.mode-grounded { background: rgba(16, 185, 129, 0.15); color: #6EE7B7; border: 1px solid rgba(16, 185, 129, 0.35); }
.pill-badge.mode-llm { background: rgba(139, 92, 246, 0.15); color: #C4B5FD; border: 1px solid rgba(139, 92, 246, 0.35); }
.pill-badge.mode-praise { background: rgba(244, 63, 94, 0.15); color: #FDA4AF; border: 1px solid rgba(244, 63, 94, 0.35); }
.pill-badge.mode-scope { background: rgba(245, 158, 11, 0.15); color: #FCD34D; border: 1px solid rgba(245, 158, 11, 0.35); }

.pill-badge.latency { background: rgba(255, 255, 255, 0.06); color: #CBD5E1; border: 1px solid rgba(255, 255, 255, 0.12); font-family: 'JetBrains Mono', monospace; }
.pill-badge.intent { background: rgba(56, 189, 248, 0.15); color: #7DD3FC; border: 1px solid rgba(56, 189, 248, 0.35); }

.pill-badge.sent-pos { background: rgba(16, 185, 129, 0.15); color: #6EE7B7; border: 1px solid rgba(16, 185, 129, 0.35); }
.pill-badge.sent-neu { background: rgba(255, 255, 255, 0.06); color: #CBD5E1; border: 1px solid rgba(255, 255, 255, 0.12); }
.pill-badge.sent-neg { background: rgba(239, 68, 68, 0.15); color: #FCA5A5; border: 1px solid rgba(239, 68, 68, 0.35); }

.pill-badge.entity-curr { background: rgba(245, 158, 11, 0.15); color: #FCD34D; border: 1px solid rgba(245, 158, 11, 0.35); }
.pill-badge.entity-order { background: rgba(16, 185, 129, 0.15); color: #6EE7B7; border: 1px solid rgba(16, 185, 129, 0.35); }
.pill-badge.entity-time { background: rgba(168, 85, 247, 0.15); color: #D8B4FE; border: 1px solid rgba(168, 85, 247, 0.35); }

/* -------------------------------------------------------------
   8. CITATIONS & AUDIT LOG EXPANDER (STREAMLIT NATIVE COMPATIBLE)
   ------------------------------------------------------------- */
div[data-testid="stExpander"] {
    background: var(--card-bg) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-md) !important;
    box-shadow: var(--shadow-card) !important;
    margin-top: 8px !important;
}

div[data-testid="stExpander"] summary {
    color: var(--text-main) !important;
    font-weight: 600 !important;
    font-size: 13px !important;
}

.source-card {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid var(--card-border);
    border-left: 4px solid var(--primary);
    border-radius: var(--radius-sm);
    padding: 12px 16px;
    margin-top: 8px;
    font-size: 12.5px;
}

.source-title {
    font-weight: 700;
    color: var(--text-main);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.source-similarity {
    font-weight: 700;
    font-size: 11px;
    background: rgba(16, 185, 129, 0.15);
    color: #6EE7B7;
    border: 1px solid rgba(16, 185, 129, 0.35);
    padding: 2px 8px;
    border-radius: 6px;
}

/* -------------------------------------------------------------
   9. PERFECTLY ALIGNED BOTTOM CHAT INPUT
   ------------------------------------------------------------- */
/* Target Streamlit's bottom container */
div[data-testid="stBottom"] {
    background: transparent !important;
    padding-bottom: 24px !important;
}

div[data-testid="stBottom"] > div {
    width: 100% !important;
    max-width: 1000px !important;
    margin: 0 auto !important;
    padding: 0 !important;
}

/* The actual chat input element */
div[data-testid="stChatInput"] {
    width: 100% !important;
    max-width: 1000px !important;
    margin: 0 auto !important;
    padding: 0 !important;
}

div[data-testid="stChatInput"] > div {
    border-radius: 20px !important;
    border: 1.5px solid var(--input-border) !important;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.35) !important;
    background: var(--input-bg) !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    padding: 2px 4px !important;
}

div[data-testid="stChatInput"] > div:focus-within {
    border-color: #635BFF !important;
    box-shadow: 0 8px 32px rgba(99, 91, 255, 0.35), 0 0 0 3px rgba(99, 91, 255, 0.2) !important;
}

div[data-testid="stChatInput"] textarea {
    color: var(--text-main) !important;
    font-family: 'Plus Jakarta Sans', 'Noto Sans Devanagari', sans-serif !important;
    font-size: 14.5px !important;
    background: transparent !important;
}

div[data-testid="stChatInput"] textarea::placeholder {
    color: var(--text-muted) !important;
    opacity: 0.8 !important;
}

div[data-testid="stChatInput"] button {
    color: #635BFF !important;
    transition: transform 0.15s ease !important;
}

div[data-testid="stChatInput"] button:hover {
    transform: scale(1.1) !important;
}

/* -------------------------------------------------------------
   10. ADMIN & EVALUATION DASHBOARD STYLING
   ------------------------------------------------------------- */
.admin-header-card {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: var(--radius-lg);
    padding: 24px 28px;
    margin-bottom: 24px;
    box-shadow: var(--shadow-card);
}

.metric-card-modern {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-top: 3px solid var(--primary);
    border-radius: var(--radius-md);
    padding: 16px 20px;
    box-shadow: var(--shadow-card);
    transition: all 0.2s ease;
}

.metric-card-modern:hover {
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
    transform: translateY(-2px);
}

.metric-val {
    font-size: 26px;
    font-weight: 800;
    color: var(--text-main);
    letter-spacing: -0.5px;
}

.metric-lbl {
    font-size: 11px;
    font-weight: 700;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-top: 2px;
}

/* Streamlit Tabs Customization */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    border-bottom: 1px solid var(--border-subtle);
    padding-bottom: 4px;
}

.stTabs [data-baseweb="tab"] {
    border-radius: var(--radius-sm) !important;
    padding: 8px 16px !important;
    font-weight: 600 !important;
    font-size: 13.5px !important;
    color: var(--text-muted) !important;
}

.stTabs [aria-selected="true"] {
    background-color: rgba(99, 91, 255, 0.15) !important;
    color: #A78BFA !important;
    font-weight: 700 !important;
}
</style>
"""


def apply_theme():
    import streamlit as st
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
