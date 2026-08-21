"""
OCR Error Correction Module

Handles common OCR mistakes and normalizes text for better extraction.
"""

import re
from difflib import SequenceMatcher
from typing import Dict, List, Tuple


class OCRCorrectionService:
    """
    Corrects common OCR mistakes and provides fuzzy matching
    for low-quality document extraction.
    """

    # Common OCR character substitutions
    CHAR_CORRECTIONS = {
        'l': ['1', 'I'],  # lowercase L confused with 1 or I
        '0': ['O', 'o'],  # zero confused with letter O
        'S': ['5'],       # S confused with 5
        '8': ['B'],       # 8 confused with B
        'r': ['n'],       # r confused with n
    }

    # Common OCR word corrections
    WORD_CORRECTIONS = {
        'irrvoce': 'invoice',
        'invoce': 'invoice',
        'invioce': 'invoice',
        'wrrowe': 'invoice',
        'invoive': 'invoice',
        'inviice': 'invoice',
        'oate': 'date',
        'dote': 'date',
        'totad': 'total',
        'totat': 'total',
        'keyooard': 'keyboard',
        'keyobard': 'keyboard',
        'mone': 'mouse',
        'mouae': 'mouse',
        'qaunity': 'quantity',
        'qty': 'quantity',
        'oty': 'quantity',
        'sokons': 'solutions',
        'techsuppry': 'techsupply',
        'suppiy': 'supply',
    }

    @staticmethod
    def correct_common_ocr_errors(text: str) -> str:
        """
        Correct common OCR mistakes in text.
        """
        # Apply word corrections
        for wrong, correct in OCRCorrectionService.WORD_CORRECTIONS.items():
            # Case-insensitive replacement with word boundaries
            pattern = r'\b' + re.escape(wrong) + r'\b'
            text = re.sub(pattern, correct, text, flags=re.IGNORECASE)

        return text

    @staticmethod
    def fuzzy_match(text: str, keyword: str, threshold: float = 0.75) -> bool:
        """
        Check if keyword approximately matches text using fuzzy matching.
        threshold: 0.0-1.0, higher means more strict matching (default 0.75 = 75% match)
        """
        text_lower = text.lower()
        keyword_lower = keyword.lower()

        # First check exact match
        if keyword_lower in text_lower:
            return True

        # Try fuzzy matching using SequenceMatcher
        ratio = SequenceMatcher(None, text_lower, keyword_lower).ratio()
        return ratio >= threshold

    @staticmethod
    def fuzzy_search_in_text(text: str, keywords: List[str], threshold: float = 0.70) -> List[str]:
        """
        Search for keywords in text with fuzzy matching.
        Returns matched keywords.
        """
        text_lower = text.lower()
        matched = []

        for keyword in keywords:
            keyword_lower = keyword.lower()

            # Exact match
            if keyword_lower in text_lower:
                matched.append(keyword)
                continue

            # Fuzzy match
            ratio = SequenceMatcher(None, text_lower, keyword_lower).ratio()
            if ratio >= threshold:
                matched.append(keyword)

        return matched

    @staticmethod
    def extract_fuzzy_value(text: str, pattern: str, fuzzy_keywords: List[str] = None) -> str:
        """
        Extract value after finding keyword (with fuzzy matching if provided).
        """
        text_lower = text.lower()

        # If fuzzy keywords provided, find them first
        if fuzzy_keywords:
            for keyword in fuzzy_keywords:
                if OCRCorrectionService.fuzzy_match(text_lower, keyword, threshold=0.70):
                    # Extract from that position onwards
                    idx = text_lower.find(keyword.lower())
                    if idx >= 0:
                        substring = text[idx:]
                        match = re.search(pattern, substring, re.IGNORECASE)
                        if match:
                            return match.group(1).strip()

        # Otherwise just use pattern
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()

        return None

    @staticmethod
    def normalize_text_for_extraction(text: str) -> str:
        """
        Normalize OCR text for better extraction:
        - Correct common OCR errors
        - Fix spacing issues
        - Normalize punctuation
        """
        # Correct OCR errors
        text = OCRCorrectionService.correct_common_ocr_errors(text)

        # Fix common OCR spacing issues
        text = re.sub(r'(\w)([=:,.])', r'\1 \2', text)  # Add space before punctuation
        text = re.sub(r'([=:,.])\s*(\w)', r'\1 \2', text)  # Normalize spacing after punctuation

        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)

        return text.strip()
