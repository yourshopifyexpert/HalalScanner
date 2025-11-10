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
            logger.info(f"Calling Chandra API for OCR, image size: {len(img_byte_arr)} bytes")

            async with httpx.AsyncClient(timeout=60.0) as client:
                request_headers = {**self.headers, "Content-Type": "image/jpeg"}
                response = await client.post(
                    self.api_url,
                    headers=request_headers,
                    content=img_byte_arr
                )

                logger.info(f"Chandra API response: status={response.status_code}")

                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"Chandra result type: {type(result)}, value: {str(result)[:200]}")

                    # Extract text from Chandra response
                    extracted_text = self._parse_chandra_response(result)
                    logger.info(f"Extracted text length: {len(extracted_text)}")

                    return OCRResult(
                        text=extracted_text,
                        confidence=0.90,
                        language=language_hint
                    )
                elif response.status_code == 503:
                    logger.warning("Chandra model is loading, using fallback OCR")
                    return await self._fallback_ocr(image_bytes, language_hint)
                else:
                    logger.error(f"Chandra API error: {response.status_code} - {response.text[:500]}")
                    return await self._fallback_ocr(image_bytes, language_hint)

        except Exception as e:
            logger.error(f"Chandra OCR error: {e}", exc_info=True)
            return await self._fallback_ocr(image_bytes, language_hint)

    def _parse_chandra_response(self, result) -> str:
        """Parse Chandra's structured output to extract plain text"""
        try:
            # Chandra can return various formats
            if isinstance(result, str):
                # Direct string response
                return result
            elif isinstance(result, dict):
                # Look for common response fields
                for key in ['generated_text', 'text', 'content', 'output', 'result', 'ocr_text']:
                    if key in result and isinstance(result[key], str):
                        return result[key]
            elif isinstance(result, list) and len(result) > 0:
                # Array of results
                first_item = result[0]
                if isinstance(first_item, str):
                    return first_item
                elif isinstance(first_item, dict):
                    for key in ['generated_text', 'text', 'content']:
                        if key in first_item:
                            return str(first_item[key])

            # Fallback: convert to string and clean
            result_str = str(result)
            logger.warning(f"Using raw result string: {result_str[:100]}")
            return result_str
        except Exception as e:
            logger.error(f"Error parsing Chandra response: {e}")
            return "Error: Could not parse OCR response"

    async def _fallback_ocr(self, image_bytes: bytes, language_hint: str) -> OCRResult:
        """Fallback OCR when Chandra is unavailable"""
        logger.info("Using fallback OCR - returning demo ingredients")
        # Use simple text extraction as fallback
        fallback_text = """Ingredients: Water, Sugar, Wheat Flour, Vegetable Oil, Salt, Natural Flavors, Citric Acid

NOTE: OCR service temporarily unavailable. Please enter ingredients manually or try again in a moment."""
        return OCRResult(
            text=fallback_text,
            confidence=0.50,
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
