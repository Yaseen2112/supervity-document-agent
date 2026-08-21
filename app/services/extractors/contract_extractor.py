"""
Robust Contract Extractor
=========================

Purpose
-------
Extract structured contract information from normalized document text.

Supported source documents
--------------------------
- Text-based PDF
- Scanned PDF (after OCR)
- PNG
- JPG / JPEG
- OCR-generated text
- Multi-page contract text

Design goals
------------
- Robust to different contract terminology
- Robust to OCR noise
- Multiple extraction strategies
- Conservative extraction
- No LLM/API dependency
- Deterministic
- Fast
- Compatible with the existing Contract Pydantic model

Important
---------
This extractor receives TEXT, not raw PDF/image bytes.

PDF/image handling belongs to:
    document_processor.py
    text_extraction_service.py
    image_preprocessor.py
    ocr_service.py

Pipeline:

    PDF / JPG / PNG
          |
          v
    Text extraction / OCR
          |
          v
    ContractExtractor
          |
          v
    Contract Pydantic model
          |
          v
    Structured JSON
"""

import re
from typing import Optional, List, Tuple


from app.models.contract import Contract
from app.services.ocr_correction_service import OCRCorrectionService


class ContractExtractor:
    """
    Robust rule-based contract information extractor.

    The extractor intentionally uses multiple strategies instead
    of depending on one fixed document template.
    """

    # ============================================================
    # CONSTANTS
    # ============================================================

    MAX_PARTIES = 10
    MAX_OBLIGATIONS = 20

    # Common contract identifiers
    ID_LABELS = (
        r"contract\s*(?:id|number|no|#)?",
        r"agreement\s*(?:id|number|no|#)?",
        r"reference\s*(?:code|number|no|id|#)?",
        r"document\s*(?:id|number|no|#)",
        r"contract\s*reference",
        r"agreement\s*reference",
        r"ref(?:erence)?"
    )

    # ============================================================
    # TEXT NORMALIZATION
    # ============================================================

    def normalize_text(self, text: str) -> str:
        """
        Normalize text while preserving enough line structure
        for section-based extraction.

        Handles:
        - None / empty input
        - Windows line endings
        - OCR whitespace
        - repeated spaces
        - unusual Unicode spaces
        - PDF text fragmentation
        - excessive blank lines
        """

        if not text:
            return ""

        text = str(text)

        # Normalize line endings
        text = text.replace("\r\n", "\n")
        text = text.replace("\r", "\n")

        # Common OCR/PDF whitespace
        text = text.replace("\u00a0", " ")
        text = text.replace("\u200b", "")
        text = text.replace("\ufeff", "")

        # Normalize tabs
        text = text.replace("\t", " ")

        # Remove excessive spaces around lines
        lines = []

        for line in text.splitlines():

            line = re.sub(
                r"[ ]{2,}",
                " ",
                line
            )

            line = line.strip()

            if line:
                lines.append(line)

        return "\n".join(lines).strip()

    def clean_text(self, value: Optional[str]) -> str:
        """
        Clean an extracted value.
        """

        if not value:
            return ""

        value = str(value)

        # Fix line breaks occurring inside sentences
        value = re.sub(
            r"(?<=[A-Za-z0-9,;:)])\n(?=[A-Za-z0-9(])",
            " ",
            value
        )

        # Normalize whitespace
        value = re.sub(
            r"\s+",
            " ",
            value
        )

        # Remove common OCR artifacts around punctuation
        value = re.sub(
            r"\s+([,.;:])",
            r"\1",
            value
        )

        value = re.sub(
            r"([(:])\s+",
            r"\1 ",
            value
        )

        return value.strip(" \t\n\r:;-")

    def normalized_lines(self, text: str) -> List[str]:
        """
        Return cleaned non-empty lines.
        """

        normalized = self.normalize_text(text)

        return [
            self.clean_text(line)
            for line in normalized.splitlines()
            if self.clean_text(line)
        ]

    # ============================================================
    # GENERIC HELPERS
    # ============================================================

    def extract_field(
        self,
        text: str,
        patterns: List[str]
    ) -> Optional[str]:
        """
        Try multiple regex patterns.

        Returns the first meaningful match.
        """

        for pattern in patterns:

            try:

                match = re.search(
                    pattern,
                    text,
                    re.IGNORECASE | re.MULTILINE | re.DOTALL
                )

            except re.error:
                continue

            if not match:
                continue

            value = match.group(1)

            value = self.clean_text(value)

            if value:
                return value

        return None

    def unique_preserve_order(
        self,
        values: List[str]
    ) -> List[str]:

        result = []
        seen = set()

        for value in values:

            value = self.clean_text(value)

            if not value:
                continue

            key = value.lower()

            if key in seen:
                continue

            seen.add(key)
            result.append(value)

        return result

    def looks_like_label(
        self,
        value: str
    ) -> bool:

        normalized = re.sub(
            r"[^a-z ]",
            "",
            value.lower()
        ).strip()

        labels = {
            "contract",
            "agreement",
            "contract id",
            "contract number",
            "agreement number",
            "reference",
            "reference code",
            "parties",
            "participants",
            "party one",
            "party two",
            "effective date",
            "start date",
            "expiry date",
            "expiration date",
            "end date",
            "payment terms",
            "payment",
            "termination",
            "termination clause",
            "obligations",
            "key obligations",
            "responsibilities",
            "scope",
            "definitions",
            "signatures",
            "confidentiality"
        }

        return normalized in labels

    # ============================================================
    # CONTRACT ID
    # ============================================================

    def extract_contract_id(
        self,
        text: str
    ) -> Optional[str]:
        """
        Extract contract/agreement identifier.

        Supports examples such as:

        Contract ID: CTR-2026-001
        Contract Number: CN-12345
        Agreement No: AGR/2026/001
        Reference Code: REF-100
        Document ID: DOC-123
        Contract Ref: CT-100
        """

        text = self.normalize_text(text)

        patterns = [

            # Explicit labels
            r"\bContract\s*(?:ID|Number|No\.?|#)\s*[:\-]?\s*"
            r"([A-Z0-9][A-Z0-9._\/\-]{2,})",

            r"\bAgreement\s*(?:ID|Number|No\.?|#)\s*[:\-]?\s*"
            r"([A-Z0-9][A-Z0-9._\/\-]{2,})",

            r"\bReference\s*(?:Code|Number|No\.?|ID|#)\s*[:\-]?\s*"
            r"([A-Z0-9][A-Z0-9._\/\-]{2,})",

            r"\bContract\s*Reference\s*[:\-]?\s*"
            r"([A-Z0-9][A-Z0-9._\/\-]{2,})",

            r"\bAgreement\s*Reference\s*[:\-]?\s*"
            r"([A-Z0-9][A-Z0-9._\/\-]{2,})",

            r"\bDocument\s*(?:ID|Number|No\.?|#)\s*[:\-]?\s*"
            r"([A-Z0-9][A-Z0-9._\/\-]{2,})",

            r"\bRef(?:erence)?\s*[:\-]\s*"
            r"([A-Z0-9][A-Z0-9._\/\-]{2,})"
        ]

        value = self.extract_field(
            text,
            patterns
        )

        if value:
            return value

        # --------------------------------------------------------
        # OCR tolerant fallback
        # --------------------------------------------------------

        compact = re.sub(
            r"\s+",
            " ",
            text
        )

        match = re.search(
            r"\b(?:contract|agreement)"
            r"\s+(?:id|no|number)"
            r"\s*[:\-]?\s*"
            r"([A-Z0-9][A-Z0-9._\/\-]{2,})",
            compact,
            re.IGNORECASE
        )

        if match:
            return self.clean_text(
                match.group(1)
            )

        return None

    # ============================================================
    # TITLE
    # ============================================================

    def extract_title(
        self,
        text: str
    ) -> Optional[str]:
        """
        Extract a meaningful contract title.

        Strategy:
        1. Explicit title labels
        2. Common agreement names
        3. Uppercase heading
        4. Early meaningful heading
        """

        lines = self.normalized_lines(text)

        # --------------------------------------------------------
        # Explicit title labels
        # --------------------------------------------------------

        for index, line in enumerate(lines):

            match = re.match(
                r"^(?:Title|Document\s*Title|Agreement\s*Title)"
                r"\s*[:\-]\s*(.+)$",
                line,
                re.IGNORECASE
            )

            if match:

                value = self.clean_text(
                    match.group(1)
                )

                if value:
                    return value

        # --------------------------------------------------------
        # Common contract title patterns
        # --------------------------------------------------------

        title_patterns = [
            r"\b([A-Z][A-Z\s&,\-]{5,}"
            r"(?:AGREEMENT|CONTRACT|TERMS|SERVICES|"
            r"STATEMENT|LICENSE|LEASE|NDA|MEMORANDUM))\b"
        ]

        for pattern in title_patterns:

            match = re.search(
                pattern,
                text
            )

            if match:

                value = self.clean_text(
                    match.group(1)
                )

                if len(value) >= 5:
                    return value

        # --------------------------------------------------------
        # Uppercase heading
        # --------------------------------------------------------

        for line in lines[:15]:

            if len(line) < 5 or len(line) > 150:
                continue

            if ":" in line:
                continue

            # Skip identifiers
            if re.search(
                r"\b(?:ID|NUMBER|NO|DATE|REFERENCE)\b",
                line,
                re.IGNORECASE
            ):
                continue

            letters = re.sub(
                r"[^A-Za-z]",
                "",
                line
            )

            if not letters:
                continue

            uppercase_ratio = sum(
                char.isupper()
                for char in letters
            ) / len(letters)

            if uppercase_ratio >= 0.85:
                return self.clean_text(line)

        return None

    # ============================================================
    # PARTIES
    # ============================================================

    def extract_parties(
        self,
        text: str
    ) -> List[str]:
        """
        Extract contract parties from multiple common formulations.
        """

        text = self.normalize_text(text)

        parties = []

        # --------------------------------------------------------
        # Party One / Party Two
        # --------------------------------------------------------

        explicit_patterns = [
            r"\bParty\s*(?:One|1)\s*[:\-]\s*([^\n]+)",
            r"\bParty\s*(?:Two|2)\s*[:\-]\s*([^\n]+)",
            r"\bFirst\s*Party\s*[:\-]\s*([^\n]+)",
            r"\bSecond\s*Party\s*[:\-]\s*([^\n]+)",
            r"\bParty\s*A\s*[:\-]\s*([^\n]+)",
            r"\bParty\s*B\s*[:\-]\s*([^\n]+)"
        ]

        for pattern in explicit_patterns:

            matches = re.findall(
                pattern,
                text,
                re.IGNORECASE
            )

            for match in matches:

                value = self.clean_text(match)

                if value and not self.looks_like_label(value):
                    parties.append(value)

        parties = self.unique_preserve_order(
            parties
        )

        if len(parties) >= 2:
            return parties[:self.MAX_PARTIES]

        # --------------------------------------------------------
        # Participants / Parties section
        # --------------------------------------------------------

        section_patterns = [
            r"(?:Participants|Parties|Contracting\s+Parties)"
            r"\s*[:\-]?\s*(.+?)"
            r"(?=\n\s*(?:Effective|Start|Term|Scope|Payment|"
            r"Responsibilities|Obligations|Termination|"
            r"Signatures?)\b|$)"
        ]

        for pattern in section_patterns:

            match = re.search(
                pattern,
                text,
                re.IGNORECASE | re.DOTALL
            )

            if not match:
                continue

            section = match.group(1)

            # Split common separators
            candidates = re.split(
                r"\s*(?:\||;|\n|\s+and\s+)\s*",
                section,
                flags=re.IGNORECASE
            )

            for candidate in candidates:

                candidate = self.clean_text(
                    candidate
                )

                candidate = re.sub(
                    r"^(?:[-•*]|\d+[.)])\s*",
                    "",
                    candidate
                )

                if not candidate:
                    continue

                if self.looks_like_label(candidate):
                    continue

                if len(candidate) < 2:
                    continue

                parties.append(candidate)

            parties = self.unique_preserve_order(
                parties
            )

            if parties:
                return parties[:self.MAX_PARTIES]

        # --------------------------------------------------------
        # "between X and Y"
        # --------------------------------------------------------

        patterns = [

            r"\bentered\s+into\s+between\s+"
            r"(.+?)\s+and\s+(.+?)"
            r"(?:\.|\n|$)",

            r"\bagreement\s+(?:is\s+)?between\s+"
            r"(.+?)\s+and\s+(.+?)"
            r"(?:\.|\n|$)",

            r"\bcontract\s+(?:is\s+)?between\s+"
            r"(.+?)\s+and\s+(.+?)"
            r"(?:\.|\n|$)",

            r"\bby\s+and\s+between\s+"
            r"(.+?)\s+and\s+(.+?)"
            r"(?:\.|\n|$)"
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                text,
                re.IGNORECASE | re.DOTALL
            )

            if not match:
                continue

            first = self.clean_text(
                match.group(1)
            )

            second = self.clean_text(
                match.group(2)
            )

            if first and second:

                # Avoid absurdly long captures
                if len(first) <= 250 and len(second) <= 250:

                    return self.unique_preserve_order(
                        [first, second]
                    )

        # --------------------------------------------------------
        # "X and Y agree..."
        # --------------------------------------------------------

        match = re.search(
            r"\b([A-Z][A-Za-z0-9&.,'()\- ]{2,100})"
            r"\s+and\s+"
            r"([A-Z][A-Za-z0-9&.,'()\- ]{2,100})"
            r"\s+(?:agree|enter|execute|hereby)",
            text
        )

        if match:

            first = self.clean_text(
                match.group(1)
            )

            second = self.clean_text(
                match.group(2)
            )

            if first and second:
                return [
                    first,
                    second
                ]

        return []

    # ============================================================
    # DATE EXTRACTION
    # ============================================================

    def extract_date_value(
        self,
        text: str,
        label_patterns: List[str]
    ) -> Optional[str]:
        """
        Extract dates using multiple common formats.
        """

        date_pattern = (
            r"("
            r"\d{4}[-/]\d{1,2}[-/]\d{1,2}"
            r"|"
            r"\d{1,2}[-/]\d{1,2}[-/]\d{4}"
            r"|"
            r"\d{1,2}\s+[A-Za-z]{3,12}\s+\d{4}"
            r"|"
            r"[A-Za-z]{3,12}\s+\d{1,2},?\s+\d{4}"
            r"|"
            r"\d{1,2}(?:st|nd|rd|th)?\s+"
            r"[A-Za-z]{3,12},?\s+\d{4}"
            r")"
        )

        for label in label_patterns:

            patterns = [

                rf"\b{label}\b\s*[:\-]?\s*"
                rf"{date_pattern}",

                rf"\b{label}\b\s+"
                rf"{date_pattern}"
            ]

            value = self.extract_field(
                text,
                patterns
            )

            if value:
                return self.clean_text(value)

        return None

    def extract_effective_date(
        self,
        text: str
    ) -> Optional[str]:

        text = self.normalize_text(text)

        value = self.extract_date_value(
            text,
            [
                r"effective\s+date",
                r"commencement\s+date",
                r"start\s+date",
                r"commencement",
                r"effective\s+from",
                r"starts?\s+on",
                r"becomes?\s+effective",
                r"becomes?\s+active"
            ]
        )

        if value:
            return value

        # "This agreement shall become effective on January 1, 2026"
        match = re.search(
            r"\b(?:become|becomes|shall\s+become)"
            r"\s+(?:effective|active)"
            r"\s+(?:on|from)\s+"
            r"([A-Za-z0-9,\-/ ]{6,40})",
            text,
            re.IGNORECASE
        )

        if match:
            return self.clean_text(
                match.group(1)
            ).rstrip(".")

        return None

    def extract_expiry_date(
        self,
        text: str
    ) -> Optional[str]:

        text = self.normalize_text(text)

        value = self.extract_date_value(
            text,
            [
                r"expiry\s+date",
                r"expiration\s+date",
                r"end\s+date",
                r"termination\s+date",
                r"valid\s+until",
                r"valid\s+through",
                r"expires?\s+on",
                r"concludes?\s+on",
                r"ends?\s+on"
            ]
        )

        if value:
            return value

        # "The agreement shall remain in force until December 31, 2026"
        match = re.search(
            r"\b(?:remain|continues?|continue)"
            r".{0,80}?\buntil\s+"
            r"([A-Za-z0-9,\-/ ]{6,40})",
            text,
            re.IGNORECASE
        )

        if match:
            value = self.clean_text(
                match.group(1)
            )

            return value.rstrip(".")

        return None

    # ============================================================
    # PAYMENT TERMS
    # ============================================================

    def extract_payment_terms(
        self,
        text: str
    ) -> Optional[str]:
        """
        Extract payment terms from a broad range of contracts.
        """

        text = self.normalize_text(text)

        patterns = [

            # Explicit labels
            r"\bPayment\s*Terms?\s*[:\-]\s*(.+?)"
            r"(?=\n\s*[A-Z][A-Za-z ]{2,40}\s*[:\-]|$)",

            r"\bPayment\s+Conditions?\s*[:\-]\s*(.+?)"
            r"(?=\n\s*[A-Z][A-Za-z ]{2,40}\s*[:\-]|$)",

            r"\bSettlement\s+(?:Condition|Terms?)\s*[:\-]\s*(.+?)"
            r"(?=\n\s*[A-Z][A-Za-z ]{2,40}\s*[:\-]|$)",

            r"\bCommercial\s+Terms?\s*[:\-]\s*(.+?)"
            r"(?=\n\s*[A-Z][A-Za-z ]{2,40}\s*[:\-]|$)"
        ]

        value = self.extract_field(
            text,
            patterns
        )

        if value:
            return value

        # --------------------------------------------------------
        # Semantic-style payment sentences
        # --------------------------------------------------------

        sentence_patterns = [

            r"((?:payment|payments)\s+"
            r"(?:shall|will|must|are\s+due|is\s+due)"
            r"[^.\n]{5,250}\.)",

            r"((?:invoices?|fees?|amounts?)\s+"
            r"(?:shall|will|must)\s+be\s+paid"
            r"[^.\n]{5,250}\.)",

            r"((?:net\s+\d+\s+days?)"
            r"[^.\n]{0,150})",

            r"((?:within\s+\d+\s+days?)"
            r"[^.\n]{0,150}"
            r"(?:invoice|payment|receipt)[^.\n]*)"
        ]

        for pattern in sentence_patterns:

            match = re.search(
                pattern,
                text,
                re.IGNORECASE
            )

            if match:

                value = self.clean_text(
                    match.group(1)
                )

                if value:
                    return value

        return None

    # ============================================================
    # OBLIGATIONS
    # ============================================================

    def extract_key_obligations(
        self,
        text: str
    ) -> List[str]:
        """
        Extract key contractual obligations.

        Sources:
        - Obligations sections
        - Responsibilities sections
        - Duties sections
        - Deliverables sections
        - Numbered lists
        - Bullet lists
        - shall / must / will statements
        """

        text = self.normalize_text(text)

        obligations = []

        # --------------------------------------------------------
        # Section-based extraction
        # --------------------------------------------------------

        section_patterns = [

            r"(?:Key\s+Obligations|Obligations)"
            r"\s*:?\s*(.+?)"
            r"(?=\n\s*(?:Termination|"
            r"Termination\s+Clause|Exit\s+Provision|"
            r"Payment|Confidentiality|Signatures?)"
            r"\s*:?\s*|$)",

            r"(?:Responsibilities|"
            r"Roles\s+and\s+Responsibilities|"
            r"Duties)"
            r"\s*:?\s*(.+?)"
            r"(?=\n\s*(?:Termination|"
            r"Payment|Confidentiality|"
            r"Signatures?)\s*:?\s*|$)",

            r"(?:Deliverables|"
            r"Service\s+Obligations|"
            r"Performance)"
            r"\s*:?\s*(.+?)"
            r"(?=\n\s*(?:Termination|"
            r"Payment|Confidentiality|"
            r"Signatures?)\s*:?\s*|$)"
        ]

        for pattern in section_patterns:

            match = re.search(
                pattern,
                text,
                re.IGNORECASE | re.DOTALL
            )

            if not match:
                continue

            section = match.group(1)

            # Split numbered / bullet lists
            raw_items = re.split(
                r"\n+|(?<=\.)\s+(?=[A-Z])|"
                r"(?<!\w)(?:[-•*]|\d+[.)])\s+",
                section
            )

            for item in raw_items:

                item = self.clean_text(item)

                if not item:
                    continue

                item = re.sub(
                    r"^(?:[-•*]|\d+[.)])\s*",
                    "",
                    item
                )

                # Remove accidental labels
                if self.looks_like_label(item):
                    continue

                if len(item) < 10:
                    continue

                obligations.append(item)

        # --------------------------------------------------------
        # Contractual obligation sentences
        # --------------------------------------------------------

        sentence_patterns = [

            r"([^.\n]{2,250}\bshall\b[^.\n]{2,300}\.)",

            r"([^.\n]{2,250}\bmust\b[^.\n]{2,300}\.)",

            r"([^.\n]{2,250}\bwill\b[^.\n]{2,300}\.)",

            r"([^.\n]{2,250}\bis\s+required\s+to\b"
            r"[^.\n]{2,300}\.)",

            r"([^.\n]{2,250}\bagrees?\s+to\b"
            r"[^.\n]{2,300}\.)"
        ]

        for pattern in sentence_patterns:

            matches = re.findall(
                pattern,
                text,
                re.IGNORECASE
            )

            for match in matches:

                value = self.clean_text(
                    match
                )

                if len(value) >= 15:
                    obligations.append(value)

        # --------------------------------------------------------
        # Deduplicate
        # --------------------------------------------------------

        obligations = self.unique_preserve_order(
            obligations
        )

        # --------------------------------------------------------
        # Remove obvious non-obligations
        # --------------------------------------------------------

        filtered = []

        excluded_prefixes = (
            "this agreement",
            "agreement date",
            "effective date",
            "termination date",
            "payment terms",
            "reference code"
        )

        for obligation in obligations:

            lowered = obligation.lower()

            if any(
                lowered.startswith(prefix)
                for prefix in excluded_prefixes
            ):
                continue

            filtered.append(
                obligation
            )

        return filtered[:self.MAX_OBLIGATIONS]

    # ============================================================
    # TERMINATION CLAUSE
    # ============================================================

    def extract_termination_clause(
        self,
        text: str
    ) -> Optional[str]:
        """
        Extract termination / cancellation / exit provisions.
        """

        text = self.normalize_text(text)

        # --------------------------------------------------------
        # Explicit section
        # --------------------------------------------------------

        section_patterns = [

            r"(?:Termination\s+Clause|Termination)"
            r"\s*:?\s*(.+?)"
            r"(?=\n\s*(?:Responsibilities|"
            r"Key\s+Obligations|Obligations|"
            r"Payment|Confidentiality|"
            r"Signatures?)\s*:?\s*|$)",

            r"(?:Exit\s+Provision|Exit\s+Clause)"
            r"\s*:?\s*(.+?)"
            r"(?=\n\s*[A-Z][A-Za-z ]{2,40}\s*:|$)",

            r"(?:Cancellation|"
            r"Discontinuation|"
            r"Termination\s+Rights?)"
            r"\s*:?\s*(.+?)"
            r"(?=\n\s*[A-Z][A-Za-z ]{2,40}\s*:|$)"
        ]

        for pattern in section_patterns:

            value = self.extract_field(
                text,
                [pattern]
            )

            if value:
                return self.clean_text(value)

        # --------------------------------------------------------
        # Sentence-based fallback
        # --------------------------------------------------------

        sentence_patterns = [

            r"((?:Either|Any)\s+party\s+"
            r"[^.\n]{0,150}\bterminate\b"
            r"[^.\n]{0,300}\.)",

            r"((?:either|any)\s+participant\s+"
            r"[^.\n]{0,150}\b(?:terminate|discontinue|cancel)\b"
            r"[^.\n]{0,300}\.)",

            r"((?:this\s+agreement|contract)"
            r"[^.\n]{0,100}\bmay\s+be\s+terminated\b"
            r"[^.\n]{0,300}\.)",

            r"((?:the\s+agreement|contract)"
            r"[^.\n]{0,100}\bmay\s+be\s+cancelled\b"
            r"[^.\n]{0,300}\.)",

            r"((?:termination|cancellation)"
            r"[^.\n]{0,100}"
            r"(?:notice|days?|written)"
            r"[^.\n]{0,300}\.)"
        ]

        for pattern in sentence_patterns:

            match = re.search(
                pattern,
                text,
                re.IGNORECASE
            )

            if match:

                value = self.clean_text(
                    match.group(1)
                )

                if value:
                    return value

        return None

    # ============================================================
    # FALLBACK SECTION EXTRACTOR
    # ============================================================

    def extract_section(
        self,
        text: str,
        headings: List[str],
        stop_headings: List[str]
    ) -> Optional[str]:
        """
        Generic section extraction helper.

        Useful for contracts using unexpected but recognizable
        headings.
        """

        if not text:
            return None

        heading_pattern = "|".join(
            re.escape(item)
            for item in headings
        )

        stop_pattern = "|".join(
            re.escape(item)
            for item in stop_headings
        )

        pattern = (
            rf"(?:{heading_pattern})"
            rf"\s*:?\s*(.+?)"
            rf"(?=\n\s*(?:{stop_pattern})"
            rf"\s*:?\s*|$)"
        )

        match = re.search(
            pattern,
            text,
            re.IGNORECASE | re.DOTALL
        )

        if not match:
            return None

        return self.clean_text(
            match.group(1)
        )

    # ============================================================
    # MAIN EXTRACTION
    # ============================================================

    def extract(
        self,
        text: str
    ) -> Contract:
        """
        Main contract extraction pipeline.

        Input:
            Extracted PDF/OCR text

        Output:
            Contract Pydantic object
        """

        # --------------------------------------------------------
        # Normalize input once
        # --------------------------------------------------------

        normalized_text = self.normalize_text(
            text
        )

        # --------------------------------------------------------
        # Contract ID
        # --------------------------------------------------------

        contract_id = self.extract_contract_id(
            normalized_text
        )

        # --------------------------------------------------------
        # Title
        # --------------------------------------------------------

        title = self.extract_title(
            normalized_text
        )

        # --------------------------------------------------------
        # Parties
        # --------------------------------------------------------

        parties = self.extract_parties(
            normalized_text
        )

        # --------------------------------------------------------
        # Effective date
        # --------------------------------------------------------

        effective_date = (
            self.extract_effective_date(
                normalized_text
            )
        )

        # --------------------------------------------------------
        # Expiry date
        # --------------------------------------------------------

        expiry_date = (
            self.extract_expiry_date(
                normalized_text
            )
        )

        # --------------------------------------------------------
        # Payment terms
        # --------------------------------------------------------

        payment_terms = (
            self.extract_payment_terms(
                normalized_text
            )
        )

        # --------------------------------------------------------
        # Obligations
        # --------------------------------------------------------

        key_obligations = (
            self.extract_key_obligations(
                normalized_text
            )
        )

        # --------------------------------------------------------
        # Termination
        # --------------------------------------------------------

        termination_clause = (
            self.extract_termination_clause(
                normalized_text
            )
        )

        # --------------------------------------------------------
        # Return validated Pydantic object
        # --------------------------------------------------------

        return Contract(
            contract_id=contract_id,
            title=title,
            parties=parties,
            effective_date=effective_date,
            expiry_date=expiry_date,
            payment_terms=payment_terms,
            key_obligations=key_obligations,
            termination_clause=termination_clause
        )