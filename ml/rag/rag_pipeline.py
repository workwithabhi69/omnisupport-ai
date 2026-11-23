"""
Grounded Multilingual Retrieval-Augmented Generation (RAG) Pipeline.
Workflow:
Query -> Language Detection -> Preprocessing -> Multilingual Embedding ->
ChromaDB Semantic Search -> Context Grounding -> Open-Source LLM (Qwen2.5) ->
Validation -> Source References & Display.
Includes an intelligent Grounded Retrieval Fallback if Ollama is unavailable.
"""

import time
import re
from typing import Dict, Any, List, Optional
from ml.language_detection.detector import LanguageDetector
from ml.retrieval.vector_store import VectorStoreManager
from ml.rag.ollama_client import OllamaClient
from ml.sentiment_extraction.analyzer import CustomerQueryAnalyzer


class MultilingualRAGPipeline:
    # Grounded system prompts per language
    SYSTEM_PROMPTS = {
        "en": (
            "You are a helpful and polite multilingual e-commerce customer support assistant. "
            "Answer the customer's question concisely in 2-3 clear sentences based ONLY on the provided official policy context. "
            "Explain the store's policy rules (such as return windows, refund timelines, or delivery terms) clearly. "
            "Do not repeat sentences. If the context has no relevant policy, politely say you don't have enough policy information. "
            "Always respond in English."
        ),
        "hi": (
            "आप एक विनम्र और सहायक ई-कॉमर्स ग्राहक सेवा सहायक हैं। "
            "नीचे दिए गए आधिकारिक नीति संदर्भ (Policy Context) के आधार पर ग्राहक के प्रश्न का 2-3 वाक्यों में संक्षिप्त और सटीक उत्तर दें। "
            "वाक्यों को बार-बार न दोहराएं। केवल आधिकारिक नीति की जानकारी दें। "
            "हमेशा स्पष्ट और शुद्ध हिंदी में ही उत्तर दें।"
        ),
        "mr": (
            "तुम्ही एक विनम्र आणि अधिकृत ई-कॉमर्स ग्राहक सेवा सहाय्यक आहात. "
            "खाली दिलेल्या अधिकृत धोरण संदर्भाचा (Policy Context) वापर करून ग्राहकाच्या प्रश्नाचे 2-3 वाक्यांत अचूक आणि संक्षिप्त उत्तर द्या. "
            "उत्तर फक्त आणि फक्त शुद्ध मराठी भाषेतच द्या (हिंदी शब्द वापरू नका). "
            "वाक्ये पुन्हा पुन्हा बोलू नका."
        )
    }

    # Standard "No relevant information found" messages
    OUT_OF_SCOPE_MESSAGES = {
        "en": (
            "I'm sorry, I could not find relevant information in our store policies regarding your query. "
            "For further assistance, please contact our 24/7 customer care team at support@ecommerce-store.demo."
        ),
        "hi": (
            "क्षमा करें, आपके प्रश्न के संबंध में हमारी स्टोर नीतियों में कोई प्रासंगिक जानकारी नहीं मिली। "
            "अधिक सहायता के लिए, कृपया हमारी ग्राहक सहायता टीम से support@ecommerce-store.demo पर संपर्क करें।"
        ),
        "mr": (
            "माफ करा, आपल्या प्रश्नासंदर्भात आमच्या स्टोअर पॉलिसींमध्ये कोणतीही संबंधित माहिती आढळली नाही. "
            "पुढील मदतीसाठी, कृपया आमच्या ग्राहक सेवा टीमशी support@ecommerce-store.demo वर संपर्क साधा."
        )
    }

    # Gracious responses for customer appreciation / gratitude
    GRATITUDE_RESPONSES = {
        "en": "Thank you so much for your kind words and positive feedback! We are thrilled to hear you had a great experience with our store. Please let us know if there is anything else we can assist you with!",
        "hi": "आपकी सकारात्मक प्रतिक्रिया और धन्यवाद के लिए बहुत-बहुत आभार! हमें अत्यंत खुशी है कि आपको हमारी सेवा और उत्पाद पसंद आए। किसी भी अन्य सहायता के लिए हम सदैव तत्पर हैं।",
        "mr": "आपल्या सकारात्मक प्रतिसादाबद्दल आणि शुभेच्छांबद्दल मनःपूर्वक धन्यवाद! आपल्याला आमची सेवा आणि उत्पादने आवडली याचा आम्हाला अत्यंत आनंद आहे. इतर कोणत्याही मदतीसाठी आम्ही सदैव उपलब्ध आहोत."
    }

    def __init__(
        self,
        vector_store: Optional[VectorStoreManager] = None,
        language_detector: Optional[LanguageDetector] = None,
        ollama_client: Optional[OllamaClient] = None
    ):
        self.language_detector = language_detector or LanguageDetector()
        self.vector_store = vector_store or VectorStoreManager()
        self.ollama_client = ollama_client or OllamaClient()
        self.query_analyzer = CustomerQueryAnalyzer()

    def _format_context(self, chunks: List[Dict[str, Any]]) -> str:
        """Formats retrieved chunks into numbered context blocks."""
        formatted_blocks = []
        for i, chunk in enumerate(chunks, 1):
            source = chunk.get("metadata", {}).get("source", "Document")
            cat = chunk.get("metadata", {}).get("category", "Policy")
            content = chunk.get("content", "").strip()
            formatted_blocks.append(f"[Document {i} - {source} ({cat})]:\n{content}")
        return "\n\n".join(formatted_blocks)

    def _grounded_fallback_synthesis(
        self,
        query: str,
        retrieved_chunks: List[Dict[str, Any]],
        language: str
    ) -> str:
        """
        Synthesizes an authoritative grounded response directly from policy chunks
        matching the customer query, scoring relevance to the query.
        """
        if not retrieved_chunks:
            return self.OUT_OF_SCOPE_MESSAGES.get(language, self.OUT_OF_SCOPE_MESSAGES["en"])

        # Prioritize chunks matching the target language
        lang_chunks = [c for c in retrieved_chunks if c.get("metadata", {}).get("language") == language]
        chunks_to_use = lang_chunks if lang_chunks else retrieved_chunks

        query_tokens = set(re.findall(r"[\w\u0900-\u097F]+", query.lower()))

        all_lines = []
        for c in chunks_to_use:
            for l in c.get("content", "").split("\n"):
                line_clean = l.strip()
                # Skip markdown headers, short fragments, and orphan vowel signs
                if not line_clean or line_clean.startswith("#") or len(line_clean) < 18:
                    continue
                if re.match(r"^[\u093E-\u094D]", line_clean) or re.match(r"^[•\-]\s*[\u093E-\u094D]", line_clean):
                    continue
                pt = line_clean if line_clean.startswith(("-", "•")) else f"• {line_clean}"
                if pt not in all_lines:
                    all_lines.append(pt)

        # Score lines by overlap with query keywords
        def line_relevance(line: str) -> int:
            return sum(1 for w in query_tokens if len(w) > 2 and w in line.lower())

        all_lines.sort(key=line_relevance, reverse=True)
        selected_points = all_lines[:4]

        body = "\n".join(selected_points)

        if language == "hi":
            header = "आधिकारिक स्टोर नीति के अनुसार:\n"
        elif language == "mr":
            header = "अधिकृत स्टोअर धोरणानुसार:\n"
        else:
            header = "According to our official store policy:\n"

        return f"{header}\n{body}"

    @staticmethod
    def _clean_response(text: str) -> str:
        """Removes duplicate lines, prompt echoes, and artifacts from small LLM outputs."""
        if not text:
            return text
        # Remove prompt echoes like **2-3 VAKY:** or **नियम:**
        text = re.sub(r"\*{0,2}\d+[-–]\d+\s*[A-Za-z\u0900-\u097F]+:?\*{0,2}", "", text)
        
        parts = re.split(r"([।\.\?!]+)", text)
        cleaned = []
        seen = set()
        for i in range(0, len(parts) - 1, 2):
            s = (parts[i] + parts[i+1]).strip()
            norm = re.sub(r"\s+", " ", s.lower())
            if norm and norm not in seen and len(norm) > 4:
                seen.add(norm)
                cleaned.append(s)
        if not cleaned:
            return text.strip()
        return " ".join(cleaned).strip()

    def answer_query(
        self,
        query: str,
        manual_language: Optional[str] = None,
        top_k: int = 4,
        similarity_threshold: float = 0.80,
        use_llm: bool = True
    ) -> Dict[str, Any]:
        """
        Executes end-to-end RAG pipeline.
        Returns:
        - answer: str
        - sources: List of source dictionaries
        - language: str ('en', 'hi', 'mr')
        - language_name: str
        - confidence: float
        - generation_mode: 'llm' or 'retrieval_fallback'
        - latency_sec: float
        """
        start_time = time.time()
        analysis = self.query_analyzer.process_query(query)
        
        # 1. Language Detection
        if manual_language in ("en", "hi", "mr"):
            detected_lang = manual_language
            lang_conf = 1.0
            lang_name = self.language_detector.SUPPORTED_LANGUAGES[manual_language]
        else:
            lang_res = self.language_detector.detect(query)
            detected_lang = lang_res["language"]
            lang_conf = lang_res["confidence"]
            lang_name = lang_res["language_name"]

        # Check for pure praise / gratitude feedback
        is_gratitude = (
            analysis["sentiment"]["sentiment"] == "Positive" and
            any(w in query.lower() for w in ["thank", "धन्यवाद", "शुक्रिया", "आभारी", "awesome", "great", "बढ़िया", "छान", "उत्तम", "love", "good service"]) and
            not any(w in query.lower() for w in ["how", "when", "what", "where", "can i", "कधी", "कसे", "किती", "कब", "कैसे", "कितना", "क्या", "कहाँ"])
        )
        if is_gratitude:
            latency = round(time.time() - start_time, 2)
            return {
                "answer": self.GRATITUDE_RESPONSES.get(detected_lang, self.GRATITUDE_RESPONSES["en"]),
                "sources": [],
                "language": detected_lang,
                "language_name": lang_name,
                "confidence": lang_conf,
                "generation_mode": "gratitude_feedback",
                "latency_sec": latency,
                "sentiment": analysis["sentiment"],
                "extracted_info": analysis["information"]
            }

        # 2. Semantic Retrieval from ChromaDB with language-aware filter
        filter_meta = {"language": detected_lang} if detected_lang in ("en", "hi", "mr") else None
        retrieved_chunks = self.vector_store.search(
            query=query,
            top_k=top_k,
            filter_metadata=filter_meta,
            score_threshold=similarity_threshold
        )
        # Fallback to general retrieval if language-filtered yields no chunks
        if not retrieved_chunks and filter_meta:
            retrieved_chunks = self.vector_store.search(
                query=query,
                top_k=top_k,
                score_threshold=similarity_threshold
            )

        sources_metadata = []
        for c in retrieved_chunks:
            meta = c.get("metadata", {})
            sources_metadata.append({
                "source": meta.get("source", "Document"),
                "category": meta.get("category", "General"),
                "similarity": c.get("similarity", 0.0),
                "content_preview": c.get("content", "")[:180] + ("..." if len(c.get("content", "")) > 180 else "")
            })

        # 3. Check if any relevant context was found
        if not retrieved_chunks:
            out_of_scope = self.OUT_OF_SCOPE_MESSAGES.get(detected_lang, self.OUT_OF_SCOPE_MESSAGES["en"])
            latency = round(time.time() - start_time, 2)
            return {
                "answer": out_of_scope,
                "sources": [],
                "language": detected_lang,
                "language_name": lang_name,
                "confidence": lang_conf,
                "generation_mode": "out_of_scope",
                "latency_sec": latency,
                "sentiment": analysis["sentiment"],
                "extracted_info": analysis["information"]
            }

        # 4. Hybrid Generation: LLM for English, Grounded Semantic Synthesis for Indic Languages
        generation_mode = "retrieval_fallback"
        final_answer = ""

        if use_llm and detected_lang == "en":
            # Check Ollama health for English generation
            conn_status = self.ollama_client.check_connection()
            if conn_status.get("connected") and conn_status.get("model_available"):
                context_str = self._format_context(retrieved_chunks)
                system_prompt = self.SYSTEM_PROMPTS.get("en")
                user_prompt = (
                    f"Official Store Policy Context:\n"
                    f"{context_str}\n\n"
                    f"Customer Query: {query}\n\n"
                    f"Provide an accurate, polite, grounded 2-3 sentence response in English based strictly on the policy above. "
                    f"For damaged, broken, or defective items, clearly mention reporting within 48 hours to get a full replacement or refund within 5 to 7 business days:"
                )

                llm_res = self.ollama_client.generate(
                    prompt=user_prompt,
                    system_prompt=system_prompt,
                    temperature=0.2
                )
                if llm_res.get("success") and llm_res.get("text"):
                    candidate_answer = self._clean_response(llm_res["text"].strip())
                    if len(candidate_answer) > 10:
                        final_answer = candidate_answer
                        generation_mode = "llm"

        # For Hindi, Marathi, or when LLM is disabled/fails, synthesize grounded policy points
        if not final_answer:
            final_answer = self._grounded_fallback_synthesis(query, retrieved_chunks, detected_lang)
            generation_mode = "retrieval_fallback"

        latency = round(time.time() - start_time, 2)
        return {
            "answer": final_answer,
            "sources": sources_metadata,
            "language": detected_lang,
            "language_name": lang_name,
            "confidence": lang_conf,
            "generation_mode": generation_mode,
            "latency_sec": latency,
            "sentiment": analysis["sentiment"],
            "extracted_info": analysis["information"]
        }
