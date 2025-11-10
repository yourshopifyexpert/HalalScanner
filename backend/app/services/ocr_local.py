"""Local Chandra OCR Service using HuggingFace transformers"""
import logging
import io
from typing import Optional
from PIL import Image
import torch
from transformers import AutoProcessor, AutoModelForVision2Seq

from app.schemas import OCRResult

logger = logging.getLogger(__name__)


class LocalChandraOCR:
    """Local Chandra OCR using transformers (no API calls)"""

    def __init__(self):
        self.model = None
        self.processor = None
        self.model_name = "datalab-to/chandra"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"LocalChandraOCR initialized, device: {self.device}")

    def _load_model(self):
        """Lazy load model on first use"""
        if self.model is None:
            try:
                logger.info(f"Loading Chandra model: {self.model_name}")
                self.processor = AutoProcessor.from_pretrained(self.model_name)
                self.model = AutoModelForVision2Seq.from_pretrained(
                    self.model_name,
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                    low_cpu_mem_usage=True
                ).to(self.device)
                logger.info("Chandra model loaded successfully!")
            except Exception as e:
                logger.error(f"Failed to load Chandra model: {e}", exc_info=True)
                raise

    async def extract_text_from_bytes(
        self,
        image_bytes: bytes,
        language_hint: str = "eng"
    ) -> OCRResult:
        """Extract text from image bytes using local Chandra model"""
        try:
            # Load model if not already loaded
            if self.model is None:
                self._load_model()

            # Open and process image
            image = Image.open(io.BytesIO(image_bytes))
            if image.mode != 'RGB':
                image = image.convert('RGB')

            # Resize if too large
            max_size = 1024
            if max(image.size) > max_size:
                ratio = max_size / max(image.size)
                new_size = tuple(int(dim * ratio) for dim in image.size)
                image = image.resize(new_size, Image.Resampling.LANCZOS)

            logger.info(f"Processing image with Chandra, size: {image.size}")

            # Prepare inputs
            inputs = self.processor(
                images=image,
                return_tensors="pt"
            ).to(self.device)

            # Generate OCR output
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=512,
                    do_sample=False
                )

            # Decode output
            extracted_text = self.processor.batch_decode(
                outputs,
                skip_special_tokens=True
            )[0]

            logger.info(f"Chandra extracted {len(extracted_text)} characters")

            return OCRResult(
                text=extracted_text.strip(),
                confidence=0.90,
                language=language_hint
            )

        except Exception as e:
            logger.error(f"Chandra OCR error: {e}", exc_info=True)
            # Fallback to demo text
            return OCRResult(
                text="Ingredients: Unable to process image with local OCR. Please enter ingredients manually.",
                confidence=0.0,
                language=language_hint
            )

    async def extract_text_from_url(
        self,
        image_url: str,
        language_hint: str = "eng"
    ) -> OCRResult:
        """Extract text from image URL"""
        import httpx
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(image_url)
                response.raise_for_status()
                return await self.extract_text_from_bytes(response.content, language_hint)
        except Exception as e:
            logger.error(f"Error fetching image from URL: {e}")
            return OCRResult(
                text="Failed to fetch image from URL",
                confidence=0.0,
                language=language_hint
            )
