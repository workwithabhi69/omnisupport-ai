# OmniSupport AI: Multilingual E-Commerce Customer Support Chatbot
### Grounded Retrieval-Augmented Generation (RAG) • Multilingual NLP • Open-Source LLM (Qwen2.5)

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B.svg)](https://streamlit.io/)
[![ChromaDB](https://img.shields.io/badge/Vector%20DB-ChromaDB-orange.svg)](https://www.trychroma.com/)
[![Embeddings](https://img.shields.io/badge/Embeddings-Multilingual--E5--Small-green.svg)](https://huggingface.co/intfloat/multilingual-e5-small)
[![LLM](https://img.shields.io/badge/LLM-Qwen2.5--0.5B%20%2F%20Ollama-purple.svg)](https://ollama.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📌 1. Project Overview

**OmniSupport AI** is an intelligent, enterprise-grade multilingual customer support conversational AI system built for modern e-commerce platforms. It resolves customer inquiries with zero hallucinations across three primary languages:
- **English**
- **Hindi (हिंदी)**
- **Marathi (मराठी)**

Traditional customer service chatbots either rely on rigid rule-based decision trees or hallucinate policies using ungrounded generative models. Furthermore, most commercial chatbots struggle with Devanagari script differentiation between Hindi and Marathi. 

OmniSupport AI overcomes these barriers using **Grounded Retrieval-Augmented Generation (RAG)**: customer queries are matched semantically against verified store policy documents via dense vector search in **ChromaDB**, and synthesized with strict factual grounding through an open-source **Qwen2.5** Large Language Model (or high-precision grounded policy synthesis).

---

## 🎯 2. Project Objectives

1. **Native Trilingual Understanding:** Accurately classify, detect, and answer customer inquiries in English, Hindi, and Marathi without script cross-mixing or transliteration artifacts.
2. **Strict Factual Grounding (Zero Hallucination):** Ensure 100% of generated responses are strictly derived from official store policy clauses (delivery timelines, returns, refunds, cancellations, warranties).
3. **Devanagari Disambiguation:** Differentiate grammatically overlapping Hindi and Marathi text through hybrid script-lexical discriminant analysis (e.g., lexical markers like *ळ, साठी, आहे, परतावा* vs. *है, के लिए, रिफंड*).
4. **Sentiment & Information Extraction:** Automatically classify customer sentiment (Positive, Neutral, Urgent/Negative) and extract intent (Delivery, Refund, Return, Cancellation, Warranty) to assist support workflows.
5. **Sub-Second Low-Latency Retrieval:** Execute vector similarity searches in $< 100\text{ ms}$ using 384-dimensional dense multilingual sentence embeddings.
6. **Zero Paid API Cost / 100% Open-Source:** Fully operational locally via **Ollama** or cloud-deployed via **Hugging Face Serverless Inference** with zero recurring commercial API expenditure.

---

## 💻 3. Technologies & Stack

| Layer | Technology | Purpose & Role |
|---|---|---|
| **User Interface** | **Streamlit 1.35+** | Dark-mode, responsive chat UI, quick inquiry chips, admin & evaluation dashboard |
| **Language Identification** | **Langdetect + Custom Devanagari Discriminator** | Script separation (Latin vs. Devanagari) + high-precision Marathi/Hindi marker heuristics |
| **Text Embeddings** | **`intfloat/multilingual-e5-small`** | 384-dimensional dense vectors fine-tuned for multilingual asymmetric retrieval |
| **Vector Store** | **ChromaDB 0.5+** | Persistent embedded vector database with Cosine Similarity indexing and language filtering |
| **Large Language Model** | **Qwen2.5 (0.5B / 1.5B)** | Open-source multilingual instruction-tuned LLM accessed via Ollama or Hugging Face |
| **Document Ingestion** | **PyPDF, PyMuPDF, python-docx** | Multi-format document parser for PDF, DOCX, and TXT policy files |
| **Data Persistence** | **SQLite3** | Session tracking, chat history storage, query telemetry, and sentiment logging |
| **Evaluation Suite** | **Scikit-learn, NumPy, Pandas** | Macro F1, Precision@K, Mean Reciprocal Rank (MRR), and latency benchmarking |

---

## 🔬 4. Methodology

The system operates across a 5-stage NLP and machine learning pipeline:

### A. Document Ingestion & Boundary-Aware Chunking
1. Policy documents (`.txt`, `.pdf`, `.docx`) across 6 retail domains are ingested.
2. Text undergoes NFKC Unicode normalization and whitespace cleaning.
3. A **boundary-aware sentence chunker** splits texts into segments of 300–500 characters with a 50-character overlap, strictly ensuring Devanagari orphan matras and split vowel signs are eliminated.
4. Chunks are tagged with category, source, and language metadata (`en`, `hi`, `mr`).

### B. Dense Vector Embedding & Indexing
1. Embeddings are generated using `intfloat/multilingual-e5-small` with `passage: ` prefixes.
2. Chunks are indexed into ChromaDB collections using Cosine Distance metrics ($d = 1 - \cos(\theta)$).
3. 51 high-quality semantic chunks across 12 policy documents are persistently indexed.

### C. Hybrid Language & Intent Detection
1. Queries are analyzed for Latin vs. Devanagari Unicode code points.
2. If Devanagari is detected, the custom lexical discriminator checks for unique Marathi grammatical morphemes (`आहे`, `नाही`, `कसे`, `किती`, `साठी`, `परतावा`, `मिळेल`, `ळ`) versus Hindi markers (`है`, `नहीं`, `कब`, `कितना`, `के लिए`, `रिफंड`).
3. Lexicon-based sentiment polarity (Positive, Neutral, Negative) and intent classification are computed simultaneously.

### D. Semantic Vector Retrieval & Filtering
1. Incoming queries are embedded with the `query: ` prefix.
2. ChromaDB searches the top-$K$ ($K=4$) most relevant chunks with a minimum similarity threshold ($0.80$).
3. Queries with explicit language selection utilize metadata pre-filtering to prevent cross-language retrieval noise.

### E. Grounded Response Generation & Dual LLM Routing
1. Retrieved context is injected into a strict system prompt tailored to the query language.
2. If **Ollama** is active locally or via GPU tunnel, inference runs locally on `qwen2.5:0.5b`.
3. If deployed on Streamlit Cloud, it connects to **Hugging Face Serverless Inference** (`Qwen/Qwen2.5-0.5B-Instruct`).
4. If an LLM is offline, the pipeline seamlessly transitions to **Grounded Fallback Synthesis**, delivering exact policy points directly with zero downtime.

---

## 🏗️ 5. System Architecture & Workflow
