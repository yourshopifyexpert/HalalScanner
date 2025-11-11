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
            # Extract ingredients section from full text
            text_lower = text.lower()

            # Find ingredients section
            if "ingredients:" in text_lower:
                # Extract everything after "INGREDIENTS:"
                start_idx = text_lower.index("ingredients:") + len("ingredients:")
                ingredients_text = text[start_idx:]
            else:
                ingredients_text = text

            # FIRST: Handle "CONTAINS X% OR LESS OF:" pattern (before removing allergen declarations)
            # This flattens: "SALT, CONTAINS 2% OR LESS OF: SUGAR, SPICE"
            # Into: "SALT, SUGAR, SPICE"
            ingredients_text = re.sub(
                r',?\s*contains\s+\d+%?\s+or\s+less\s+of\s*:?\s*',
                ', ',
                ingredients_text,
                flags=re.IGNORECASE
            )

            # THEN: Remove only standalone allergen declarations at the end
            # Match "CONTAINS: WHEAT" or "ALLERGENS: SOY" but NOT "CONTAINS 2% OR LESS OF"
            # Use word boundary and look for standalone "CONTAINS:" without "OR LESS"
            ingredients_text = re.sub(
                r'\.\s*(contains|allergens|allergen information|may contain)\s*:\s*[^\n]*',
                '.',
                ingredients_text,
                flags=re.IGNORECASE
            )

            # Clean up the text
            ingredients_text = ingredients_text.strip()

            # Extract ingredients while respecting parentheses
            tokens = self._split_ingredients(ingredients_text)

            # Normalize each token
            normalized = []
            for token in tokens:
                token = token.strip()
                if len(token) < 2:
                    continue

                # Skip common non-ingredient phrases
                if any(skip in token.lower() for skip in [
                    'ingredients:', 'contains:', 'allergen', 'may contain',
                    'processed in', 'made in', 'manufactured'
                ]):
                    continue

                # Remove parenthetical clarifications but keep main ingredient
                # Example: "FLOUR (WHEAT)" -> "FLOUR"
                main_ingredient = re.sub(r'\s*\([^)]*\)\s*', ' ', token).strip()

                if main_ingredient:
                    normalized.append(NormalizedIngredient(
                        original=main_ingredient,
                        canonical=main_ingredient.upper().replace(" ", "_"),
                        aliases=[],
                        confidence=0.8
                    ))

            logger.info(f"Normalized {len(normalized)} ingredients from text")
            return normalized

        except Exception as e:
            logger.error(f"Normalization failed: {e}")
            return []

    def _balance_parentheses(self, text: str, missing_closes: int) -> str:
        """
        Balance unbalanced parentheses by adding closing parens at logical positions
        Strategy: Look for ingredient boundaries (patterns like "CONTAINS X% OR LESS OF:")
        or add all closing parens at the end to preserve sub-ingredient lists
        """
        # Simple approach: add all missing ) at the end to avoid breaking sub-ingredient lists
        # This preserves structures like "FLOUR (WHEAT, BARLEY)" as a single ingredient
        fixed_text = text + (')' * missing_closes)

        logger.info(f"Fixed unbalanced parentheses: added {missing_closes} closing parens at end")
        return fixed_text

    def _split_ingredients(self, text: str) -> List[str]:
        """
        Split ingredient text by commas while respecting parentheses
        Example: "FLOUR (WHEAT, BARLEY), SALT, SUGAR" -> ["FLOUR (WHEAT, BARLEY)", "SALT", "SUGAR"]

        Handles unbalanced parentheses from OCR errors
        """
        # First, normalize whitespace and remove trailing punctuation
        text = ' '.join(text.split())
        text = text.rstrip('.')

        # Fix unbalanced parentheses (common OCR error)
        open_count = text.count('(')
        close_count = text.count(')')

        if open_count > close_count:
            # Add missing closing parentheses at reasonable positions
            # Strategy: Look for ", " after an unclosed "(" and add ")" before it
            text = self._balance_parentheses(text, open_count - close_count)
        elif close_count > open_count:
            # Remove extra closing parentheses
            text = text.replace(')', '', close_count - open_count)

        ingredients = []
        current = []
        paren_depth = 0

        for char in text:
            if char == '(':
                paren_depth += 1
                current.append(char)
            elif char == ')':
                paren_depth -= 1
                current.append(char)
            elif char == ',' and paren_depth == 0:
                # Found ingredient delimiter outside parentheses
                ingredient = ''.join(current).strip()
                if ingredient:
                    ingredients.append(ingredient)
                current = []
            else:
                current.append(char)

        # Add last ingredient
        ingredient = ''.join(current).strip()
        if ingredient:
            ingredients.append(ingredient)

        # Handle ", AND" as a delimiter and split compound ingredients
        final_ingredients = []
        for ing in ingredients:
            ing = ing.strip()

            # Remove leading "AND " (from ", AND INGREDIENT")
            if ing.lower().startswith('and '):
                ing = ing[4:].strip()

            if not ing:
                continue

            # Smart AND splitting:
            # Split "CALCIUM PROPIONATE AND SORBIC ACID" into two ingredients
            # But keep "VEGETABLE SHORTENING (INTERESTERIFIED AND HYDROGENATED OILS)" together

            # Remove content in parentheses to check for AND outside
            without_parens = re.sub(r'\([^)]*\)', '', ing)

            # Check if there's " AND " in the text without parentheses
            if ' AND ' in without_parens.upper():
                # Find the position of AND in the original string (outside parentheses)
                paren_depth = 0
                and_pos = -1

                for i in range(len(ing) - 4):
                    if ing[i] == '(':
                        paren_depth += 1
                    elif ing[i] == ')':
                        paren_depth -= 1
                    elif paren_depth == 0:
                        # Check if we're at " AND "
                        if ing[i:i+5].upper() == ' AND ':
                            and_pos = i
                            break

                if and_pos > 0:
                    # Split at this position
                    left = ing[:and_pos].strip()
                    right = ing[and_pos+5:].strip()  # +5 for " AND "

                    # Check if both parts are substantive ingredients
                    left_clean = re.sub(r'\([^)]*\)', '', left).strip()
                    right_clean = re.sub(r'\([^)]*\)', '', right).strip()

                    left_words = len(left_clean.split())
                    right_words = len(right_clean.split())

                    standalone_indicators = ['acid', 'salt', 'oil', 'flour', 'sugar', 'starch', 'powder', 'soda', 'propionate']
                    right_lower = right_clean.lower()

                    if (left_words >= 2 and right_words >= 2) or \
                       any(right_lower.endswith(indicator) for indicator in standalone_indicators):
                        # These are likely two separate ingredients
                        final_ingredients.append(left)
                        final_ingredients.append(right)
                    else:
                        # Keep together (e.g., "INTERESTERIFIED AND HYDROGENATED")
                        final_ingredients.append(ing)
                else:
                    final_ingredients.append(ing)
            else:
                # No AND - keep as is
                final_ingredients.append(ing)

        return final_ingredients
