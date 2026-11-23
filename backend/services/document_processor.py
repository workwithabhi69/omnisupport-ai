"""
Document Processing Service for Knowledge Base Ingestion.
Supports: PDF, DOCX, TXT.
Implements: Text extraction, text cleaning, language detection, category categorization, and sliding-window chunking.
"""

import os
import re
from typing import List, Dict, Any, Optional
from ml.language_detection.detector import LanguageDetector


class DocumentProcessor:
    def __init__(self, chunk_size: int = 400, chunk_overlap: int = 60):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.lang_detector = LanguageDetector()

    def clean_text(self, text: str) -> str:
        """Cleans and normalizes extracted text preserving Devanagari and Latin."""
        if not text:
            return ""
        # Replace multiple spaces, tabs, and newlines
        text = re.sub(r"[\r\f\v]+", "\n", text)
        text = re.sub(r"\n\s*\n+", "\n\n", text)
        text = re.sub(r"[ \t]+", " ", text)
        return text.strip()

    def extract_from_txt(self, file_path_or_bytes: Any) -> str:
        """Extracts text from a TXT file path or bytes."""
        if isinstance(file_path_or_bytes, str):
            with open(file_path_or_bytes, "r", encoding="utf-8", errors="replace") as f:
                return f.read()
        elif hasattr(file_path_or_bytes, "read"):
            content = file_path_or_bytes.read()
            if isinstance(content, bytes):
                return content.decode("utf-8", errors="replace")
            return content
        elif isinstance(file_path_or_bytes, bytes):
            return file_path_or_bytes.decode("utf-8", errors="replace")
        return ""

    def extract_from_pdf(self, file_path_or_bytes: Any) -> str:
        """Extracts text from PDF using PyPDF or PyMuPDF."""
        text_parts = []
        try:
            # Try PyMuPDF (fitz)
            import fitz
            if isinstance(file_path_or_bytes, (str, bytes)):
                doc = fitz.open(file_path_or_bytes) if isinstance(file_path_or_bytes, str) else fitz.open(stream=file_path_or_bytes, filetype="pdf")
            else:
                doc = fitz.open(stream=file_path_or_bytes.read(), filetype="pdf")
            for page in doc:
                text_parts.append(page.get_text())
            doc.close()
        except Exception:
            # Fallback to PyPDF
            try:
                from pypdf import PdfReader
                reader = PdfReader(file_path_or_bytes)
                for page in reader.pages:
                    txt = page.extract_text()
                    if txt:
                        text_parts.append(txt)
            except Exception as e:
                text_parts.append(f"Error extracting PDF: {str(e)}")

        return "\n".join(text_parts)

    def extract_from_docx(self, file_path_or_bytes: Any) -> str:
        """Extracts text from DOCX using python-docx."""
        try:
            import docx
            import io
            if isinstance(file_path_or_bytes, bytes):
                file_obj = io.BytesIO(file_path_or_bytes)
                doc = docx.Document(file_obj)
            elif hasattr(file_path_or_bytes, "read"):
                doc = docx.Document(file_path_or_bytes)
            else:
                doc = docx.Document(file_path_or_bytes)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            return "\n\n".join(paragraphs)
        except Exception as e:
            return f"Error extracting DOCX: {str(e)}"

    def extract_text(self, filename: str, file_content_or_path: Any) -> str:
        """Dispatches extraction based on file extension."""
        ext = os.path.splitext(filename)[1].lower()
        if ext == ".txt":
            raw = self.extract_from_txt(file_content_or_path)
        elif ext == ".pdf":
            raw = self.extract_from_pdf(file_content_or_path)
        elif ext in (".docx", ".doc"):
            raw = self.extract_from_docx(file_content_or_path)
        else:
            raw = self.extract_from_txt(file_content_or_path)
        return self.clean_text(raw)

    def chunk_text(self, text: str) -> List[str]:
        """
        Splits text into chunks preserving line, bullet point, and sentence boundaries.
        Never cuts words or Devanagari vowel signs in half.
        """
        if not text:
            return []

        # Split into distinct non-empty lines
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        chunks = []
        current_lines = []
        current_length = 0

        for line in lines:
            line_len = len(line) + 1
            if current_length + line_len <= self.chunk_size or not current_lines:
                current_lines.append(line)
                current_length += line_len
            else:
                chunks.append("\n".join(current_lines))
                # Add overlap of previous short bullet if appropriate
                overlap = current_lines[-1] if len(current_lines) > 1 and len(current_lines[-1]) < 120 else ""
                current_lines = [overlap, line] if overlap else [line]
                current_length = sum(len(l) + 1 for l in current_lines)

        if current_lines:
            chunks.append("\n".join(current_lines))

        return [c for c in chunks if len(c.strip()) > 15]

    def infer_category(self, filename: str, text: str) -> str:
        """Infers e-commerce policy category from filename and content."""
        fn_lower = filename.lower()
        combined = f"{fn_lower} {text[:300].lower()}"

        if any(w in fn_lower for w in ["return", "refund", "वापसी", "परतावा", "परत"]):
            return "Return & Refund Policies"
        elif any(w in fn_lower for w in ["ship", "delivery", "डिलीवरी", "डिलिव्हरी"]):
            return "Shipping & Delivery"
        elif any(w in fn_lower for w in ["payment", "cancellation", "पेमेंट", "रद्द"]):
            return "Payment & Cancellation"
        elif any(w in fn_lower for w in ["account", "product", "खाता", "खाते", "उत्पाद"]):
            return "Account & Product Support"

        if any(w in combined for w in ["refund", "रिफंड", "परतावा", "return", "रिटर्न", "वापसी", "परत"]):
            return "Return & Refund Policies"
        elif any(w in combined for w in ["ship", "delivery", "डिलीवरी", "डिलिव्हरी", "कूरियर", "courier", "dispatch"]):
            return "Shipping & Delivery"
        elif any(w in combined for w in ["cancel", "रद्द", "कॅन्सल"]):
            return "Order Cancellation"
        elif any(w in combined for w in ["pay", "upi", "card", "पेमेंट", "पैसे", "cod", "cash"]):
            return "Payment Methods"
        elif any(w in combined for w in ["account", "login", "password", "खाता", "खाते", "पासवर्ड"]):
            return "Account Support"
        elif any(w in combined for w in ["product", "warranty", "उत्पाद", "उत्पादन", "वॉरंटी"]):
            return "Product Information"
        return "General Policy"

    def process_file(
        self,
        filename: str,
        file_content_or_path: Any,
        override_language: Optional[str] = None,
        override_category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Full ingestion pipeline:
        Extract -> Clean -> Detect Language -> Infer Category -> Chunk -> Create Metadatas
        """
        raw_text = self.extract_text(filename, file_content_or_path)
        if not raw_text:
            return {
                "filename": filename,
                "error": "Document contains no extractable text",
                "chunks": [],
                "metadatas": []
            }

        # Language detection
        if override_language:
            lang = override_language
        else:
            lang_res = self.lang_detector.detect(raw_text[:500])
            lang = lang_res["language"]

        # Category inference
        cat = override_category or self.infer_category(filename, raw_text)

        chunks = self.chunk_text(raw_text)
        metadatas = []
        for i, chunk in enumerate(chunks):
            metadatas.append({
                "source": filename,
                "language": lang,
                "category": cat,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "char_length": len(chunk)
            })

        return {
            "filename": filename,
            "raw_text_length": len(raw_text),
            "language": lang,
            "category": cat,
            "chunk_count": len(chunks),
            "chunks": chunks,
            "metadatas": metadatas
        }
