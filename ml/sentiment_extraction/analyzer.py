"""
Sentiment Analysis and Information/Entity Extraction Module for Multilingual Customer Queries.
Covers Assessment Rubric Criterion 2 (CO2 - 8 Marks):
- Multilingual Sentiment Analysis (Positive, Neutral, Negative/Frustrated/Urgent)
- Information Extraction: Customer Intent, Key Entities (Money amounts, Timelines, Product/Service categories)
"""

import re
from typing import Dict, Any, List


class CustomerQueryAnalyzer:
    # Multilingual Lexicons for Sentiment
    POSITIVE_WORDS = {
        # English
        "good", "great", "excellent", "fast", "thanks", "thank", "helpful", "happy", "love", "awesome",
        "best", "satisfied", "pleased", "perfect",
        # Hindi
        "अच्छा", "बढ़िया", "धन्यवाद", "शुक्रिया", "उत्कृष्ट", "खुश", "मददगार", "संतुष्ट", "सही",
        # Marathi
        "छान", "चांगले", "उत्तम", "धन्यवाद", "आभारी", "आनंदी", "मदत", "समाधानी", "योग्य"
    }

    NEGATIVE_WORDS = {
        # English
        "bad", "terrible", "worst", "slow", "broken", "damaged", "delay", "delayed", "late", "fraud",
        "cheat", "poor", "issue", "problem", "angry", "complaint", "fail", "failed", "stolen", "missing", "wrong",
        # Hindi
        "खराब", "बुरा", "टूटा", "क्षतिग्रस्त", "देरी", "विलंब", "धोखा", "शिकायत", "समस्या", "परेशानी", "गलत", "गायब",
        # Marathi
        "खराब", "वाईट", "तुटलेले", "उशीर", "विलंब", "तक्रार", "अडचण", "त्रास", "समस्या", "चुकीचे", "गहाळ"
    }

    URGENT_WORDS = {
        "urgent", "immediately", "asap", "emergency", "help", "fast", "quick", "hurry",
        "जल्दी", "तुरंत", "तत्काल", "शीघ्र", "मदद",
        "तात्काळ", "लवकर", "तातडीने"
    }

    # Intent Classification Patterns
    INTENT_PATTERNS = [
        ("Refund Status", [r"\brefund\b", r"\bmoney back\b", r"रिफंड", r"परतावा", r"पैसे वापस", r"पैसे", r"पैसा"]),
        ("Return Request", [r"\breturn\b", r"\breplace\b", r"\bexchange\b", r"वापसी", r"वापस", r"(?:^|\s)परत(?:$|\s)", r"बदलून", r"रिटर्न", r"रिप्लेस"]),
        ("Delivery Inquiry", [r"\bdelivery\b", r"\bshipping\b", r"\bdispatch\b", r"\btrack\b", r"\bstatus\b", r"डिलीवरी", r"डिलिव्हरी", r"ट्रैक", r"ट्रॅक", r"पोहोचेल", r"कधी येईल", r"कब आएगा"]),
        ("Order Cancellation", [r"\bcancel\b", r"\bcancellation\b", r"रद्द", r"कॅन्सल", r"कैंसिल"]),
        ("Payment & Billing", [r"\bpayment\b", r"\bcharge\b", r"\bfee\b", r"\bcost\b", r"\bprice\b", r"\bupi\b", r"\bcard\b", r"\bcod\b", r"\bemi\b", r"भुगतान", r"पेमेंट", r"शुल्क", r"किंमत"]),
        ("Account Support", [r"\bpassword\b", r"\baccount\b", r"\blogin\b", r"\bsign in\b", r"पासवर्ड", r"खाता", r"खाते", r"लॉगिन"])
    ]

    def __init__(self):
        pass

    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyzes customer query sentiment across English, Hindi, and Marathi.
        Returns sentiment label, polarity score (-1.0 to +1.0), and urgency flag.
        """
        if not text:
            return {"sentiment": "Neutral", "score": 0.0, "is_urgent": False, "badge": "😐 Neutral"}

        # Tokenize using Unicode Devanagari (\u0900-\u097F) and alphanumeric characters
        tokens = set(re.findall(r"[\w\u0900-\u097F]+", text.lower()))
        
        pos_hits = len(tokens.intersection(self.POSITIVE_WORDS))
        neg_hits = len(tokens.intersection(self.NEGATIVE_WORDS))
        urgent_hits = len(tokens.intersection(self.URGENT_WORDS))

        is_urgent = (urgent_hits > 0) or (neg_hits >= 2)

        if neg_hits > 0 and is_urgent:
            sentiment = "Negative"
            badge = "⚠️ Urgent / Frustrated"
            polarity = max(-1.0, -0.4 - 0.3 * neg_hits)
        elif neg_hits > pos_hits:
            sentiment = "Negative"
            badge = "🙁 Negative"
            polarity = max(-1.0, -0.3 - 0.25 * neg_hits)
        elif pos_hits > neg_hits:
            sentiment = "Positive"
            badge = "😊 Positive"
            polarity = min(1.0, 0.3 + 0.25 * pos_hits)
        elif is_urgent:
            sentiment = "Neutral"
            badge = "⚡ Priority"
            polarity = -0.1
        else:
            sentiment = "Neutral"
            badge = "😐 Neutral"
            polarity = 0.0

        return {
            "sentiment": sentiment,
            "polarity": round(polarity, 2),
            "is_urgent": is_urgent,
            "badge": badge,
            "positive_matches": pos_hits,
            "negative_matches": neg_hits
        }

    def extract_information(self, text: str) -> Dict[str, Any]:
        """
        Extracts key entities, customer intent, monetary amounts, and timelines from query.
        """
        text_lower = text.lower()

        # 1. Intent Extraction
        detected_intent = "General Inquiry"
        for intent, patterns in self.INTENT_PATTERNS:
            if any(re.search(pat, text_lower) for pat in patterns):
                detected_intent = intent
                break

        # 2. Monetary Entity Extraction (e.g. ₹499, 499 rupees, 99 rs)
        money_entities = re.findall(r"(?:₹|\brs\.?|\brupees?\b)\s*(\d+)", text_lower)
        if not money_entities:
            money_entities = re.findall(r"(\d+)\s*(?:₹|\brs\.?|\brupees?\b)", text_lower)

        # 3. Timeline Entity Extraction (e.g. 7 days, 24 hours, 3-5 days, 48 तास, 7 दिवस)
        time_entities = re.findall(
            r"(\d+(?:\s*(?:to|-)\s*\d+)?)\s*(?:days?|hours?|weeks?|कार्य दिवस|दिन|दिवस|घंटे|तास)",
            text_lower
        )

        # 4. Order Reference Extraction (e.g. #12345, ORD-8921)
        order_entities = re.findall(r"(?:order|ord|id|#)\s*#?([0-9]{3,8})", text_lower)

        return {
            "intent": detected_intent,
            "extracted_currency_amounts": [f"₹{m}" for m in money_entities],
            "extracted_timelines": time_entities,
            "extracted_order_ids": [f"#{oid}" for oid in order_entities],
            "query_length_chars": len(text),
            "query_token_count": len(text.split())
        }

    def process_query(self, text: str) -> Dict[str, Any]:
        """Combines sentiment analysis and information extraction."""
        sentiment_info = self.analyze_sentiment(text)
        extracted_info = self.extract_information(text)
        return {
            "sentiment": sentiment_info,
            "information": extracted_info
        }
