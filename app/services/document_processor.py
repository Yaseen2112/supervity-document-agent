from pathlib import Path
from typing import Dict, Any, List

import pymupdf
from PIL import Image


SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg"
}


class DocumentProcessor:

    def validate_file(self, file_path: str | Path) -> Path:
        """
        Validate that the file exists and has a supported extension.
        """

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"File not found: {path}"
            )

        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file type: {path.suffix}"
            )

        return path

    def get_file_type(self, file_path: str | Path) -> str:

        path = Path(file_path)

        if path.suffix.lower() == ".pdf":
            return "pdf"

        return "image"

    def extract_text_from_pdf(
        self,
        file_path: str | Path
    ) -> Dict[str, Any]:
        """
        Extract embedded text from a PDF.
        """

        path = self.validate_file(file_path)

        document = pymupdf.open(path)

        pages_text: List[str] = []

        for page in document:
            blocks = page.get_text("blocks", sort=True)
            page_text = "\n".join(
                block[4].strip()
                for block in blocks
                if block[4].strip()
            )
            pages_text.append(page_text)

        document.close()

        full_text = "\n".join(pages_text).strip()

        return {
            "text": full_text,
            "page_count": len(pages_text),
            "has_embedded_text": bool(full_text)
        }

    def pdf_to_images(
        self,
        file_path: str | Path,
        zoom: float = 2.0
    ) -> List[Image.Image]:
        """
        Convert each PDF page into a PIL image.
        """

        path = self.validate_file(file_path)

        document = pymupdf.open(path)

        images = []

        matrix = pymupdf.Matrix(zoom, zoom)

        for page in document:

            pixmap = page.get_pixmap(
                matrix=matrix
            )

            mode = "RGB"

            image = Image.frombytes(
                mode,
                [pixmap.width, pixmap.height],
                pixmap.samples
            )

            images.append(image)

        document.close()

        return images

    def load_image(
        self,
        file_path: str | Path
    ) -> Image.Image:
        """
        Load an image document.
        """

        path = self.validate_file(file_path)

        image = Image.open(path)

        return image.convert("RGB")

    def process_document(
        self,
        file_path: str | Path
    ) -> Dict[str, Any]:
        """
        Main document ingestion method.
        """

        path = self.validate_file(file_path)

        file_type = self.get_file_type(path)

        result = {
            "filename": path.name,
            "file_path": str(path),
            "file_type": file_type,
            "text": "",
            "page_count": 1,
            "requires_ocr": False,
            "images": []
        }

        # -------------------------
        # PDF PROCESSING
        # -------------------------

        if file_type == "pdf":

            pdf_result = self.extract_text_from_pdf(
                path
            )

            result["text"] = pdf_result["text"]
            result["page_count"] = pdf_result["page_count"]

            # Sparse text layers are common in designed PDFs. They often
            # contain only a title or hidden accessibility text, so OCR the
            # rendered page instead of returning incomplete extraction data.
            words_per_page = len(result["text"].split()) / max(
                result["page_count"], 1
            )
            if (
                not pdf_result["has_embedded_text"]
                or words_per_page < 8
                or len(result["text"]) < 40
            ):

                result["requires_ocr"] = True

                result["images"] = self.pdf_to_images(
                    path
                )

        # -------------------------
        # IMAGE PROCESSING
        # -------------------------

        else:

            image = self.load_image(path)

            result["requires_ocr"] = True

            result["images"] = [image]

        return result