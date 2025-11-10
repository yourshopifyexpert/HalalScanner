"""Simplified OCR Service for demo (no Tesseract required)"""
import logging
from app.schemas import OCRResult

logger = logging.getLogger(__name__)


class OCRService:
    """Simplified OCR service for demo purposes"""

    async def extract_text_from_bytes(
        self,
        image_bytes: bytes,
        language_hint: str = "eng"
    ) -> OCRResult:
        """Mock OCR extraction for demo"""
        # Return mock ingredient list for demo
        mock_text = """
        Ingredients: Water, Sugar, Wheat Flour, Vegetable Oil, Salt,
        Natural Flavors, Citric Acid, Yeast, Baking Powder
        """

        return OCRResult(
            text=mock_text.strip(),
            confidence=0.85,
            language=language_hint
        )

    async def extract_text_from_url(
        self,
        image_url: str,
        language_hint: str = "eng"
    ) -> OCRResult:
        """Mock OCR from URL"""
        return await self.extract_text_from_bytes(b"", language_hint)
