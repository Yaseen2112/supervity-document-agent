import re
from typing import Dict, List, Tuple


class DocumentClassifier:

    KEYWORDS = {
        "invoice": {
            "strong": [
                "invoice",
                "commercial bill",
                "tax invoice",
                "bill no",
                "bill number",
                "invoice number",
                "invoice no",
                "invoice id",
                "bill to",
                "amount payable",
                "grand total",
                "net amount",
                "total amount",
                "subtotal",
                "tax",
                "vat"
            ],
            "medium": [
                "due date",
                "billing date",
                "payment due",
                "unit price",
                "rate",
                "quantity",
                "amount",
                "currency",
                "balance due"
            ]
        },

        "delivery_note": {
            "strong": [
                "delivery note",
                "delivery note number",
                "goods delivery",
                "goods delivery record",
                "goods receipt",
                "goods received",
                "grn",
                "deliver to",
                "delivery status"
            ],
            "medium": [
                "delivered quantity",
                "ordered quantity",
                "received",
                "requested",
                "supplier",
                "date delivered",
                "receiving company"
            ]
        },

        "contract": {
            "strong": [
                "contract",
                "agreement",
                "memorandum",
                "contract id",
                "agreement number",
                "reference code",
                "commercial terms"
            ],
            "medium": [
                "effective date",
                "expiry date",
                "termination",
                "payment terms",
                "parties",
                "party one",
                "party two",
                "obligations",
                "responsibilities"
            ]
        }
    }

    def normalize_text(self, text: str) -> str:
        """
        Normalize text before classification.
        """

        text = text.lower()

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.strip()

    def calculate_score(
        self,
        text: str,
        keywords: Dict[str, List[str]]
    ) -> Tuple[float, List[str]]:

        score = 0.0

        matched_keywords = []

        for keyword in keywords["strong"]:

            if keyword in text:

                score += 3.0

                matched_keywords.append(keyword)

        for keyword in keywords["medium"]:

            if keyword in text:

                score += 1.0

                matched_keywords.append(keyword)

        return score, matched_keywords

    def classify(
        self,
        text: str
    ) -> Dict:

        normalized_text = self.normalize_text(text)

        if not normalized_text:

            return {
                "document_type": "unknown",
                "confidence": 0.0,
                "matched_keywords": [],
                "scores": {}
            }

        scores = {}
        matches = {}

        for document_type, keywords in self.KEYWORDS.items():

            score, matched_keywords = self.calculate_score(
                normalized_text,
                keywords
            )

            scores[document_type] = score
            matches[document_type] = matched_keywords

        best_type = max(
            scores,
            key=scores.get
        )

        best_score = scores[best_type]

        # No evidence found
        if best_score == 0:

            return {
                "document_type": "unknown",
                "confidence": 0.0,
                "matched_keywords": [],
                "scores": scores
            }

        # ---------------------------------------
        # 1. RELATIVE CONFIDENCE
        # ---------------------------------------

        total_score = sum(scores.values())

        relative_confidence = (
            best_score / total_score
            if total_score > 0
            else 0.0
        )

        # ---------------------------------------
        # 2. EVIDENCE CONFIDENCE
        # ---------------------------------------

        evidence_confidence = min(
            best_score / 15.0,
            1.0
        )

        # ---------------------------------------
        # 3. COMBINED CONFIDENCE
        # ---------------------------------------

        confidence = (
            0.6 * relative_confidence
            +
            0.4 * evidence_confidence
        )

        confidence = round(
            min(confidence, 1.0),
            2
        )

        # ---------------------------------------
        # UNKNOWN THRESHOLD
        # ---------------------------------------

        if best_score < 2:

            return {
                "document_type": "unknown",
                "confidence": confidence,
                "matched_keywords": matches[best_type],
                "scores": scores
            }

        return {
            "document_type": best_type,
            "confidence": confidence,
            "matched_keywords": matches[best_type],
            "scores": scores
        }