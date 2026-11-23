"""
Chat Interface Component for Multilingual Customer Queries.
Linear & Intercom-inspired conversation interface.
Renders Hero Section, Welcome Area, Quick Inquiry Cards,
ChatGPT-style message threads with distinct avatars, timestamps, and pill badges.
"""

import streamlit as st
from typing import List, Dict, Any, Callable


QUICK_INQUIRIES = [
    {
        "id": "del_en",
        "title": "Delivery Timelines",
        "subtitle": "Shipping duration & charges",
        "icon": "🚚",
        "query": "How long does standard delivery take?",
        "tag": "English"
    },
    {
        "id": "ret_en",
        "title": "Return Policy",
        "subtitle": "7-day policy & condition rules",
        "icon": "📦",
        "query": "How can I return my product?",
        "tag": "English"
    },
    {
        "id": "del_hi",
        "title": "डिलीवरी का समय",
        "subtitle": "शिपिंग चार्ज और समय सीमा",
        "icon": "🇮🇳",
        "query": "डिलीवरी में कितना समय लगता है?",
        "tag": "Hindi"
    },
    {
        "id": "ref_hi",
        "title": "रिफंड प्रक्रिया",
        "subtitle": "बैंक खाते में पैसे कब मिलेंगे",
        "icon": "💳",
        "query": "मेरा रिफंड कब मिलेगा?",
        "tag": "Hindi"
    },
    {
        "id": "del_mr",
        "title": "डिलिव्हरी वेळ",
        "subtitle": "पार्सल पोहोचण्यास किती दिवस",
        "icon": "🚩",
        "query": "डिलिव्हरीसाठी किती वेळ लागतो?",
        "tag": "Marathi"
    },
    {
        "id": "ret_mr",
        "title": "उत्पादन परतावा",
        "subtitle": "वस्तू परत करण्याचे अधिकृत नियम",
        "icon": "🔄",
        "query": "मी माझे उत्पादन परत कसे करू शकतो?",
        "tag": "Marathi"
    }
]


