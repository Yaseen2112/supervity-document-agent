import re
from typing import Optional, List, Tuple, Dict, Any

from app.models.invoice import (
    Invoice,
    Vendor,
    InvoiceLineItem
)

from app.services.ocr_correction_service import OCRCorrectionService


class InvoiceExtractor:
    """
    Robust rule-based invoice extractor.

    Design goals:
    - Backward compatible with the existing Invoice schema.
    - Handle multiple invoice layouts and terminology.
    - Work with both embedded PDF text and OCR text.
    - Avoid hallucinating values.
    - Prefer validated candidates over blindly matched values.
    - Support common Indian GST invoice terminology.
    """

    # ============================================================
    # CONSTANTS
    # ============================================================

    DATE_PATTERN = (
        r"(?:"
        r"\d{4}[-/]\d{1,2}[-/]\d{1,2}"
        r"|"
        r"\d{1,2}[-/]\d{1,2}[-/]\d{2,4}"
        r"|"
        r"\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4}"
        r"|"
        r"[A-Za-z]{3,9}\s+\d{1,2},?\s+\d{4}"
        r")"
    )

    NUMBER_PATTERN = (
        r"[-+]?(?:\d{1,3}(?:,\d{2,3})+|\d+)"
        r"(?:\.\d+)?"
    )

    CURRENCY_CODES = {
        "INR",
        "USD",
        "EUR",
        "GBP",
        "AUD",
        "CAD",
        "SGD",
        "AED",
        "JPY",
        "CNY",
        "CHF",
        "NZD",
        "SAR",
        "QAR",
        "MYR",
        "THB"
    }

    CURRENCY_SYMBOLS = {
        "₹": "INR",
        "Rs": "INR",
        "Rs.": "INR",
        "INR": "INR",
        "$": "USD",
        "€": "EUR",
        "£": "GBP",
        "¥": "JPY"
    }

    STOP_WORDS = {
        "subtotal",
        "sub total",
        "taxable amount",
        "tax",
        "gst",
        "cgst",
        "sgst",
        "igst",
        "vat",
        "discount",
        "shipping",
        "freight",
        "delivery charges",
        "total",
        "total amount",
        "grand total",
        "amount payable",
        "balance due",
        "amount due",
        "round off",
        "rounding",
        "terms",
        "notes",
        "remarks",
        "payment terms"
    }

    # ============================================================
    # TEXT NORMALIZATION
    # ============================================================

    def normalize_text(self, text: str) -> str:
        """
        Normalize OCR/PDF text without destroying useful structure.
        """

        if not text:
            return ""

        text = text.replace("\r\n", "\n")
        text = text.replace("\r", "\n")

        # Common OCR substitutions.
        text = text.replace("\u00a0", " ")
        text = text.replace("—", "-")
        text = text.replace("–", "-")

        # Keep line structure but collapse excessive spaces.
        lines = []

        for line in text.splitlines():

            line = line.strip()

            if not line:
                continue

            line = re.sub(r"[ \t]+", " ", line)

            lines.append(line)

        return "\n".join(lines)

    def get_lines(self, text: str) -> List[str]:
        """
        Return cleaned non-empty lines.
        """

        normalized = self.normalize_text(text)

        return [
            line.strip()
            for line in normalized.splitlines()
            if line.strip()
        ]

    def normalize_label(self, value: str) -> str:
        """
        Normalize a label for comparison.
        """

        value = value.lower().strip()

        value = value.replace(":", " ")
        value = value.replace("#", " number ")
        value = value.replace(".", " ")

        value = re.sub(r"[^a-z0-9]+", " ", value)

        value = re.sub(r"\s+", " ", value)

        return value.strip()

    # ============================================================
    # COMMON HELPERS
    # ============================================================

    def extract_field(
        self,
        text: str,
        patterns: List[str]
    ) -> Optional[str]:
        """
        Try multiple regex patterns and return the first
        non-empty captured value.
        """

        if not text:
            return None

        for pattern in patterns:

            try:
                match = re.search(
                    pattern,
                    text,
                    re.IGNORECASE | re.MULTILINE
                )

            except re.error:
                continue

            if match:

                try:
                    value = match.group(1).strip()
                except IndexError:
                    continue

                if value:
                    return value

        return None

    def extract_all_candidates(
        self,
        text: str,
        patterns: List[str]
    ) -> List[str]:
        """
        Extract all possible candidates from multiple patterns.
        """

        candidates = []

        for pattern in patterns:

            try:
                matches = re.findall(
                    pattern,
                    text,
                    re.IGNORECASE | re.MULTILINE
                )
            except re.error:
                continue

            if isinstance(matches, str):
                matches = [matches]

            for value in matches:

                if isinstance(value, tuple):
                    value = value[0]

                value = str(value).strip()

                if value:
                    candidates.append(value)

        return self.unique_values(candidates)

    def unique_values(
        self,
        values: List[str]
    ) -> List[str]:
        """
        Remove duplicates while preserving order.
        """

        result = []
        seen = set()

        for value in values:

            key = value.lower().strip()

            if key not in seen:

                seen.add(key)
                result.append(value)

        return result

    def clean_value(
        self,
        value: Optional[str]
    ) -> Optional[str]:
        """
        Clean extracted textual values.
        """

        if not value:
            return None

        value = value.strip()

        value = re.sub(
            r"\s+",
            " ",
            value
        )

        value = value.strip(" :|-")

        return value or None

    # ============================================================
    # NUMBER / AMOUNT HELPERS
    # ============================================================

    def parse_amount(
        self,
        value: Optional[str]
    ) -> Optional[float]:
        """
        Parse common monetary formats.

        Supports examples:
        1000
        1,000
        1,000.50
        1.000,50
        ₹1,000
        INR 1,000.00
        """

        if value is None:
            return None

        value = str(value).strip()

        if not value:
            return None

        negative = (
            value.startswith("(")
            and value.endswith(")")
        )

        cleaned = value

        cleaned = re.sub(
            r"(INR|USD|EUR|GBP|AUD|CAD|SGD|AED|JPY|CNY)",
            "",
            cleaned,
            flags=re.IGNORECASE
        )

        cleaned = re.sub(
            r"[₹$€£¥]",
            "",
            cleaned
        )

        cleaned = cleaned.replace(" ", "")
        cleaned = cleaned.replace("(", "")
        cleaned = cleaned.replace(")", "")

        # Handle European style 1.234,56.
        if (
            "," in cleaned
            and "." in cleaned
            and cleaned.rfind(",")
            > cleaned.rfind(".")
        ):
            cleaned = cleaned.replace(".", "")
            cleaned = cleaned.replace(",", ".")

        else:
            cleaned = cleaned.replace(",", "")

        cleaned = re.sub(
            r"[^0-9.\-+]",
            "",
            cleaned
        )

        if cleaned.count(".") > 1:
            parts = cleaned.split(".")
            cleaned = (
                "".join(parts[:-1])
                + "."
                + parts[-1]
            )

        try:

            number = float(cleaned)

            if negative:
                number = -abs(number)

            return number

        except (ValueError, TypeError):
            return None

    def extract_amount(
        self,
        text: str,
        patterns: List[str]
    ) -> Optional[float]:
        """
        Extract the first valid numeric amount.
        """

        values = self.extract_all_candidates(
            text,
            patterns
        )

        for value in values:

            amount = self.parse_amount(value)

            if amount is not None:
                return amount

        return None

    def is_numeric_amount(
        self,
        value: str
    ) -> bool:
        """
        Check whether a string represents a numeric value.
        """

        if not value:
            return False

        return (
            self.parse_amount(value)
            is not None
        )

    def is_positive_number(
        self,
        value: str
    ) -> bool:
        """
        Check for a positive numeric value.
        """

        number = self.parse_amount(value)

        return (
            number is not None
            and number > 0
        )

    # ============================================================
    # INVOICE NUMBER
    # ============================================================

    def extract_invoice_number(
        self,
        text: str
    ) -> Optional[str]:

        text = self.normalize_text(text)
        lines = self.get_lines(text)

        # --------------------------------------------------------
        # Strong explicit labels
        # --------------------------------------------------------

        patterns = [
            r"\bInvoice\s*(?:Number|No\.?|#|ID|Ref(?:erence)?)"
            r"\s*[:#.\-]?\s*([A-Z0-9][A-Z0-9\-\/_.]+)",

            r"\bTax\s+Invoice\s*(?:Number|No\.?|#)"
            r"\s*[:#.\-]?\s*([A-Z0-9][A-Z0-9\-\/_.]+)",

            r"\bBill\s*(?:Number|No\.?|#)"
            r"\s*[:#.\-]?\s*([A-Z0-9][A-Z0-9\-\/_.]+)",

            r"\bDocument\s*(?:Number|No\.?|#)"
            r"\s*[:#.\-]?\s*([A-Z0-9][A-Z0-9\-\/_.]+)",

            r"\bReference\s*(?:Number|No\.?|#)"
            r"\s*[:#.\-]?\s*([A-Z0-9][A-Z0-9\-\/_.]+)"
        ]

        candidates = self.extract_all_candidates(
            text,
            patterns
        )

        # --------------------------------------------------------
        # Handle label/value on separate lines.
        # --------------------------------------------------------

        invoice_labels = {
            "invoice number",
            "invoice no",
            "invoice id",
            "invoice",
            "tax invoice number",
            "tax invoice no",
            "bill number",
            "bill no",
            "document number",
            "reference number"
        }

        for index, line in enumerate(lines):

            normalized = self.normalize_label(line)

            if normalized in invoice_labels:

                if index + 1 < len(lines):

                    candidate = lines[index + 1]

                    if self.looks_like_invoice_number(
                        candidate
                    ):
                        candidates.append(candidate)

        # --------------------------------------------------------
        # Modern layout:
        #
        # Invoice ID
        # Issued
        # Payment Due
        # TS-INV-998
        # ...
        # --------------------------------------------------------

        for index, line in enumerate(lines):

            if (
                self.normalize_label(line)
                == "invoice id"
                and index + 3 < len(lines)
            ):

                candidate = lines[index + 3]

                if self.looks_like_invoice_number(
                    candidate
                ):
                    candidates.append(candidate)

        # --------------------------------------------------------
        # OCR layout:
        #
        # Company Name Invoice No: ABC-001
        # --------------------------------------------------------

        scanned = re.search(
            r"^(.+?)\s+"
            r"(?:Invoice|lnvoice)\s*"
            r"(?:No|Number|ID)"
            r"\s*[:#.]?\s*"
            r"([A-Z0-9][A-Z0-9\-\/_.]+)",
            text,
            re.IGNORECASE | re.MULTILINE
        )

        if scanned:

            candidate = scanned.group(2)

            if self.looks_like_invoice_number(
                candidate
            ):
                candidates.append(candidate)

        # --------------------------------------------------------
        # Score candidates.
        # --------------------------------------------------------

        candidates = self.unique_values(
            candidates
        )

        if not candidates:
            return None

        scored = []

        for candidate in candidates:

            score = 0

            if re.search(
                r"[A-Za-z]",
                candidate
            ):
                score += 2

            if re.search(
                r"\d",
                candidate
            ):
                score += 2

            if "-" in candidate:
                score += 1

            if "/" in candidate:
                score += 1

            if len(candidate) <= 40:
                score += 1

            scored.append(
                (score, candidate)
            )

        scored.sort(
            key=lambda item: item[0],
            reverse=True
        )

        return scored[0][1]

    def looks_like_invoice_number(
        self,
        value: str
    ) -> bool:
        """
        Validate a likely invoice number.
        """

        value = value.strip()

        if not value:
            return False

        if len(value) > 60:
            return False

        if re.fullmatch(
            self.DATE_PATTERN,
            value,
            re.IGNORECASE
        ):
            return False

        if self.is_numeric_amount(value):
            return False

        return bool(
            re.search(
                r"[A-Za-z0-9]",
                value
            )
        )

    # ============================================================
    # VENDOR
    # ============================================================

    def extract_vendor_name(
        self,
        text: str
    ) -> Optional[str]:

        text = self.normalize_text(text)

        patterns = [
            r"\bVendor\s*[:\-]\s*([^\n]+)",
            r"\bSupplier\s*[:\-]\s*([^\n]+)",
            r"\bSeller\s*[:\-]\s*([^\n]+)",
            r"\bBilled\s+By\s*[:\-]\s*([^\n]+)",
            r"\bSold\s+By\s*[:\-]\s*([^\n]+)",
            r"\bFrom\s*[:\-]\s*([^\n]+)"
        ]

        vendor = self.extract_field(
            text,
            patterns
        )

        if vendor:
            return self.clean_company_name(
                vendor
            )

        # --------------------------------------------------------
        # Handle:
        #
        # TechSupply Solutions Pvt Ltd
        # Invoice
        # --------------------------------------------------------

        lines = self.get_lines(text)

        for index, line in enumerate(lines):

            if self.normalize_label(line) in {
                "invoice",
                "tax invoice",
                "commercial invoice"
            }:

                if index > 0:

                    candidate = lines[index - 1]

                    if self.looks_like_company_name(
                        candidate
                    ):
                        return self.clean_company_name(
                            candidate
                        )

        # --------------------------------------------------------
        # OCR:
        #
        # Company Invoice No: ...
        # --------------------------------------------------------

        scanned = re.search(
            r"^(.+?)\s+"
            r"(?:Invoice|lnvoice)\s*"
            r"(?:No|Number|ID)\s*:",
            text,
            re.IGNORECASE | re.MULTILINE
        )

        if scanned:

            candidate = scanned.group(1).strip()

            if self.looks_like_company_name(
                candidate
            ):
                return self.clean_company_name(
                    candidate
                )

        return None

    def clean_company_name(
        self,
        value: str
    ) -> Optional[str]:

        value = self.clean_value(value)

        if not value:
            return None

        value = re.sub(
            r"\s+(Invoice|Tax Invoice)$",
            "",
            value,
            flags=re.IGNORECASE
        )

        return value.strip()

    def looks_like_company_name(
        self,
        value: str
    ) -> bool:

        if not value:
            return False

        normalized = self.normalize_label(
            value
        )

        blocked = {
            "invoice",
            "tax invoice",
            "bill to",
            "from",
            "to",
            "description",
            "subtotal",
            "total"
        }

        if normalized in blocked:
            return False

        if len(value) > 120:
            return False

        return bool(
            re.search(
                r"[A-Za-z]",
                value
            )
        )

    def extract_vendor_address(
        self,
        text: str
    ) -> Optional[str]:

        text = self.normalize_text(text)

        patterns = [
            r"\bVendor\s+Address\s*[:\-]\s*([^\n]+)",
            r"\bSupplier\s+Address\s*[:\-]\s*([^\n]+)",
            r"\bSeller\s+Address\s*[:\-]\s*([^\n]+)",
            r"\bAddress\s*[:\-]\s*([^\n]+)"
        ]

        address = self.extract_field(
            text,
            patterns
        )

        if address:
            return self.clean_value(
                address
            )

        # --------------------------------------------------------
        # OCR structure:
        #
        # Invoice No: ABC-001
        # 45, HITEC City, Hyderabad, India
        # Invoice Date:
        # --------------------------------------------------------

        match = re.search(
            r"(?:Invoice|lnvoice)\s*"
            r"(?:No|Number|ID)\s*:\s*"
            r"[A-Z0-9\-\/_.]+\s+"
            r"(.+?)\s+"
            r"(?:Invoice|lnvoice)\s+Date",
            text,
            re.IGNORECASE
        )

        if match:

            return self.clean_value(
                match.group(1)
            )

        return None

    def extract_modern_vendor(
        self,
        text: str
    ) -> Optional[str]:

        lines = self.get_lines(text)

        for index, line in enumerate(lines):

            if (
                self.normalize_label(line)
                in {
                    "invoice",
                    "tax invoice"
                }
                and index > 0
            ):

                candidate = lines[index - 1]

                if self.looks_like_company_name(
                    candidate
                ):
                    return candidate

        return None

    # ============================================================
    # CUSTOMER
    # ============================================================

    def extract_customer(
        self,
        text: str
    ) -> Tuple[
        Optional[str],
        Optional[str]
    ]:

        text = self.normalize_text(text)

        lines = self.get_lines(text)

        labels = {
            "bill to",
            "billed to",
            "customer",
            "buyer",
            "client",
            "sold to"
        }

        # --------------------------------------------------------
        # Label followed by name/address.
        # --------------------------------------------------------

        for index, line in enumerate(lines):

            if self.normalize_label(line) in labels:

                customer_name = None
                customer_address = None

                if index + 1 < len(lines):

                    candidate = lines[index + 1]

                    if not self.is_section_label(
                        candidate
                    ):
                        customer_name = candidate

                if index + 2 < len(lines):

                    candidate = lines[index + 2]

                    if (
                        not self.is_section_label(
                            candidate
                        )
                        and not self.looks_like_table_header(
                            candidate
                        )
                    ):
                        customer_address = candidate

                return (
                    customer_name,
                    customer_address
                )

        # --------------------------------------------------------
        # Same-line customer labels.
        # --------------------------------------------------------

        patterns = [
            r"\bBill\s+To\s*[:\-]\s*([^\n]+)",
            r"\bBilled\s+To\s*[:\-]\s*([^\n]+)",
            r"\bCustomer\s*[:\-]\s*([^\n]+)",
            r"\bBuyer\s*[:\-]\s*([^\n]+)",
            r"\bClient\s*[:\-]\s*([^\n]+)",
            r"\bSold\s+To\s*[:\-]\s*([^\n]+)"
        ]

        customer = self.extract_field(
            text,
            patterns
        )

        if customer:

            return (
                self.clean_value(customer),
                None
            )

        # --------------------------------------------------------
        # OCR structure:
        #
        # BILL TO
        # Company
        # Address
        # Description Qty ...
        # --------------------------------------------------------

        match = re.search(
            r"\bBILL\s+TO\b\s+"
            r"(.+?)"
            r"(?="
            r"\bDescription\b"
            r"|\bItem\b"
            r"|\bProduct\b"
            r")",
            text,
            re.IGNORECASE
        )

        if match:

            section = match.group(1).strip()

            section_lines = [
                x.strip()
                for x in re.split(
                    r"\n+",
                    section
                )
                if x.strip()
            ]

            if section_lines:

                return (
                    section_lines[0],
                    (
                        section_lines[1]
                        if len(section_lines) > 1
                        else None
                    )
                )

        return None, None

    def is_section_label(
        self,
        value: str
    ) -> bool:

        normalized = self.normalize_label(
            value
        )

        labels = {
            "invoice",
            "tax invoice",
            "description",
            "item",
            "product",
            "subtotal",
            "tax",
            "total",
            "payment terms",
            "notes",
            "terms and conditions"
        }

        return normalized in labels

    def looks_like_table_header(
        self,
        value: str
    ) -> bool:

        normalized = self.normalize_label(
            value
        )

        keywords = {
            "description",
            "item",
            "product",
            "qty",
            "quantity",
            "unit price",
            "price",
            "amount",
            "total"
        }

        matches = sum(
            1
            for word in keywords
            if word in normalized
        )

        return matches >= 2

    # ============================================================
    # DATES
    # ============================================================

    def extract_date(
        self,
        text: str,
        field_name: str
    ) -> Optional[str]:

        aliases = {
            "Invoice Date": [
                "Invoice Date",
                "Issue Date",
                "Issued",
                "Date of Issue",
                "Billing Date",
                "Document Date"
            ],
            "Due Date": [
                "Due Date",
                "Payment Due",
                "Due",
                "Pay By",
                "Payment Date"
            ]
        }

        labels = aliases.get(
            field_name,
            [field_name]
        )

        for label in labels:

            escaped = re.escape(label)

            patterns = [
                rf"\b{escaped}\b\s*[:#\-]?\s*"
                rf"({self.DATE_PATTERN})"
            ]

            value = self.extract_field(
                text,
                patterns
            )

            if value:
                return value

        # --------------------------------------------------------
        # Label and value on separate lines.
        # --------------------------------------------------------

        lines = self.get_lines(text)

        normalized_labels = {
            self.normalize_label(label)
            for label in labels
        }

        for index, line in enumerate(lines):

            if (
                self.normalize_label(line)
                in normalized_labels
            ):

                if index + 1 < len(lines):

                    candidate = lines[index + 1]

                    if re.fullmatch(
                        self.DATE_PATTERN,
                        candidate,
                        re.IGNORECASE
                    ):
                        return candidate

        return None

    def extract_modern_invoice_dates(
        self,
        text: str
    ) -> Tuple[
        Optional[str],
        Optional[str],
        Optional[str]
    ]:

        lines = self.get_lines(text)

        for index, line in enumerate(lines):

            if (
                self.normalize_label(line)
                == "invoice id"
                and index + 5 < len(lines)
            ):

                if (
                    self.normalize_label(
                        lines[index + 1]
                    ) == "issued"
                    and
                    self.normalize_label(
                        lines[index + 2]
                    ) == "payment due"
                ):

                    return (
                        lines[index + 3],
                        lines[index + 4],
                        lines[index + 5]
                    )

        return None, None, None

    # ============================================================
    # CURRENCY
    # ============================================================

    def extract_currency(
        self,
        text: str
    ) -> Optional[str]:

        if not text:
            return None

        # Prefer explicit currency code.
        for code in self.CURRENCY_CODES:

            if re.search(
                rf"\b{re.escape(code)}\b",
                text,
                re.IGNORECASE
            ):
                return code

        # Currency words.
        currency_words = {
            "rupees": "INR",
            "rupee": "INR",
            "indian rupees": "INR",
            "dollars": "USD",
            "dollar": "USD",
            "euros": "EUR",
            "euro": "EUR",
            "pounds": "GBP",
            "pound": "GBP"
        }

        lower = text.lower()

        for word, code in currency_words.items():

            if word in lower:
                return code

        # Symbols.
        for symbol, code in sorted(
            self.CURRENCY_SYMBOLS.items(),
            key=lambda item: len(item[0]),
            reverse=True
        ):

            if symbol in text:
                return code

        return None

    # ============================================================
    # FINANCIAL FIELDS
    # ============================================================

    def extract_subtotal(
        self,
        text: str
    ) -> Optional[float]:

        patterns = [
            r"\bSub\s*Total\b\s*[:\-]?\s*"
            rf"({self.NUMBER_PATTERN})",

            r"\bSubtotal\b\s*[:\-]?\s*"
            rf"({self.NUMBER_PATTERN})",

            r"\bNet\s+Amount\b\s*[:\-]?\s*"
            rf"({self.NUMBER_PATTERN})",

            r"\bTaxable\s+Amount\b\s*[:\-]?\s*"
            rf"({self.NUMBER_PATTERN})"
        ]

        return self.extract_amount(
            text,
            patterns
        )

    def extract_tax(
        self,
        text: str
    ) -> Optional[float]:

        # First look for explicit combined tax.
        patterns = [
            r"\bTax\b(?:\s*\([^)]*\))?"
            r"\s*[:\-]?\s*"
            rf"({self.NUMBER_PATTERN})",

            r"\bGST\b\s*[:\-]?\s*"
            rf"({self.NUMBER_PATTERN})",

            r"\bVAT\b\s*[:\-]?\s*"
            rf"({self.NUMBER_PATTERN})",

            r"\bTotal\s+Tax\b\s*[:\-]?\s*"
            rf"({self.NUMBER_PATTERN})"
        ]

        tax = self.extract_amount(
            text,
            patterns
        )

        if tax is not None:
            return tax

        # --------------------------------------------------------
        # Indian GST:
        #
        # CGST 900
        # SGST 900
        #
        # or:
        #
        # CGST: 900
        # SGST: 900
        # --------------------------------------------------------

        cgst = self.extract_amount(
            text,
            [
                rf"\bCGST\b[^0-9]*"
                rf"({self.NUMBER_PATTERN})"
            ]
        )

        sgst = self.extract_amount(
            text,
            [
                rf"\bSGST\b[^0-9]*"
                rf"({self.NUMBER_PATTERN})"
            ]
        )

        igst = self.extract_amount(
            text,
            [
                rf"\bIGST\b[^0-9]*"
                rf"({self.NUMBER_PATTERN})"
            ]
        )

        values = [
            value
            for value in (
                cgst,
                sgst,
                igst
            )
            if value is not None
        ]

        if values:
            return round(
                sum(values),
                2
            )

        return None

    def extract_total_amount(
        self,
        text: str
    ) -> Optional[float]:

        patterns = [
            r"\bTotal\s+Amount\b"
            r"\s*[:\-|I₹$€£\s]*"
            rf"({self.NUMBER_PATTERN})",

            r"\bAmount\s+Payable\b"
            r"\s*[:\-|I₹$€£\s]*"
            rf"({self.NUMBER_PATTERN})",

            r"\bGrand\s+Total\b"
            r"\s*[:\-|I₹$€€£\s]*"
            rf"({self.NUMBER_PATTERN})",

            r"\bTotal\s+Due\b"
            r"\s*[:\-|I₹$€£\s]*"
            rf"({self.NUMBER_PATTERN})",

            r"\bBalance\s+Due\b"
            r"\s*[:\-|I₹$€£\s]*"
            rf"({self.NUMBER_PATTERN})",

            r"(?<!Sub)\bTotal\b"
            r"\s*[:\-|I₹$€£\s]*"
            rf"({self.NUMBER_PATTERN})"
        ]

        candidates = self.extract_all_candidates(
            text,
            patterns
        )

        # Prefer explicit total labels.
        if candidates:

            values = []

            for candidate in candidates:

                amount = self.parse_amount(
                    candidate
                )

                if amount is not None:
                    values.append(amount)

            if values:
                return max(values)

        return None

    # ============================================================
    # LINE ITEM HEADER DETECTION
    # ============================================================

    def find_line_items_start(
        self,
        lines: List[str]
    ) -> Optional[int]:

        normalized = [
            self.normalize_label(line)
            for line in lines
        ]

        header_aliases = {
            "description",
            "item",
            "product",
            "particulars",
            "details",
            "qty",
            "quantity",
            "units",
            "unit price",
            "price",
            "rate",
            "amount",
            "total",
            "line total",
            "net amount"
        }

        best_index = None
        best_score = 0

        for index, line in enumerate(
            normalized
        ):

            score = 0

            # Inspect current line and nearby lines.
            window = " ".join(
                normalized[
                    index:min(
                        index + 6,
                        len(normalized)
                    )
                ]
            )

            for alias in header_aliases:

                if alias in window:
                    score += 1

            # A proper item header usually has
            # description/item + quantity + price/amount.
            has_description = any(
                word in window
                for word in [
                    "description",
                    "item",
                    "product",
                    "particulars",
                    "details"
                ]
            )

            has_quantity = any(
                word in window
                for word in [
                    "quantity",
                    "qty",
                    "units"
                ]
            )

            has_amount = any(
                word in window
                for word in [
                    "amount",
                    "total",
                    "price",
                    "rate"
                ]
            )

            if (
                has_description
                and has_quantity
                and has_amount
            ):
                score += 5

            if score > best_score:

                best_score = score
                best_index = index

        if best_index is None:
            return None

        if best_score < 5:
            return None

        # Determine where actual rows start.
        return best_index + 1

    # ============================================================
    # LINE ITEM ROW PARSING
    # ============================================================

    def parse_line_item_row(
        self,
        line: str
    ) -> Optional[InvoiceLineItem]:
        """
        Parse common single-line invoice rows.

        Examples:

        Laptop 2 50000 100000
        Mouse 5 500 2500
        """

        line = line.strip()

        if not line:
            return None

        if self.is_stop_line(line):
            return None

        # --------------------------------------------------------
        # Description + quantity + unit price + total
        # --------------------------------------------------------

        pattern = (
            r"^(.+?)\s+"
            r"(\d+(?:\.\d+)?)\s+"
            r"(?:₹|Rs\.?|INR|USD|\$|€|£)?\s*"
            r"([\d,]+(?:\.\d+)?)\s+"
            r"(?:₹|Rs\.?|INR|USD|\$|€|£)?\s*"
            r"([\d,]+(?:\.\d+)?)$"
        )

        match = re.match(
            pattern,
            line,
            re.IGNORECASE
        )

        if not match:
            return None

        description = self.clean_value(
            match.group(1)
        )

        quantity = self.parse_amount(
            match.group(2)
        )

        unit_price = self.parse_amount(
            match.group(3)
        )

        total = self.parse_amount(
            match.group(4)
        )

        if not description:
            return None

        if (
            quantity is None
            or unit_price is None
            or total is None
        ):
            return None

        if quantity <= 0:
            return None

        # Validate arithmetic.
        if not self.validate_line_item_math(
            quantity,
            unit_price,
            total
        ):
            return None

        return InvoiceLineItem(
            description=description,
            quantity=quantity,
            unit_price=unit_price,
            total=total
        )

    def validate_line_item_math(
        self,
        quantity: float,
        unit_price: float,
        total: float
    ) -> bool:

        expected = (
            quantity * unit_price
        )

        tolerance = max(
            1.0,
            abs(expected) * 0.05
        )

        return (
            abs(expected - total)
            <= tolerance
        )

    def is_stop_line(
        self,
        line: str
    ) -> bool:

        normalized = self.normalize_label(
            line
        )

        for word in self.STOP_WORDS:

            if normalized == self.normalize_label(
                word
            ):
                return True

        return any(
            normalized.startswith(
                self.normalize_label(word)
            )
            for word in [
                "subtotal",
                "sub total",
                "tax",
                "gst",
                "cgst",
                "sgst",
                "igst",
                "vat",
                "grand total",
                "total amount",
                "amount payable",
                "balance due"
            ]
        )

    # ============================================================
    # MULTI-LINE LINE ITEMS
    # ============================================================

    def extract_multiline_line_items(
        self,
        text: str
    ) -> List[InvoiceLineItem]:

        lines = self.get_lines(text)

        start_index = (
            self.find_line_items_start(
                lines
            )
        )

        if start_index is None:
            return []

        items = []

        index = start_index

        while index < len(lines):

            line = lines[index]

            if self.is_stop_line(line):
                break

            # ----------------------------------------------------
            # First attempt: one-line row.
            # ----------------------------------------------------

            item = self.parse_line_item_row(
                line
            )

            if item:

                items.append(item)
                index += 1
                continue

            # ----------------------------------------------------
            # Existing multiline format:
            #
            # Description
            # Quantity
            # Unit Price
            # Total
            # ----------------------------------------------------

            if index + 3 < len(lines):

                description = lines[index]

                quantity = self.parse_amount(
                    lines[index + 1]
                )

                unit_price = self.parse_amount(
                    lines[index + 2]
                )

                total = self.parse_amount(
                    lines[index + 3]
                )

                if (
                    quantity is not None
                    and unit_price is not None
                    and total is not None
                    and quantity > 0
                    and self.validate_line_item_math(
                        quantity,
                        unit_price,
                        total
                    )
                ):

                    items.append(
                        InvoiceLineItem(
                            description=description,
                            quantity=quantity,
                            unit_price=unit_price,
                            total=total
                        )
                    )

                    index += 4
                    continue

            index += 1

        return items

    # ============================================================
    # SCANNED OCR LINE ITEMS
    # ============================================================

    def extract_scanned_line_items(
        self,
        text: str
    ) -> List[InvoiceLineItem]:

        # --------------------------------------------------------
        # First try newline-based extraction.
        # --------------------------------------------------------

        lines = self.get_lines(text)

        items = []

        for line in lines:

            item = self.parse_line_item_row(
                line
            )

            if item:
                items.append(item)

        if items:
            return items

        # --------------------------------------------------------
        # Single-line OCR extraction.
        # --------------------------------------------------------

        normalized = re.sub(
            r"\s+",
            " ",
            text
        )

        section_match = re.search(
            r"(?:Description|Item|Product|Particulars)"
            r"\s+"
            r"(?:Qty|Quantity|Units)"
            r"\s+"
            r"(?:Unit\s+Price|Price|Rate)"
            r"\s+"
            r"(?:Amount|Total)"
            r"\s+"
            r"(.+?)"
            r"(?="
            r"\s+(?:Subtotal|Sub\s+Total|Tax|GST|"
            r"Grand\s+Total|Total\s+Amount|"
            r"Amount\s+Payable)"
            r")",
            normalized,
            re.IGNORECASE
        )

        if not section_match:
            return []

        items_text = section_match.group(1).strip()

        pattern = (
            r"([A-Za-z][A-Za-z0-9\s\-./&()]+?)\s+"
            r"(\d+(?:\.\d+)?)\s+"
            r"(?:₹|Rs\.?|INR|USD|\$|€|£)?\s*"
            r"([\d,]+(?:\.\d+)?)\s+"
            r"(?:₹|Rs\.?|INR|USD|\$|€|£)?\s*"
            r"([\d,]+(?:\.\d+)?)"
        )

        matches = re.findall(
            pattern,
            items_text,
            re.IGNORECASE
        )

        for match in matches:

            description = self.clean_value(
                match[0]
            )

            quantity = self.parse_amount(
                match[1]
            )

            unit_price = self.parse_amount(
                match[2]
            )

            total = self.parse_amount(
                match[3]
            )

            if not description:
                continue

            if (
                quantity is None
                or unit_price is None
                or total is None
                or quantity <= 0
            ):
                continue

            if not self.validate_line_item_math(
                quantity,
                unit_price,
                total
            ):
                continue

            items.append(
                InvoiceLineItem(
                    description=description,
                    quantity=quantity,
                    unit_price=unit_price,
                    total=total
                )
            )

        return items

    # ============================================================
    # MAIN LINE ITEM EXTRACTION
    # ============================================================

    def extract_line_items(
        self,
        text: str
    ) -> List[InvoiceLineItem]:

        multiline_items = (
            self.extract_multiline_line_items(
                text
            )
        )

        if multiline_items:
            return multiline_items

        return (
            self.extract_scanned_line_items(
                text
            )
        )

    # ============================================================
    # FINANCIAL VALIDATION
    # ============================================================

    def validate_financials(
        self,
        line_items: List[InvoiceLineItem],
        subtotal: Optional[float],
        tax: Optional[float],
        total_amount: Optional[float]
    ) -> Dict[str, Any]:
        """
        Validate invoice arithmetic.

        Returns diagnostic information without
        modifying extracted values.
        """

        result = {
            "line_items_match_subtotal": None,
            "subtotal_tax_match_total": None,
            "calculated_subtotal": None
        }

        if line_items:

            calculated = round(
                sum(
                    item.total
                    for item in line_items
                ),
                2
            )

            result[
                "calculated_subtotal"
            ] = calculated

            if subtotal is not None:

                tolerance = max(
                    1.0,
                    abs(subtotal) * 0.02
                )

                result[
                    "line_items_match_subtotal"
                ] = (
                    abs(
                        calculated - subtotal
                    )
                    <= tolerance
                )

        if (
            subtotal is not None
            and tax is not None
            and total_amount is not None
        ):

            expected = round(
                subtotal + tax,
                2
            )

            tolerance = max(
                1.0,
                abs(total_amount) * 0.02
            )

            result[
                "subtotal_tax_match_total"
            ] = (
                abs(
                    expected - total_amount
                )
                <= tolerance
            )

        return result

    # ============================================================
    # EXTRACTION CONFIDENCE
    # ============================================================

    def calculate_extraction_confidence(
        self,
        invoice_number: Optional[str],
        invoice_date: Optional[str],
        vendor_name: Optional[str],
        line_items: List[InvoiceLineItem],
        subtotal: Optional[float],
        tax: Optional[float],
        total_amount: Optional[float]
    ) -> float:
        """
        Calculate a lightweight document-level
        extraction confidence.

        This is not an ML probability.
        It is an explainable heuristic score.
        """

        score = 0.0

        if invoice_number:
            score += 15

        if invoice_date:
            score += 10

        if vendor_name:
            score += 15

        if line_items:
            score += 20

        if subtotal is not None:
            score += 10

        if tax is not None:
            score += 10

        if total_amount is not None:
            score += 20

        return round(
            min(score, 100.0),
            2
        )

    # ============================================================
    # MAIN EXTRACTION
    # ============================================================

    def extract(
        self,
        text: str
    ) -> Invoice:

        text = self.normalize_text(text)

        # --------------------------------------------------------
        # Modern invoice metadata
        # --------------------------------------------------------

        (
            modern_invoice_number,
            modern_invoice_date,
            modern_due_date
        ) = self.extract_modern_invoice_dates(
            text
        )

        # --------------------------------------------------------
        # Invoice number
        # --------------------------------------------------------

        invoice_number = (
            self.extract_invoice_number(
                text
            )
        )

        if not invoice_number:
            invoice_number = (
                modern_invoice_number
            )

        # --------------------------------------------------------
        # Invoice date
        # --------------------------------------------------------

        invoice_date = self.extract_date(
            text,
            "Invoice Date"
        )

        if not invoice_date:
            invoice_date = (
                modern_invoice_date
            )

        # --------------------------------------------------------
        # Due date
        # --------------------------------------------------------

        due_date = self.extract_date(
            text,
            "Due Date"
        )

        if not due_date:
            due_date = modern_due_date

        # --------------------------------------------------------
        # Vendor
        # --------------------------------------------------------

        vendor_name = (
            self.extract_vendor_name(
                text
            )
        )

        if not vendor_name:

            vendor_name = (
                self.extract_modern_vendor(
                    text
                )
            )

        vendor_address = (
            self.extract_vendor_address(
                text
            )
        )

        vendor = None

        if vendor_name:

            vendor = Vendor(
                name=vendor_name,
                address=vendor_address
            )

        # --------------------------------------------------------
        # Customer
        # --------------------------------------------------------

        (
            customer_name,
            customer_address
        ) = self.extract_customer(
            text
        )

        # --------------------------------------------------------
        # Line items
        # --------------------------------------------------------

        line_items = self.extract_line_items(
            text
        )

        # --------------------------------------------------------
        # Financial fields
        # --------------------------------------------------------

        subtotal = self.extract_subtotal(
            text
        )

        tax = self.extract_tax(
            text
        )

        total_amount = (
            self.extract_total_amount(
                text
            )
        )

        # OCR table columns can separate a tax label from its amount.
        # Recover it only when the invoice totals provide a strict check.
        if (
            tax is None
            and subtotal is not None
            and total_amount is not None
            and total_amount > subtotal
        ):
            derived_tax = round(total_amount - subtotal, 2)
            if derived_tax > 0:
                tax = derived_tax

        # --------------------------------------------------------
        # Currency
        # --------------------------------------------------------

        currency = self.extract_currency(
            text
        )

        # --------------------------------------------------------
        # Financial validation
        # --------------------------------------------------------

        validation = (
            self.validate_financials(
                line_items,
                subtotal,
                tax,
                total_amount
            )
        )

        # --------------------------------------------------------
        # Conservative correction:
        #
        # If subtotal is missing but line items are
        # confidently extracted, calculate subtotal.
        # --------------------------------------------------------

        if (
            subtotal is None
            and line_items
        ):

            calculated = (
                validation[
                    "calculated_subtotal"
                ]
            )

            if calculated is not None:
                subtotal = calculated

        # --------------------------------------------------------
        # Conservative correction:
        #
        # If total is missing and subtotal + tax are
        # available, calculate it.
        # --------------------------------------------------------

        if (
            total_amount is None
            and subtotal is not None
            and tax is not None
        ):

            total_amount = round(
                subtotal + tax,
                2
            )

        # --------------------------------------------------------
        # Return existing Pydantic schema.
        #
        # IMPORTANT:
        # No schema changes are required.
        # --------------------------------------------------------

        return Invoice(
            invoice_number=invoice_number,
            invoice_date=invoice_date,
            due_date=due_date,
            vendor=vendor,
            customer_name=customer_name,
            customer_address=customer_address,
            currency=currency,
            line_items=line_items,
            subtotal=subtotal,
            tax=tax,
            total_amount=total_amount
        )