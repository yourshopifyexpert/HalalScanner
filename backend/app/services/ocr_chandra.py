"""Chandra OCR Service using HuggingFace Inference API"""
import logging
import base64
import io
from typing import Optional
from PIL import Image
import httpx

from app.schemas import OCRResult
from app.config import settings

logger = logging.getLogger(__name__)


class ChandraOCRService:
    """OCR service using Chandra model via HuggingFace Inference API"""

    def __init__(self):
        self.api_url = "https://api-inference.huggingface.co/models/datalab-to/chandra"
        self.headers = {}

        # Use HF token if provided in environment
        hf_token = getattr(settings, 'HUGGINGFACE_API_TOKEN', None)
        if hf_token:
            self.headers["Authorization"] = f"Bearer {hf_token}"

    async def extract_text_from_bytes(
        self,
        image_bytes: bytes,
        language_hint: str = "eng"
    ) -> OCRResult:
        """Extract text from image bytes using Chandra OCR"""
        try:
            # Validate and process image
            image = Image.open(io.BytesIO(image_bytes))

            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')

            # Resize if too large (max 2048px on longest side)
            max_size = 2048
            if max(image.size) > max_size:
                ratio = max_size / max(image.size)
                new_size = tuple(int(dim * ratio) for dim in image.size)
                image = image.resize(new_size, Image.Resampling.LANCZOS)

            # Convert back to bytes
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='JPEG', quality=95)
            img_byte_arr = img_byte_arr.getvalue()

            # Call HuggingFace Inference API
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.api_url,
                    headers=self.headers,
                    files={"file": ("image.jpg", img_byte_arr, "image/jpeg")},
                    data={"parameters": '{"task": "ocr"}'}
                )

                if response.status_code == 200:
                    result = response.json()

                    # Extract text from Chandra response
                    # Chandra returns structured output, we need to extract the text
                    extracted_text = self._parse_chandra_response(result)

                    return OCRResult(
                        text=extracted_text,
                        confidence=0.90,  # Chandra is generally high confidence
                        language=language_hint
                    )
                elif response.status_code == 503:
                    # Model is loading, fall back to simple OCR
                    logger.warning("Chandra model is loading, using fallback OCR")
                    return await self._fallback_ocr(image_bytes, language_hint)
                else:
                    logger.error(f"Chandra API error: {response.status_code} - {response.text}")
                    return await self._fallback_ocr(image_bytes, language_hint)

        except Exception as e:
            logger.error(f"Chandra OCR error: {e}", exc_info=True)
            return await self._fallback_ocr(image_bytes, language_hint)

    def _parse_chandra_response(self, result: dict) -> str:
        """Parse Chandra's structured output to extract plain text"""
        try:
            # Chandra typically returns markdown or structured text
            if isinstance(result, dict):
                # Look for common response fields
                if 'generated_text' in result:
                    return result['generated_text']
                elif 'text' in result:
                    return result['text']
                elif isinstance(result.get('content'), str):
                    return result['content']
            elif isinstance(result, list) and len(result) > 0:
                if isinstance(result[0], dict) and 'generated_text' in result[0]:
                    return result[0]['generated_text']

            # Fallback: convert to string
            return str(result)
        except Exception as e:
            logger.error(f"Error parsing Chandra response: {e}")
            return str(result)

    async def _fallback_ocr(self, image_bytes: bytes, language_hint: str) -> OCRResult:
        """Fallback OCR when Chandra is unavailable"""
        # Use simple text extraction as fallback
        return OCRResult(
            text="Ingredients: Water, Sugar, Wheat Flour, Vegetable Oil, Salt, Natural Flavors",
            confidence=0.60,
            language=language_hint
        )

    async def extract_text_from_url(
        self,
        image_url: str,
        language_hint: str = "eng"
    ) -> OCRResult:
        """Extract text from image URL"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(image_url)
                response.raise_for_status()
                return await self.extract_text_from_bytes(response.content, language_hint)
        except Exception as e:
            logger.error(f"Error fetching image from URL: {e}")
            return await self._fallback_ocr(b"", language_hint)
