import re
from typing import Optional, List, Tuple

from app.models.delivery_note import (
    DeliveryNote,
    DeliveryItem,
    Recipient
)

from app.services.ocr_correction_service import OCRCorrectionService


class DeliveryNoteExtractor:
    """
    Robust rule-based delivery note extractor.

    Designed to handle:
    - Digital PDFs
    - OCR text
    - Different delivery note layouts
    - Different terminology
    - Single-line and multi-line tables
    - Common quantity/unit variations

    The public API intentionally remains:
        DeliveryNoteExtractor.extract(text)

    so it can be used without changing the existing
    document processing pipeline.
    """

    # ============================================================
    # CONFIGURATION
    # ============================================================

    NUMBER_PATTERN = r"\d+(?:[.,]\d+)*"

    UNIT_ALIASES = {
        "piece",
        "pieces",
        "pc",
        "pcs",
        "unit",
        "units",
        "item",
        "items",
        "kg",
        "kgs",
        "g",
        "gm",
        "gms",
        "gram",
        "grams",
        "mg",
        "ton",
        "tons",
        "tonne",
        "tonnes",
        "box",
        "boxes",
        "pack",
        "packs",
        "packet",
        "packets",
        "case",
        "cases",
        "carton",
        "cartons",
        "set",
        "sets",
        "pair",
        "pairs",
        "dozen",
        "dozens",
        "litre",
        "litres",
        "liter",
        "liters",
        "l",
        "ml",
        "meter",
        "meters",
        "metre",
        "metres",
        "m"
    }

    STOP_WORDS = {
        "subtotal",
        "total",
        "grand total",
        "status",
        "delivery status",
        "remarks",
        "remark",
        "signature",
        "authorized",
        "authorised",
        "received by",
        "prepared by",
        "approved by",
        "notes",
        "comments"
    }

    HEADER_TERMS = {
        "item",
        "items",
        "product",
        "products",
        "description",
        "material",
        "goods",
        "particulars"
    }

    ORDERED_TERMS = {
        "ordered",
        "ordered qty",
        "ordered quantity",
        "order qty",
        "order quantity",
        "requested",
        "requested qty",
        "requested quantity",
        "qty ordered",
        "quantity ordered"
    }

    DELIVERED_TERMS = {
        "delivered",
        "delivered qty",
        "delivered quantity",
        "received",
        "received qty",
        "received quantity",
        "qty delivered",
        "quantity delivered",
        "qty received",
        "quantity received",
        "actual qty",
        "actual quantity"
    }

    UNIT_TERMS = {
        "unit",
        "units",
        "uom",
        "unit of measure",
        "measure",
        "measurement"
    }

    # ============================================================
    # NORMALIZATION
    # ============================================================

    def normalize_text(
        self,
        text: str
    ) -> str:
        """
        Normalize OCR/PDF text while preserving line structure.
        """

        if not text:
            return ""

        text = text.replace("\r\n", "\n")
        text = text.replace("\r", "\n")

        # Normalize common OCR characters.
        text = text.replace("—", "-")
        text = text.replace("–", "-")
        text = text.replace("“", '"')
        text = text.replace("”", '"')
        text = text.replace("‘", "'")
        text = text.replace("’", "'")

        # Remove excessive spaces.
        text = re.sub(
            r"[ \t]+",
            " ",
            text
        )

        # Remove excessive blank lines.
        text = re.sub(
            r"\n{3,}",
            "\n\n",
            text
        )

        return text.strip()

    def get_lines(
        self,
        text: str
    ) -> List[str]:
        """
        Return normalized non-empty lines.
        """

        text = self.normalize_text(text)

        return [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

    def normalize_label(
        self,
        value: str
    ) -> str:
        """
        Normalize labels for flexible header matching.
        """

        value = value.lower().strip()

        value = re.sub(
            r"[:|]+$",
            "",
            value
        )

        value = re.sub(
            r"\s+",
            " ",
            value
        )

        return value

    # ============================================================
    # GENERIC FIELD EXTRACTION
    # ============================================================

    def extract_field(
        self,
        text: str,
        patterns: List[str]
    ) -> Optional[str]:
        """
        Try multiple regex patterns and return
        the first non-empty result.
        """

        if not text:
            return None

        for pattern in patterns:

            match = re.search(
                pattern,
                text,
                re.IGNORECASE | re.MULTILINE
            )

            if not match:
                continue

            value = match.group(1).strip()

            if value:
                return value

        return None

    def extract_labeled_value(
        self,
        text: str,
        labels: List[str]
    ) -> Optional[str]:
        """
        Extract values from common label:value layouts.

        Handles:
            Supplier: ABC Ltd
            Supplier - ABC Ltd
            Supplier ABC Ltd
            Supplier | ABC Ltd
        """

        escaped_labels = [
            re.escape(label)
            for label in labels
        ]

        label_pattern = "|".join(
            escaped_labels
        )

        pattern = (
            rf"^(?:{label_pattern})"
            rf"\s*(?:[:|=-]\s*)?"
            rf"([^\n|]+)$"
        )

        return self.extract_field(
            text,
            [pattern]
        )

    # ============================================================
    # DELIVERY NOTE NUMBER
    # ============================================================

    def extract_delivery_note_number(
        self,
        text: str
    ) -> Optional[str]:
        """
        Extract delivery note/reference number.

        Supports:
            Delivery Note Number: DN-001
            Delivery Note No: DN-001
            Delivery Note #: DN-001
            Delivery Reference: DN-001
            Reference: DN-001
            DN Number: DN-001
        """

        patterns = [
            r"Delivery\s*Note\s*(?:Number|No\.?|#)"
            r"\s*[:|=-]?\s*([A-Z0-9][A-Z0-9._/\-]*)",

            r"Delivery\s*Reference"
            r"\s*[:|=-]?\s*([A-Z0-9][A-Z0-9._/\-]*)",

            r"Reference"
            r"\s*[:|=-]?\s*([A-Z0-9][A-Z0-9._/\-]*)",

            r"DN\s*(?:Number|No\.?|#)"
            r"\s*[:|=-]?\s*([A-Z0-9][A-Z0-9._/\-]*)"
        ]

        value = self.extract_field(
            text,
            patterns
        )

        if value:
            return value.strip(".,:;")

        # OCR-friendly fallback.
        lines = self.get_lines(text)

        for line in lines:

            normalized = self.normalize_label(
                line
            )

            if (
                normalized.startswith("delivery note")
                and any(
                    char.isdigit()
                    for char in line
                )
            ):

                match = re.search(
                    r"([A-Z]{0,5}[-/]?\d{2,}[\w./-]*)",
                    line,
                    re.IGNORECASE
                )

                if match:
                    return match.group(1)

        return None

    # ============================================================
    # VENDOR / SUPPLIER
    # ============================================================

    def extract_vendor_name(
        self,
        text: str
    ) -> Optional[str]:
        """
        Extract supplier/vendor name.
        """

        value = self.extract_labeled_value(
            text,
            [
                "Vendor",
                "Supplier",
                "Seller",
                "Shipper",
                "From"
            ]
        )

        if value:
            return value

        lines = self.get_lines(text)

        # Handle:
        #
        # SUPPLIER
        # TechSupply Solutions Pvt Ltd
        #
        # or:
        #
        # FROM
        # ABC Corporation

        labels = {
            "vendor",
            "supplier",
            "seller",
            "shipper",
            "from"
        }

        for index, line in enumerate(lines):

            if self.normalize_label(line) in labels:

                if index + 1 < len(lines):

                    candidate = lines[index + 1]

                    if not self.looks_like_label(
                        candidate
                    ):
                        return candidate

        return None

    # ============================================================
    # DELIVERY DATE
    # ============================================================

    def extract_delivery_date(
        self,
        text: str
    ) -> Optional[str]:
        """
        Extract delivery date using multiple common labels.
        """

        patterns = [
            r"Delivery\s*Date"
            r"\s*[:|=-]?\s*([^\n|]+)",

            r"Date\s*Delivered"
            r"\s*[:|=-]?\s*([^\n|]+)",

            r"Delivered\s*Date"
            r"\s*[:|=-]?\s*([^\n|]+)",

            r"Date\s*of\s*Delivery"
            r"\s*[:|=-]?\s*([^\n|]+)",

            r"Delivery\s*Dt\.?"
            r"\s*[:|=-]?\s*([^\n|]+)",

            r"Received\s*On"
            r"\s*[:|=-]?\s*([^\n|]+)",

            r"Received\s*Date"
            r"\s*[:|=-]?\s*([^\n|]+)"
        ]

        value = self.extract_field(
            text,
            patterns
        )

        if value:
            return value

        # Generic DATE fallback, used only when
        # the document clearly contains delivery terminology.
        if re.search(
            r"\b(delivery|delivered|dispatch|shipment)\b",
            text,
            re.IGNORECASE
        ):

            return self.extract_field(
                text,
                [
                    r"^\s*Date\s*[:|=-]?\s*"
                    r"([0-9]{1,4}[-/][0-9]{1,2}[-/][0-9]{2,4})$",

                    r"^\s*Date\s*[:|=-]?\s*"
                    r"([0-9]{1,2}\s+"
                    r"[A-Za-z]{3,9}\s+"
                    r"[0-9]{4})$"
                ]
            )

        return None

    # ============================================================
    # RECIPIENT
    # ============================================================

    def extract_recipient_name(
        self,
        text: str
    ) -> Optional[str]:
        """
        Extract recipient / consignee / receiving company.
        """

        value = self.extract_labeled_value(
            text,
            [
                "Deliver To",
                "Deliver To:",
                "Receiving Company",
                "Recipient",
                "Consignee",
                "Ship To",
                "Received By"
            ]
        )

        if value:
            return value

        lines = self.get_lines(text)

        labels = {
            "deliver to",
            "receiving company",
            "recipient",
            "consignee",
            "ship to",
            "received by"
        }

        for index, line in enumerate(lines):

            normalized = self.normalize_label(
                line
            )

            if normalized in labels:

                if index + 1 < len(lines):

                    candidate = lines[index + 1]

                    if not self.looks_like_label(
                        candidate
                    ):
                        return candidate

        return None

    def extract_recipient_address(
        self,
        text: str
    ) -> Optional[str]:
        """
        Extract delivery/recipient address.
        """

        value = self.extract_labeled_value(
            text,
            [
                "Delivery Address",
                "Recipient Address",
                "Receiving Address",
                "Address",
                "Location"
            ]
        )

        if value:
            return value

        lines = self.get_lines(text)

        recipient_labels = {
            "deliver to",
            "receiving company",
            "recipient",
            "consignee",
            "ship to"
        }

        for index, line in enumerate(lines):

            if self.normalize_label(line) in recipient_labels:

                if index + 2 < len(lines):

                    candidate = lines[index + 2]

                    if not self.looks_like_label(
                        candidate
                    ):
                        return candidate

        return None

    # ============================================================
    # DELIVERY STATUS
    # ============================================================

    def extract_delivery_status(
        self,
        text: str
    ) -> Optional[str]:
        """
        Extract explicit delivery status.

        If no explicit status exists, infer:
            DELIVERED
            PARTIAL
            PENDING
        only when sufficient evidence exists.
        """

        value = self.extract_labeled_value(
            text,
            [
                "Delivery Status",
                "Status",
                "Delivery State"
            ]
        )

        if value:
            return self.normalize_status(
                value
            )

        # --------------------------------------------------------
        # Infer status from common phrases.
        # --------------------------------------------------------

        lower_text = text.lower()

        if re.search(
            r"\b(partially\s+delivered|partial\s+delivery|"
            r"short\s+delivery|partially\s+received)\b",
            lower_text
        ):
            return "PARTIAL"

        if re.search(
            r"\b(fully\s+delivered|completely\s+delivered|"
            r"delivered\s+in\s+full|fully\s+received)\b",
            lower_text
        ):
            return "DELIVERED"

        return None

    def normalize_status(
        self,
        value: str
    ) -> str:
        """
        Normalize common status variations.
        """

        normalized = value.strip().upper()

        aliases = {
            "COMPLETE": "DELIVERED",
            "COMPLETED": "DELIVERED",
            "FULL": "DELIVERED",
            "FULLY DELIVERED": "DELIVERED",
            "FULLY RECEIVED": "DELIVERED",
            "RECEIVED": "DELIVERED",

            "PART": "PARTIAL",
            "PARTIALLY DELIVERED": "PARTIAL",
            "PARTIAL DELIVERY": "PARTIAL",
            "PARTIALLY RECEIVED": "PARTIAL",

            "PENDING DELIVERY": "PENDING",
            "AWAITING DELIVERY": "PENDING"
        }

        return aliases.get(
            normalized,
            normalized
        )

    # ============================================================
    # NUMERIC HELPERS
    # ============================================================

    def clean_number(
        self,
        value: str
    ) -> Optional[float]:
        """
        Convert common numeric representations to float.

        Handles:
            10
            10.5
            1,000
            1,000.50
        """

        if not value:
            return None

        value = value.strip()

        # Remove currency-like/non-numeric characters,
        # but preserve decimal separators.
        cleaned = re.sub(
            r"[^\d.,\-]",
            "",
            value
        )

        if not cleaned:
            return None

        # Handle comma thousands separators.
        if "," in cleaned and "." in cleaned:

            if cleaned.rfind(".") > cleaned.rfind(","):
                cleaned = cleaned.replace(",", "")

            else:
                cleaned = (
                    cleaned
                    .replace(".", "")
                    .replace(",", ".")
                )

        elif "," in cleaned:

            parts = cleaned.split(",")

            # 1,000 -> 1000
            if (
                len(parts) == 2
                and len(parts[1]) == 3
            ):
                cleaned = "".join(parts)

            else:
                cleaned = cleaned.replace(
                    ",",
                    "."
                )

        try:
            return float(cleaned)

        except ValueError:
            return None

    def is_number(
        self,
        value: str
    ) -> bool:
        """
        Check whether a value represents a number.
        """

        return (
            self.clean_number(value)
            is not None
        )

    def is_unit(
        self,
        value: str
    ) -> bool:
        """
        Check whether a value represents a known unit.
        """

        normalized = (
            value
            .strip()
            .lower()
            .rstrip(".")
        )

        return normalized in self.UNIT_ALIASES

    def normalize_unit(
        self,
        value: str
    ) -> str:
        """
        Normalize common unit spellings.
        """

        normalized = (
            value
            .strip()
            .lower()
            .rstrip(".")
        )

        aliases = {
            "pc": "pieces",
            "pcs": "pieces",
            "piece": "pieces",

            "unit": "units",

            "kg": "kg",
            "kgs": "kg",

            "g": "grams",
            "gm": "grams",
            "gms": "grams",
            "gram": "grams",

            "box": "boxes",

            "pack": "packs",

            "packet": "packets",

            "case": "cases",

            "carton": "cartons",

            "set": "sets",

            "pair": "pairs",

            "dozen": "dozen",

            "l": "litres",
            "liter": "litres",
            "liters": "litres",
            "litre": "litres",

            "ml": "ml",

            "m": "meters",
            "meter": "meters",
            "metre": "meters"
        }

        return aliases.get(
            normalized,
            value.strip()
        )

    # ============================================================
    # LABEL DETECTION
    # ============================================================

    def looks_like_label(
        self,
        value: str
    ) -> bool:
        """
        Determine whether a line looks like a metadata label.
        """

        normalized = self.normalize_label(
            value
        )

        labels = (
            self.HEADER_TERMS
            | self.ORDERED_TERMS
            | self.DELIVERED_TERMS
            | self.UNIT_TERMS
            | self.STOP_WORDS
            | {
                "vendor",
                "supplier",
                "from",
                "to",
                "deliver to",
                "receiving company",
                "recipient",
                "consignee",
                "delivery date",
                "date delivered",
                "reference",
                "delivery note",
                "delivery note number"
            }
        )

        return normalized in labels

    # ============================================================
    # TABLE HEADER DETECTION
    # ============================================================

    def find_items_header(
        self,
        lines: List[str]
    ) -> Optional[int]:
        """
        Locate the beginning of the delivery item table.

        Supports headers such as:

        Item
        Ordered Qty
        Delivered Qty
        Unit

        Description
        Requested
        Received
        UOM

        Product | Qty | Received | Unit
        """

        for index, line in enumerate(lines):

            normalized = self.normalize_label(
                line
            )

            # ----------------------------------------------------
            # Single-line table header.
            # ----------------------------------------------------

            if (
                self.contains_any(
                    normalized,
                    self.HEADER_TERMS
                )
                and
                self.contains_any(
                    normalized,
                    self.ORDERED_TERMS
                )
                and
                self.contains_any(
                    normalized,
                    self.DELIVERED_TERMS
                )
            ):
                return index

            # ----------------------------------------------------
            # Multi-line header.
            # ----------------------------------------------------

            if normalized in self.HEADER_TERMS:

                nearby = " ".join(
                    self.normalize_label(
                        x
                    )
                    for x in lines[
                        index + 1:index + 5
                    ]
                )

                if (
                    self.contains_any(
                        nearby,
                        self.ORDERED_TERMS
                    )
                    and
                    self.contains_any(
                        nearby,
                        self.DELIVERED_TERMS
                    )
                ):
                    return index

        return None

    def contains_any(
        self,
        text: str,
        values: set
    ) -> bool:
        """
        Check whether text contains any configured term.
        """

        return any(
            value in text
            for value in values
        )

    # ============================================================
    # MULTI-LINE ITEMS
    # ============================================================

    def extract_multiline_items(
        self,
        lines: List[str],
        start_index: int
    ) -> List[DeliveryItem]:
        """
        Extract vertically structured OCR/PDF tables.

        Example:

        Laptop
        10
        10
        pieces

        Keyboard
        20
        18
        pieces
        """

        items = []

        index = start_index + 1

        while index < len(lines):

            # ----------------------------------------------------
            # Stop at metadata/footer sections.
            # ----------------------------------------------------

            if self.is_stop_line(
                lines[index]
            ):
                break

            # ----------------------------------------------------
            # Skip secondary header rows.
            # ----------------------------------------------------

            if self.looks_like_label(
                lines[index]
            ):
                index += 1
                continue

            if index + 3 >= len(lines):
                break

            description = lines[index]

            ordered_text = lines[index + 1]
            delivered_text = lines[index + 2]
            unit_text = lines[index + 3]

            ordered_quantity = (
                self.clean_number(
                    ordered_text
                )
            )

            delivered_quantity = (
                self.clean_number(
                    delivered_text
                )
            )

            # ----------------------------------------------------
            # Valid item structure.
            # ----------------------------------------------------

            if (
                ordered_quantity is not None
                and delivered_quantity is not None
                and self.is_unit(unit_text)
            ):

                if (
                    description
                    and not self.looks_like_label(
                        description
                    )
                ):

                    items.append(
                        DeliveryItem(
                            description=description,
                            ordered_quantity=ordered_quantity,
                            delivered_quantity=delivered_quantity,
                            unit=self.normalize_unit(
                                unit_text
                            )
                        )
                    )

                    index += 4
                    continue

            # ----------------------------------------------------
            # If current alignment failed, move one line forward.
            # This is important for OCR where extra lines may
            # appear inside the table.
            # ----------------------------------------------------

            index += 1

        return items

    # ============================================================
    # SINGLE-LINE / PIPE / TABULAR ITEMS
    # ============================================================

    def extract_inline_items(
        self,
        lines: List[str],
        start_index: int
    ) -> List[DeliveryItem]:
        """
        Extract rows such as:

        Laptop | 10 | 10 | pcs
        Keyboard 20 18 pieces
        """

        items = []

        for line in lines[start_index + 1:]:

            if self.is_stop_line(line):
                break

            # ----------------------------------------------------
            # Pipe / comma-separated table.
            # ----------------------------------------------------

            if "|" in line:

                parts = [
                    part.strip()
                    for part in line.split("|")
                    if part.strip()
                ]

            elif "\t" in line:

                parts = [
                    part.strip()
                    for part in line.split("\t")
                    if part.strip()
                ]

            else:

                parts = self.split_item_line(
                    line
                )

            if len(parts) < 3:
                continue

            description = parts[0]

            ordered_quantity = (
                self.clean_number(parts[1])
            )

            delivered_quantity = (
                self.clean_number(parts[2])
            )

            unit = parts[3] or None if len(parts) >= 4 else None

            if (
                not description
                or ordered_quantity is None
                or delivered_quantity is None
                or (unit is not None and not self.is_unit(unit))
            ):
                continue

            if self.looks_like_label(
                description
            ):
                continue

            items.append(
                DeliveryItem(
                    description=description,
                    ordered_quantity=ordered_quantity,
                    delivered_quantity=delivered_quantity,
                    unit=(
                        self.normalize_unit(unit)
                        if unit is not None
                        else None
                    )
                )
            )

        return items

    def split_item_line(
        self,
        line: str
    ) -> List[str]:
        """
        Split a compact OCR row.

        Example:

            Laptop 10 10 pieces

        Result:

            ["Laptop", "10", "10", "pieces"]
        """

        pattern = re.compile(
            rf"^(.+?)\s+"
            rf"({self.NUMBER_PATTERN})\s+"
            rf"({self.NUMBER_PATTERN})"
            rf"(?:\s+([A-Za-z]+\.?))?$",
            re.IGNORECASE
        )

        match = pattern.match(
            line.strip()
        )

        if not match:
            return []

        return [
            match.group(1).strip(),
            match.group(2).strip(),
            match.group(3).strip(),
            (match.group(4) or "").strip()
        ]

    # ============================================================
    # ITEM EXTRACTION
    # ============================================================

    def extract_items(
        self,
        text: str
    ) -> List[DeliveryItem]:
        """
        Main item extraction pipeline.

        Strategy:
            1. Find table header.
            2. Try multi-line extraction.
            3. Try inline extraction.
            4. Return best available result.
        """

        lines = self.get_lines(text)

        if not lines:
            return []

        header_index = self.find_items_header(
            lines
        )

        if header_index is None:
            return []

        # --------------------------------------------------------
        # Multi-line structure.
        # --------------------------------------------------------

        multiline_items = (
            self.extract_multiline_items(
                lines,
                header_index
            )
        )

        if multiline_items:
            return multiline_items

        # --------------------------------------------------------
        # Inline/tabular structure.
        # --------------------------------------------------------

        inline_items = (
            self.extract_inline_items(
                lines,
                header_index
            )
        )

        return inline_items

    # ============================================================
    # STOP CONDITIONS
    # ============================================================

    def is_stop_line(
        self,
        line: str
    ) -> bool:
        """
        Detect footer/status sections.
        """

        normalized = self.normalize_label(
            line
        )

        if normalized in self.STOP_WORDS:
            return True

        for word in self.STOP_WORDS:

            if normalized.startswith(
                word + ":"
            ):
                return True

            if normalized.startswith(
                word + " "
            ):
                return True

        return False

    # ============================================================
    # STATUS INFERENCE FROM QUANTITIES
    # ============================================================

    def infer_status_from_items(
        self,
        items: List[DeliveryItem]
    ) -> Optional[str]:
        """
        Infer delivery status when no explicit status exists.

        Rules:
            delivered == ordered -> DELIVERED
            delivered < ordered  -> PARTIAL
            delivered > ordered  -> OVERDELIVERED
        """

        if not items:
            return None

        has_partial = False
        has_overdelivery = False

        for item in items:

            if (
                item.delivered_quantity
                < item.ordered_quantity
            ):
                has_partial = True

            elif (
                item.delivered_quantity
                > item.ordered_quantity
            ):
                has_overdelivery = True

        if has_partial:
            return "PARTIAL"

        if has_overdelivery:
            return "OVERDELIVERED"

        return "DELIVERED"

    # ============================================================
    # MAIN EXTRACTION
    # ============================================================

    def extract(
        self,
        text: str
    ) -> DeliveryNote:
        """
        Extract structured delivery note data.

        This method preserves the original interface so
        the rest of the application does not need modification.
        """

        text = self.normalize_text(
            text
        )

        # --------------------------------------------------------
        # Metadata
        # --------------------------------------------------------

        delivery_note_number = (
            self.extract_delivery_note_number(
                text
            )
        )

        vendor_name = (
            self.extract_vendor_name(
                text
            )
        )

        delivery_date = (
            self.extract_delivery_date(
                text
            )
        )

        recipient_name = (
            self.extract_recipient_name(
                text
            )
        )

        recipient_address = (
            self.extract_recipient_address(
                text
            )
        )

        # --------------------------------------------------------
        # Items
        # --------------------------------------------------------

        items = self.extract_items(
            text
        )

        # --------------------------------------------------------
        # Explicit status first.
        # --------------------------------------------------------

        delivery_status = (
            self.extract_delivery_status(
                text
            )
        )

        # --------------------------------------------------------
        # Infer status only if explicit status is unavailable.
        # --------------------------------------------------------

        if not delivery_status:

            delivery_status = (
                self.infer_status_from_items(
                    items
                )
            )

        # --------------------------------------------------------
        # Recipient object.
        # --------------------------------------------------------

        recipient = None

        if (
            recipient_name
            or recipient_address
        ):

            recipient = Recipient(
                name=recipient_name,
                address=recipient_address
            )

        # --------------------------------------------------------
        # Final structured response.
        # --------------------------------------------------------

        return DeliveryNote(
            delivery_note_number=(
                delivery_note_number
            ),
            vendor_name=vendor_name,
            delivery_date=delivery_date,
            recipient=recipient,
            items=items,
            delivery_status=delivery_status
        )