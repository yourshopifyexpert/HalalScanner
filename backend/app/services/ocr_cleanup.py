"""Smart rule-based OCR text cleanup service"""
import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)


class OCRCleanupService:
    """Smart rule-based OCR error correction (no external APIs needed)"""

    def __init__(self):
        # Common OCR misreads
        self.common_corrections = {
            # Single character misreads
            r'\bA\s+SUGAR\b': 'SALT, SUGAR',
            r'\bA\s+BAKING\b': 'SALT, BAKING',
            r'\b0\s+': 'O ',  # Zero as O
            r'\b1\s+': 'I ',  # One as I
            r'\bRIGE\b': 'RICE',
            r'\bSOYBEAN\s+01LS\b': 'SOYBEAN OILS',
            r'\bFLOUR\b': 'FLOUR',

            # Common ingredient typos
            r'\bINTERESTERIFI[EÉ]D\b': 'INTERESTERIFIED',
            r'\bHYDR0GENATED\b': 'HYDROGENATED',
            r'\bS0DIUM\b': 'SODIUM',
            r'\bCALGIUM\b': 'CALCIUM',
            r'\bPR0PIONATE\b': 'PROPIONATE',
            r'\bS0RBIC\b': 'SORBIC',
            r'\bM0N0GLYCERIDES\b': 'MONOGLYCERIDES',
            r'\bDIGLYGERIDES\b': 'DIGLYCERIDES',
            r'\bTHIAMINE\s+M0N0NITRATE\b': 'THIAMINE MONONITRATE',
        }

    async def cleanup_ocr_text(self, raw_ocr_text: str) -> str:
        """
        Smart rule-based OCR cleanup - 100% free, no APIs needed

        Fixes:
        - Common character misreads (0→O, 1→I, A→SALT)
        - Missing/unbalanced parentheses
        - Missing commas between ingredients
        - Spacing issues
        """
        text = raw_ocr_text

        try:
            logger.info("Starting rule-based OCR cleanup")

            # Step 1: Fix common character substitutions
            for pattern, replacement in self.common_corrections.items():
                text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

            # Step 2: Fix unbalanced parentheses
            text = self._fix_parentheses(text)

            # Step 3: Fix missing commas (e.g., "ACID WATER" → "ACID, WATER")
            text = self._fix_missing_commas(text)

            # Step 4: Clean up spacing
            text = re.sub(r'\s+', ' ', text).strip()

            logger.info(f"OCR cleanup complete: {len(raw_ocr_text)} → {len(text)} chars")
            return text

        except Exception as e:
            logger.error(f"OCR cleanup failed: {e}")
            return raw_ocr_text

    def _fix_parentheses(self, text: str) -> str:
        """Fix unbalanced parentheses by detecting ingredient boundaries"""
        open_count = text.count('(')
        close_count = text.count(')')

        if open_count == close_count:
            return text

        if open_count > close_count:
            # Missing closing parens - find logical places to add them
            # Look for patterns like "ACID, WATER" or "ACID), CONTAINS"
            missing = open_count - close_count

            # Strategy: Add ) before ", WATER" or ", VEGETABLE" etc.
            patterns = [
                (r'(ACID|IRON|RIBOFLAVIN|NIACIN),\s+(WATER|VEGETABLE|SALT)', r'\1),\2'),
            ]

            for pattern, replacement in patterns:
                if missing > 0:
                    new_text = re.sub(pattern, replacement, text, count=missing, flags=re.IGNORECASE)
                    if new_text != text:
                        text = new_text
                        missing = text.count('(') - text.count(')')

            # If still missing, add at end
            if missing > 0:
                text = text + (')' * missing)
                logger.info(f"Added {missing} closing parentheses")

        return text

    def _fix_missing_commas(self, text: str) -> str:
        """Add missing commas between ingredients"""
        # Pattern: "WORD WORD, CAPITALIZED_WORD" → "WORD WORD, CAPITALIZED_WORD"
        # Look for patterns like "ACID WATER" → "ACID, WATER"

        # Common ingredient starts that should have comma before them
        ingredient_starts = [
            'WATER', 'SALT', 'SUGAR', 'VEGETABLE', 'FLOUR', 'OIL',
            'VITAMIN', 'CALCIUM', 'SODIUM', 'POTASSIUM', 'IRON'
        ]

        for ing_start in ingredient_starts:
            # Pattern: "SOME_WORD INGREDIENT_START" → "SOME_WORD, INGREDIENT_START"
            # But not inside parentheses
            pattern = r'([A-Z]{3,})\s+(' + ing_start + r'\b)'
            text = re.sub(pattern, r'\1, \2', text)

        return text
