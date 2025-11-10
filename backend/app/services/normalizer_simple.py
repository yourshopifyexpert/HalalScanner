"""Simplified Ingredient Normalizer (no spaCy required)"""
import re
import logging
from typing import List
from sqlalchemy.orm import Session

from app.schemas import NormalizedIngredient
from app.models import IngredientMaster

logger = logging.getLogger(__name__)


class IngredientNormalizer:
    """Simplified ingredient normalizer for demo"""

    def __init__(self, db: Session):
        self.db = db

    async def normalize(self, text: str) -> List[NormalizedIngredient]:
        """Normalize ingredient text into structured tokens"""
        try:
            # Extract ingredients section
            text = text.lower()
            if "ingredients:" in text:
                text = text.split("ingredients:")[1].split("\n")[0]

            # Split by common delimiters
            tokens = re.split(r'[,;.\n]|\band\b', text)

            # Normalize each token
            normalized = []
            for token in tokens:
                token = token.strip()
                if len(token) < 2:
                    continue

                # Remove quantities
                token = re.sub(r'\d+%|\d+\s*mg|\d+\s*g', '', token).strip()

                if token:
                    normalized.append(NormalizedIngredient(
                        original=token,
                        canonical=token.upper().replace(" ", "_"),
                        aliases=[],
                        confidence=0.8
                    ))

            logger.info(f"Normalized {len(normalized)} ingredients")
            return normalized

        except Exception as e:
            logger.error(f"Normalization failed: {e}")
            return []
