import cv2
import numpy as np
from PIL import Image


class ImagePreprocessor:

    def preprocess(self, image: Image.Image) -> Image.Image:
        """
        Apply preprocessing steps to improve OCR quality.
        """

        # Convert PIL image to NumPy array
        image_np = np.array(image)

        # Convert RGB to grayscale
        if len(image_np.shape) == 3:
            gray = cv2.cvtColor(
                image_np,
                cv2.COLOR_RGB2GRAY
            )
        else:
            gray = image_np

        # Upscale small images
        height, width = gray.shape

        if width < 1500:
            scale = 2
            gray = cv2.resize(
                gray,
                None,
                fx=scale,
                fy=scale,
                interpolation=cv2.INTER_CUBIC
            )

        # Reduce noise
        denoised = cv2.fastNlMeansDenoising(
            gray,
            None,
            h=10,
            templateWindowSize=7,
            searchWindowSize=21
        )

        # Improve local contrast
        clahe = cv2.createCLAHE(
            clipLimit=2.0,
            tileGridSize=(8, 8)
        )

        enhanced = clahe.apply(denoised)

        # Adaptive thresholding
        thresholded = cv2.adaptiveThreshold(
            enhanced,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31,
            11
        )

        # Convert back to PIL Image
        processed_image = Image.fromarray(
            thresholded
        )

        return processed_image