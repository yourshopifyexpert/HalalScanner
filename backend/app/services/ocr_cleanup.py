"""AI-powered OCR text cleanup service"""
import logging
import httpx
import os
from typing import Optional

logger = logging.getLogger(__name__)


class OCRCleanupService:
    """Use AI to clean up OCR errors in ingredient text"""

    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.timeout = 15.0

    async def cleanup_ocr_text(self, raw_ocr_text: str) -> str:
        """
        Use AI to clean up OCR errors and format ingredient text properly

        Fixes:
        - Missing or unbalanced parentheses
        - OCR character errors (A → SALT, etc.)
        - Missing commas
        - Spacing issues
        """
        if not self.api_key:
            logger.warning("No AI API key found - skipping AI cleanup")
            return raw_ocr_text

        try:
            # Use Anthropic Claude API if available
            if os.getenv("ANTHROPIC_API_KEY"):
                return await self._cleanup_with_claude(raw_ocr_text)
            elif os.getenv("OPENAI_API_KEY"):
                return await self._cleanup_with_openai(raw_ocr_text)
            else:
                return raw_ocr_text

        except Exception as e:
            logger.error(f"AI OCR cleanup failed: {e}")
            return raw_ocr_text  # Return original on error

    async def _cleanup_with_claude(self, text: str) -> str:
        """Clean up OCR text using Claude API"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": os.getenv("ANTHROPIC_API_KEY"),
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json"
                    },
                    json={
                        "model": "claude-3-haiku-20240307",
                        "max_tokens": 1024,
                        "messages": [{
                            "role": "user",
                            "content": f"""Fix OCR errors in this ingredient list. Common errors:
- "A " might be "SALT, "
- Missing closing parentheses
- Missing commas between ingredients
- Typos in ingredient names

Return ONLY the corrected ingredient text, nothing else.

OCR Text:
{text}

Corrected text:"""
                        }]
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    cleaned = data["content"][0]["text"].strip()
                    logger.info(f"Claude cleaned OCR text: {len(text)} → {len(cleaned)} chars")
                    return cleaned
                else:
                    logger.error(f"Claude API error: {response.status_code}")
                    return text

        except Exception as e:
            logger.error(f"Claude cleanup error: {e}")
            return text

    async def _cleanup_with_openai(self, text: str) -> str:
        """Clean up OCR text using OpenAI API"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-3.5-turbo",
                        "messages": [{
                            "role": "user",
                            "content": f"""Fix OCR errors in this ingredient list. Common errors:
- "A " might be "SALT, "
- Missing closing parentheses
- Missing commas between ingredients
- Typos in ingredient names

Return ONLY the corrected ingredient text, nothing else.

OCR Text:
{text}

Corrected text:"""
                        }],
                        "temperature": 0.1,
                        "max_tokens": 500
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    cleaned = data["choices"][0]["message"]["content"].strip()
                    logger.info(f"OpenAI cleaned OCR text: {len(text)} → {len(cleaned)} chars")
                    return cleaned
                else:
                    logger.error(f"OpenAI API error: {response.status_code}")
                    return text

        except Exception as e:
            logger.error(f"OpenAI cleanup error: {e}")
            return text
