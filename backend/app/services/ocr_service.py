"""OCR Service for text extraction from images"""
import logging
from typing import Optional
import io
from PIL import Image
import pytesseract
import cv2
import numpy as np
import httpx

from app.schemas import OCRResult
from app.config import settings

logger = logging.getLogger(__name__)


class OCRService:
    """OCR service for extracting text from product labels"""

    def __init__(self):
        if settings.TESSERACT_CMD:
            pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD

    async def extract_text_from_bytes(
        self,
        image_bytes: bytes,
        language_hint: str = "eng"
    ) -> OCRResult:
        """Extract text from image bytes using Tesseract OCR"""
        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_bytes))

            # Preprocess image
            processed_image = self._preprocess_image(image)

            # Perform OCR
            lang_code = self._get_tesseract_lang(language_hint)
            text = pytesseract.image_to_string(
                processed_image,
                lang=lang_code,
                config='--psm 6'  # Assume a single uniform block of text
            )

            # Get confidence score
            data = pytesseract.image_to_data(
                processed_image,
                lang=lang_code,
                output_type=pytesseract.Output.DICT
            )

            # Calculate average confidence
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) / 100.0 if confidences else 0.0

            logger.info(f"OCR extracted {len(text)} characters with confidence {avg_confidence:.2f}")

            return OCRResult(
                text=text.strip(),
                confidence=avg_confidence,
                language=language_hint,
                bounding_boxes=None  # TODO: Extract bounding boxes if needed
            )

        except Exception as e:
            logger.error(f"OCR extraction failed: {e}", exc_info=True)
            return OCRResult(
                text="",
                confidence=0.0,
                language=language_hint
            )

    async def extract_text_from_url(
        self,
        image_url: str,
        language_hint: str = "eng"
    ) -> OCRResult:
        """Extract text from image URL"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(image_url, timeout=30.0)
                response.raise_for_status()
                image_bytes = response.content

            return await self.extract_text_from_bytes(image_bytes, language_hint)

        except Exception as e:
            logger.error(f"Failed to fetch image from URL: {e}", exc_info=True)
            return OCRResult(
                text="",
                confidence=0.0,
                language=language_hint
            )

    def _preprocess_image(self, image: Image.Image) -> np.ndarray:
        """Preprocess image for better OCR accuracy"""
        # Convert PIL Image to OpenCV format
        img_array = np.array(image)

        # Convert to grayscale
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array

        # Apply denoising
        denoised = cv2.fastNlMeansDenoising(gray)

        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            denoised,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,
            2
        )

        # Deskew image (basic rotation correction)
        coords = np.column_stack(np.where(thresh > 0))
        if len(coords) > 0:
            angle = cv2.minAreaRect(coords)[-1]
            if angle < -45:
                angle = -(90 + angle)
            else:
                angle = -angle

            # Rotate image if needed
            if abs(angle) > 0.5:
                (h, w) = thresh.shape[:2]
                center = (w // 2, h // 2)
                M = cv2.getRotationMatrix2D(center, angle, 1.0)
                thresh = cv2.warpAffine(
                    thresh,
                    M,
                    (w, h),
                    flags=cv2.INTER_CUBIC,
                    borderMode=cv2.BORDER_REPLICATE
                )

        return thresh

    def _get_tesseract_lang(self, language_hint: str) -> str:
        """Map language hint to Tesseract language code"""
        lang_map = {
            "en": "eng",
            "ar": "ara",
            "ur": "urd",
            "tr": "tur",
            "id": "ind",
            "ms": "msa"
        }
        return lang_map.get(language_hint, "eng")

    async def extract_with_cloud_ocr(
        self,
        image_bytes: bytes,
        provider: str = "google"
    ) -> OCRResult:
        """
        Use cloud OCR service for higher accuracy
        (Placeholder - implement based on chosen provider)
        """
        # TODO: Implement Google Cloud Vision or AWS Textract integration
        logger.warning("Cloud OCR not implemented yet, falling back to Tesseract")
        return await self.extract_text_from_bytes(image_bytes)
