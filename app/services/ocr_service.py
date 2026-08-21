from typing import Dict, Any, List

import pytesseract
from pytesseract import Output
from PIL import Image


# Windows Tesseract executable path
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


class OCRService:

    def _extract_with_config(
        self,
        image: Image.Image,
        config: str
    ) -> Dict[str, Any]:
        data = pytesseract.image_to_data(
            image,
            output_type=Output.DICT,
            config=config
        )

        lines: Dict[tuple, List[str]] = {}
        confidences: List[float] = []

        for index, (text, confidence) in enumerate(
            zip(data["text"], data["conf"])
        ):
            text = text.strip()

            if not text:
                continue

            try:
                confidence = float(confidence)
            except ValueError:
                confidence = -1

            if confidence < 0:
                continue

            key = (
                data["block_num"][index],
                data["par_num"][index],
                data["line_num"][index]
            )
            lines.setdefault(key, []).append(text)
            confidences.append(confidence)

        extracted_text = "\n".join(
            " ".join(words)
            for words in lines.values()
        )

        return {
            "text": extracted_text,
            "average_confidence": round(
                sum(confidences) / len(confidences), 2
            ) if confidences else 0.0,
            "word_count": sum(len(words) for words in lines.values()),
            "words": [word for words in lines.values() for word in words]
        }

    def extract_text(
        self,
        image: Image.Image
    ) -> Dict[str, Any]:
        """
        Extract text and word-level confidence scores
        from an image using Tesseract OCR.
        """

        candidates = [
            self._extract_with_config(image, "--oem 3 --psm 6"),
            self._extract_with_config(image, "--oem 3 --psm 11")
        ]
        best_result = max(
            candidates,
            key=lambda candidate: (
                candidate["average_confidence"],
                candidate["word_count"]
            )
        )

        return {
            "text": best_result["text"],
            "average_confidence": best_result["average_confidence"],
            "word_count": best_result["word_count"],
            "words": best_result["words"]
        }

    def extract_text_from_images(
        self,
        images: List[Image.Image]
    ) -> Dict[str, Any]:
        """
        Extract text from multiple pages/images.
        """

        page_results = []

        all_text = []

        for index, image in enumerate(
            images,
            start=1
        ):

            result = self.extract_text(image)

            page_results.append({
                "page": index,
                **result
            })

            all_text.append(result["text"])

        average_confidence = 0.0

        if page_results:
            average_confidence = (
                sum(
                    page["average_confidence"]
                    for page in page_results
                )
                / len(page_results)
            )

        return {
            "text": "\n".join(all_text),
            "average_confidence": round(
                average_confidence,
                2
            ),
            "page_results": page_results
        }