def render_chat_view(
    messages: List[Dict[str, Any]],
    on_send_query: Callable[[str], None]
):
    # ---------------------------------------------------------
    # 1. HERO SECTION (Linear / Stripe Inspired)
    # ---------------------------------------------------------
    st.html("""
    <div class="hero-card">
        <div class="hero-header-row">
            <div class="hero-brand">
                <div class="hero-logo-box">🛍️</div>
                <div>
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <h1 class="hero-title">OmniSupport AI</h1>
                        <span class="hero-version-badge">Version 2.5</span>
                    </div>
                    <div class="hero-tagline">Intelligent Multilingual Customer Support</div>
                </div>
            </div>
        </div>
        <p class="hero-desc">
            Your AI-powered assistant for orders, deliveries, returns, refunds and payments.
        </p>
        <div class="hero-indicators-bar">
            <span class="hero-pill">
                <span class="pulse-indicator"></span> Online & Grounded
            </span>
            <span class="hero-pill">🌐 English, Hindi & Marathi</span>
            <span class="hero-pill">⚡ Sub-Second Retrieval</span>
            <span class="hero-pill">🛡️ Zero Hallucinations</span>
        </div>
    </div>
    """)

    # ---------------------------------------------------------
    # 2. WELCOME / EMPTY STATE
    # ---------------------------------------------------------
    if not messages:
        st.html("""
        <div class="welcome-container">
            <div class="welcome-badge-icon">✨</div>
            <div class="welcome-title">Namaste! Welcome to OmniSupport AI 👋</div>
            <div class="welcome-subtitle">
                Your intelligent multilingual shopping assistant. Ask anything about your orders, deliveries, returns or payments.
            </div>
            <div class="welcome-feature-grid">
                <div class="welcome-feature-card">
                    <div class="welcome-feature-icon">⚡</div>
                    <div class="welcome-feature-heading">Sub-Second Precision</div>
                    <div class="welcome-feature-desc">Official policy retrieval in under 0.1s with zero hallucinations.</div>
                </div>
                <div class="welcome-feature-card">
                    <div class="welcome-feature-icon">🌐</div>
                    <div class="welcome-feature-heading">Native Trilingual</div>
                    <div class="welcome-feature-desc">Fluency in English, शुद्ध हिंदी, and अस्खलित मराठी without script cross-mixing.</div>
                </div>
                <div class="welcome-feature-card">
                    <div class="welcome-feature-icon">🛡️</div>
                    <div class="welcome-feature-heading">Grounded Knowledge</div>
                    <div class="welcome-feature-desc">Every response is strictly verified against indexed retail store guidelines.</div>
                </div>
            </div>
        </div>
        """)

    # ---------------------------------------------------------
    # 3. QUICK INQUIRY CARDS (Responsive 3-column layout)
    # ---------------------------------------------------------
    st.html("""
    <div class="quick-inquiry-header">
        <span>💡</span> Quick Inquiries / वारंवार विचारले जाणारे प्रश्न / अक्सर पूछे जाने वाले सवाल:
    </div>
    """)

    cols = st.columns(3)
    for idx, card in enumerate(QUICK_INQUIRIES):
        col = cols[idx % 3]
        with col:
            button_label = f"{card['icon']}  {card['title']}"
            if st.button(button_label, key=f"qi_{card['id']}", use_container_width=True, help=f"{card['subtitle']} ({card['tag']})"):
                on_send_query(card["query"])

    st.html("<div style='height: 18px;'></div>")

    # ---------------------------------------------------------
    # 4. CHAT THREAD (ChatGPT / Intercom Inspired)
    # ---------------------------------------------------------
    if messages:
        for idx, msg in enumerate(messages):
            role = msg.get("role", "user")
            content = msg.get("content", "")
            lang = msg.get("language", "en")
            latency = msg.get("latency_sec", 0.0)
            mode = msg.get("generation_mode", "llm")
            sources = msg.get("sources", [])

            if role == "user":
                sentiment_obj = msg.get("sentiment", {}) or {}
                sentiment_badge = sentiment_obj.get("badge", "😐 Neutral")
                polarity = sentiment_obj.get("polarity", 0.0)
                info_obj = msg.get("extracted_info", {}) or {}
                intent_label = info_obj.get("intent", "General Inquiry")

                sent_class = "sent-neu"
                if polarity > 0.1:
                    sent_class = "sent-pos"
                elif polarity < -0.1:
                    sent_class = "sent-neg"

                user_html = (
                    f'<div class="user-row">'
                    f'<div class="user-bubble-box">'
                    f'<div class="user-bubble">{content}</div>'
                    f'<div class="user-meta-bar">'
                    f'<span class="pill-badge intent">🎯 {intent_label}</span>'
                    f'<span class="pill-badge {sent_class}">{sentiment_badge}</span>'
                    f'</div>'
                    f'</div>'
                    f'<div class="user-avatar">👤</div>'
                    f'</div>'
                )
                st.html(user_html)

            else:
                # Assistant Language Badge
                if lang == "hi":
                    lang_label = "🇮🇳 हिंदी"
                    lang_class = "lang-hi"
                elif lang == "mr":
                    lang_label = "🚩 मराठी"
                    lang_class = "lang-mr"
                else:
                    lang_label = "🇬🇧 English"
                    lang_class = "lang-en"

                # Assistant Generation Mode Badge
                if mode == "retrieval_fallback":
                    mode_label = "⚡ Grounded Policy"
                    mode_class = "mode-grounded"
                elif mode == "out_of_scope":
                    mode_label = "🚫 Out of Scope"
                    mode_class = "mode-scope"
                elif mode == "gratitude_feedback":
                    mode_label = "💖 Customer Praise"
                    mode_class = "mode-praise"
                else:
                    mode_label = "🤖 Qwen2.5 LLM"
                    mode_class = "mode-llm"

                sentiment_obj = msg.get("sentiment", {}) or {}
                sentiment_badge = sentiment_obj.get("badge", "😐 Neutral")
                polarity = sentiment_obj.get("polarity", 0.0)
                sent_class = "sent-neu"
                if polarity > 0.1:
                    sent_class = "sent-pos"
                elif polarity < -0.1:
                    sent_class = "sent-neg"

                info_obj = msg.get("extracted_info", {}) or {}
                intent_label = info_obj.get("intent", "General Inquiry")
                currencies = info_obj.get("extracted_currency_amounts", [])
                timelines = info_obj.get("extracted_timelines", [])
                order_ids = info_obj.get("extracted_order_ids", [])

                entity_chips = ""
                if currencies:
                    entity_chips += f'<span class="pill-badge entity-curr">💰 {", ".join(currencies)}</span>'
                if timelines:
                    entity_chips += f'<span class="pill-badge entity-time">⏳ {", ".join(timelines)}</span>'
                if order_ids:
                    entity_chips += f'<span class="pill-badge entity-order">📦 {", ".join(order_ids)}</span>'

                formatted_body = content.replace(chr(10), "<br>")

                assistant_html = (
                    f'<div class="assistant-row">'
                    f'<div class="assistant-avatar">⚡</div>'
                    f'<div class="assistant-bubble-box">'
                    f'<div class="assistant-bubble">'
                    f'<div class="assistant-card-header">'
                    f'<div class="assistant-name">OmniSupport AI</div>'
                    f'<span class="verified-badge">✓ Verified Policy</span>'
                    f'</div>'
                    f'<div class="assistant-body">{formatted_body}</div>'
                    f'<div class="meta-footer-bar">'
                    f'<span class="pill-badge {lang_class}">{lang_label}</span>'
                    f'<span class="pill-badge {mode_class}">{mode_label}</span>'
                    f'<span class="pill-badge latency">⏱️ {latency:.2f}s</span>'
                    f'<span class="pill-badge {sent_class}">{sentiment_badge} ({polarity:+.2f})</span>'
                    f'<span class="pill-badge intent">🎯 {intent_label}</span>'
                    f'{entity_chips}'
                    f'</div>'
                    f'</div>'
                    f'</div>'
                    f'</div>'
                )
                st.html(assistant_html)

                # Grounded Citations Accordion
                if sources:
                    with st.expander(f"📚 Grounded Knowledge Sources ({len(sources)} cited policy sections)", expanded=False):
                        for s_idx, src in enumerate(sources, start=1):
                            sim_pct = src.get("similarity", 0) * 100
                            source_card_html = (
                                f'<div class="source-card">'
                                f'<div class="source-title">'
                                f'<span>#{s_idx} Document: <code>{src.get("source")}</code> ({src.get("category")})</span>'
                                f'<span class="source-similarity">Relevance: {sim_pct:.1f}%</span>'
                                f'</div>'
                                f'<div style="margin-top: 6px; color: #475569; font-style: italic; font-size: 12px; line-height: 1.5;">"{src.get("content_preview")}"</div>'
                                f'</div>'
                            )
                            st.html(source_card_html)

            st.html("<div style='height: 10px;'></div>")

    # ---------------------------------------------------------
    # 5. FLOATING MESSAGE COMPOSER
    # ---------------------------------------------------------
    user_query = st.chat_input("Ask anything in English, हिन्दी or मराठी... (e.g. 'How long does delivery take?')")
    if user_query:
        on_send_query(user_query)
