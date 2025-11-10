"""Ingredient Normalizer Service"""
import re
import logging
from typing import List, Dict, Set
from sqlalchemy.orm import Session
import spacy

from app.schemas import NormalizedIngredient
from app.models import IngredientMaster

logger = logging.getLogger(__name__)


class IngredientNormalizer:
    """
    Parses raw OCR text into normalized ingredient tokens

    Steps:
    1. Split text into ingredient tokens
    2. Clean and normalize tokens
    3. Expand abbreviations
    4. Map to canonical ingredient names
    """

    def __init__(self, db: Session):
        self.db = db
        # Load spaCy model for NLP
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            logger.warning("spaCy model not found, using basic tokenization")
            self.nlp = None

        # Common abbreviations
        self.abbreviations = {
            "artif": "artificial",
            "nat": "natural",
            "flav": "flavor",
            "flavr": "flavor",
            "conc": "concentrate",
            "pres": "preservative",
            "emuls": "emulsifier",
            "stab": "stabilizer",
            "color": "coloring",
            "vit": "vitamin",
            "min": "mineral",
        }

        # Ingredient delimiters
        self.delimiters = [",", ";", "\n", ".", "and"]

    async def normalize(self, text: str) -> List[NormalizedIngredient]:
        """Normalize ingredient text into structured tokens"""
        try:
            # Step 1: Clean text
            cleaned_text = self._clean_text(text)

            # Step 2: Extract ingredients section
            ingredients_text = self._extract_ingredients_section(cleaned_text)

            # Step 3: Split into individual ingredients
            ingredient_tokens = self._split_ingredients(ingredients_text)

            # Step 4: Normalize each token
            normalized = []
            for token in ingredient_tokens:
                if len(token.strip()) < 2:
                    continue

                normalized_token = self._normalize_token(token)
                if normalized_token:
                    normalized.append(normalized_token)

            logger.info(f"Normalized {len(ingredient_tokens)} raw tokens into {len(normalized)} ingredients")
            return normalized

        except Exception as e:
            logger.error(f"Normalization failed: {e}", exc_info=True)
            return []

    def _clean_text(self, text: str) -> str:
        """Clean OCR text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove common OCR artifacts
        text = text.replace('|', 'I')
        text = text.replace('0', 'O')  # Sometimes O is misread as 0

        # Lowercase for processing
        text = text.lower()

        return text.strip()

    def _extract_ingredients_section(self, text: str) -> str:
        """Extract the ingredients section from label text"""
        # Look for "ingredients:" marker
        patterns = [
            r'ingredients?\s*:(.+?)(?:nutrition|allergen|contains|$)',
            r'ingredients?\s*:(.+)',
            r'contains?\s*:(.+?)(?:nutrition|allergen|$)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()

        # If no marker found, assume entire text is ingredients
        return text

    def _split_ingredients(self, text: str) -> List[str]:
        """Split ingredient text into individual tokens"""
        # Split by common delimiters
        tokens = re.split(r'[,;.\n]|\band\b', text)

        # Clean each token
        cleaned_tokens = []
        for token in tokens:
            token = token.strip()

            # Remove parentheticals (we'll handle these separately if needed)
            # But keep the content for context
            if token:
                cleaned_tokens.append(token)

        return cleaned_tokens

    def _normalize_token(self, token: str) -> Optional[NormalizedIngredient]:
        """Normalize a single ingredient token"""
        # Remove extra whitespace
        token = token.strip()

        if not token or len(token) < 2:
            return None

        # Expand abbreviations
        expanded = self._expand_abbreviations(token)

        # Remove quantity indicators
        expanded = re.sub(r'\d+%|\d+\s*mg|\d+\s*g', '', expanded).strip()

        # Remove parentheticals for canonical name
        canonical = re.sub(r'\([^)]*\)', '', expanded).strip()

        # Try to match with master ingredient database
        master_ingredient = self._find_master_ingredient(canonical)

        if master_ingredient:
            canonical = master_ingredient.canonical_name
            aliases = master_ingredient.aliases or []
            confidence = 0.9
        else:
            # New ingredient not in database
            aliases = []
            confidence = 0.6

        return NormalizedIngredient(
            original=token,
            canonical=canonical.upper(),
            aliases=aliases,
            confidence=confidence
        )

    def _expand_abbreviations(self, token: str) -> str:
        """Expand common abbreviations"""
        for abbr, full in self.abbreviations.items():
            token = re.sub(
                r'\b' + abbr + r'\b',
                full,
                token,
                flags=re.IGNORECASE
            )
        return token

    def _find_master_ingredient(self, name: str) -> Optional[IngredientMaster]:
        """Find ingredient in master database by name or alias"""
        # Try exact match first
        ingredient = self.db.query(IngredientMaster).filter(
            IngredientMaster.canonical_name.ilike(name)
        ).first()

        if ingredient:
            return ingredient

        # Try fuzzy match with aliases
        # TODO: Implement better fuzzy matching with Elasticsearch
        ingredients = self.db.query(IngredientMaster).all()
        for ing in ingredients:
            if ing.aliases:
                for alias in ing.aliases:
                    if alias.lower() == name.lower():
                        return ing

        return None
