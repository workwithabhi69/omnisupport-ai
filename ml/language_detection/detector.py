"""
Multilingual Language Detector for E-commerce Customer Support Chatbot.
Supports: English ('en'), Hindi ('hi'), Marathi ('mr').
Uses a hybrid approach:
1. Script classification (Latin vs Devanagari vs Other)
2. Statistical/lexical n-gram and stopword discrimination for Devanagari (Hindi vs Marathi)
3. langdetect fallback with safety thresholds
4. Ambiguous / mixed language handling
"""

import re
from typing import Dict, Any, Tuple
try:
    from langdetect import detect_langs, DetectorFactory
    DetectorFactory.seed = 42
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False


class LanguageDetector:
    # ISO-639 codes and display names
    SUPPORTED_LANGUAGES = {
        "en": "English",
        "hi": "Hindi (हिंदी)",
        "mr": "Marathi (मराठी)"
    }

    # Distinctive Marathi lexical and morphological markers
    # 'ळ' (U+0933) is a strong Marathi Devanagari marker not found in standard modern Hindi vocabulary
    MARATHI_SPECIAL_CHAR = re.compile(r"[\u0933]")  # ळ

    # High-frequency Marathi markers, postpositions, and verb forms
    MARATHI_TOKENS = {
        "आहे", "आहेत", "नाही", "नाहीत", "नाहीये", "होते", "होती", "होता", "होत्या",
        "करावे", "करावा", "करावी", "करा", "करू", "करतो", "करते", "करतात", "केले", "केली", "केला",
        "मिळेल", "मिळतील", "होईल", "होतील", "शकतो", "शकते", "शकतात", "पाहिजे",
        "मला", "माझे", "माझी", "माझा", "माझ्या", "आम्ही", "आम्हाला", "आमचे", "आमची",
        "तुम्ही", "तुम्हाला", "तुमचे", "तुमची", "तुमचा", "तुमच्या", "आपण", "आपले",
        "साठी", "वरून", "मधील", "मध्ये", "पासून", "पर्यंत", "बद्दल", "सोबत", "द्वारे",
        "काय", "कसे", "कशी", "कसा", "कधी", "कुठे", "किती", "कोण", "का",
        "परतावा", "डिलिव्हरी", "खरेदी", "विक्री", "उत्पादन", "मागणी", "पत्ता", "खाते"
    }

    # High-frequency Hindi markers, postpositions, and verb forms
    HINDI_TOKENS = {
        "है", "हैं", "नहीं", "था", "थी", "थे", "होगा", "होगी", "होंगे",
        "करें", "करें?", "करना", "करूं", "करता", "करती", "करते", "किया", "किए", "की",
        "मिलेगा", "मिलेगी", "मिलेंगे", "सकता", "सकती", "सकते", "चाहिए",
        "मुझे", "मेरा", "मेरी", "मेरे", "हम", "हमें", "हमारा", "हमारी", "हमारे",
        "आप", "आपको", "आपका", "आपकी", "आपके", "तुम", "तुम्हें", "तुम्हारा",
        "के", "लिए", "पर", "में", "से", "तक", "बारे", "साथ", "द्वारा", "की", "का", "को",
        "क्या", "कैसे", "कैसी", "कैसा", "कब", "कहाँ", "कितना", "कितनी", "कितने", "कौन", "क्यों",
        "रिफंड", "डिलीवरी", "ऑर्डर", "वापसी", "उत्पाद", "पता", "खाता"
    }

    def __init__(self):
        pass

    def _count_script_chars(self, text: str) -> Tuple[int, int, int]:
        """Counts Latin, Devanagari, and total alpha characters."""
        devanagari_count = len(re.findall(r"[\u0900-\u097F]", text))
        latin_count = len(re.findall(r"[a-zA-Z]", text))
        total_alpha = devanagari_count + latin_count
        return latin_count, devanagari_count, total_alpha

    def _discriminate_devanagari(self, text: str) -> Tuple[str, float]:
        """
        Distinguish Hindi from Marathi Devanagari text using:
        1. Unique Marathi character 'ळ'
        2. Marathi vs Hindi token matching
        3. langdetect probability blending
        """
        # 1. Check for Marathi exclusive character 'ळ'
        has_lla = bool(self.MARATHI_SPECIAL_CHAR.search(text))

        # Tokenize Devanagari words
        words = set(re.findall(r"[\u0900-\u097F]+", text))
        if not words:
            return "hi", 0.50

        mr_matches = len(words.intersection(self.MARATHI_TOKENS))
        hi_matches = len(words.intersection(self.HINDI_TOKENS))

        # Check langdetect if available
        ld_lang, ld_prob = "hi", 0.5
        if LANGDETECT_AVAILABLE:
            try:
                preds = detect_langs(text)
                for p in preds:
                    if p.lang in ("mr", "hi"):
                        ld_lang = p.lang
                        ld_prob = p.prob
                        break
            except Exception:
                pass

        # Decision scoring
        mr_score = (mr_matches * 2.0) + (3.0 if has_lla else 0.0) + (1.5 if ld_lang == "mr" else 0.0)
        hi_score = (hi_matches * 2.0) + (1.5 if ld_lang == "hi" else 0.0)

        if mr_score > hi_score:
            conf = min(0.99, 0.65 + (mr_score / (mr_score + hi_score + 1e-5)) * 0.34)
            return "mr", round(conf, 2)
        elif hi_score > mr_score:
            conf = min(0.99, 0.65 + (hi_score / (mr_score + hi_score + 1e-5)) * 0.34)
            return "hi", round(conf, 2)
        else:
            # Fallback to langdetect or default Hindi
            if ld_lang in ("mr", "hi"):
                return ld_lang, round(max(0.60, ld_prob), 2)
            return "hi", 0.60

    def detect(self, text: str) -> Dict[str, Any]:
        """
        Detects language of input text.
        Returns dict with:
        - language: 'en', 'hi', or 'mr'
        - language_name: Display string
        - confidence: float (0.0 to 1.0)
        - is_mixed: bool
        - detected_method: str explanation
        """
        if not text or not text.strip():
            return {
                "language": "en",
                "language_name": self.SUPPORTED_LANGUAGES["en"],
                "confidence": 0.0,
                "is_mixed": False,
                "detected_method": "empty_fallback"
            }

        cleaned = text.strip()
        latin_count, devanagari_count, total_alpha = self._count_script_chars(cleaned)

        if total_alpha == 0:
            return {
                "language": "en",
                "language_name": self.SUPPORTED_LANGUAGES["en"],
                "confidence": 0.50,
                "is_mixed": False,
                "detected_method": "symbols_fallback"
            }

        is_mixed = (latin_count > 0 and devanagari_count > 0)

        # Predominantly Devanagari script
        if devanagari_count >= latin_count:
            lang, conf = self._discriminate_devanagari(cleaned)
            return {
                "language": lang,
                "language_name": self.SUPPORTED_LANGUAGES[lang],
                "confidence": conf,
                "is_mixed": is_mixed,
                "detected_method": f"devanagari_discriminator (mr_tokens/hi_tokens/char_set)"
            }

        # Predominantly Latin script
        # Check if it's English or another Latin-script language
        if LANGDETECT_AVAILABLE:
            try:
                preds = detect_langs(cleaned)
                top = preds[0]
                if top.lang == "en":
                    return {
                        "language": "en",
                        "language_name": self.SUPPORTED_LANGUAGES["en"],
                        "confidence": round(top.prob, 2),
                        "is_mixed": is_mixed,
                        "detected_method": "langdetect_latin"
                    }
            except Exception:
                pass

        # Latin fallback default to English
        conf = round(latin_count / total_alpha, 2)
        return {
            "language": "en",
            "language_name": self.SUPPORTED_LANGUAGES["en"],
            "confidence": max(0.70, conf),
            "is_mixed": is_mixed,
            "detected_method": "latin_script_heuristic"
        }
