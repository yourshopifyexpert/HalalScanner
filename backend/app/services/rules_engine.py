"""Rules Engine for ingredient classification"""
import re
import logging
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session

from app.schemas import VerdictLabel, HalalStatus, IngredientEvidence, NormalizedIngredient
from app.models import RuleDefinition, IngredientMaster

logger = logging.getLogger(__name__)


class RulesEngine:
    """
    Deterministic rules engine for ingredient classification

    Priority order:
    1. Explicit blacklist (HARAM) - highest priority
    2. Certification override
    3. Explicit whitelist (HALAL)
    4. Pattern matching
    5. Ambiguous/Unknown
    """

    def __init__(self, db: Session):
        self.db = db
        self._load_rules()
        self._init_blacklist()
        self._init_whitelist()

    def _load_rules(self):
        """Load active rules from database"""
        self.rules = self.db.query(RuleDefinition).filter(
            RuleDefinition.active == True
        ).order_by(RuleDefinition.priority.desc()).all()

        logger.info(f"Loaded {len(self.rules)} active rules")

    def _init_blacklist(self):
        """Initialize haram blacklist"""
        self.haram_keywords = {
            # Pork and derivatives
            "pork", "pig", "swine", "lard", "bacon", "ham", "pepperoni",
            "pork gelatin", "pork fat", "pork enzymes",

            # Alcohol
            "alcohol", "ethanol", "ethyl alcohol", "wine", "beer", "rum",
            "vodka", "whiskey", "liqueur",

            # Non-halal animal derivatives
            "gelatin",  # Unless specified as beef/fish
            "glycerin",  # Ambiguous
            "mono and diglycerides",  # Ambiguous
            "shortening",  # May contain lard

            # Other haram
            "blood", "plasma",
            "l-cysteine",  # Often from human hair or feathers
            "carmine", "cochineal",  # Insect-derived
        }

    def _init_whitelist(self):
        """Initialize halal whitelist (plant-based, clearly halal)"""
        self.halal_keywords = {
            # Common halal ingredients
            "water", "sugar", "salt", "flour", "wheat", "rice", "corn",
            "soy", "soybean", "vegetable oil", "palm oil", "coconut oil",
            "sunflower oil", "olive oil", "canola oil",

            # Fruits and vegetables
            "tomato", "potato", "onion", "garlic", "lemon", "apple",
            "orange", "banana", "strawberry", "blueberry",

            # Grains and legumes
            "oat", "barley", "chickpea", "lentil", "bean",

            # Spices and herbs
            "pepper", "cinnamon", "cumin", "oregano", "basil", "thyme",
            "turmeric", "ginger", "mint", "vanilla",

            # Common additives (plant-based)
            "citric acid", "ascorbic acid", "baking soda", "baking powder",
            "yeast", "vinegar",
        }

    def classify_ingredient(
        self,
        ingredient: NormalizedIngredient
    ) -> IngredientEvidence:
        """Classify a single ingredient using rules"""

        canonical = ingredient.canonical.lower()
        original = ingredient.original.lower()

        # Check database first
        master_ing = self.db.query(IngredientMaster).filter(
            IngredientMaster.canonical_name.ilike(canonical)
        ).first()

        if master_ing and master_ing.halal_status != HalalStatus.UNKNOWN:
            return IngredientEvidence(
                ingredient=ingredient.original,
                normalized_name=ingredient.canonical,
                status=master_ing.halal_status,
                reason=master_ing.notes or "Known ingredient status",
                rule_name="DATABASE",
                confidence=0.95
            )

        # Priority 1: Check haram blacklist
        for keyword in self.haram_keywords:
            if keyword in canonical or keyword in original:
                # Special case: "beef gelatin" is halal
                if "gelatin" in canonical:
                    if "beef" in canonical or "fish" in canonical or "bovine" in canonical:
                        return IngredientEvidence(
                            ingredient=ingredient.original,
                            normalized_name=ingredient.canonical,
                            status=HalalStatus.HALAL,
                            reason="Gelatin from halal source (beef/fish)",
                            rule_name="HALAL_GELATIN",
                            confidence=0.8
                        )
                    else:
                        return IngredientEvidence(
                            ingredient=ingredient.original,
                            normalized_name=ingredient.canonical,
                            status=HalalStatus.AMBIGUOUS,
                            reason="Gelatin source not specified - may be from pork",
                            rule_name="AMBIGUOUS_GELATIN",
                            confidence=0.9
                        )

                # Other haram ingredients
                return IngredientEvidence(
                    ingredient=ingredient.original,
                    normalized_name=ingredient.canonical,
                    status=HalalStatus.HARAM,
                    reason=f"Contains {keyword} (haram ingredient)",
                    rule_name="HARAM_BLACKLIST",
                    confidence=0.99
                )

        # Priority 2: Check halal whitelist
        for keyword in self.halal_keywords:
            if keyword in canonical or canonical.startswith(keyword):
                return IngredientEvidence(
                    ingredient=ingredient.original,
                    normalized_name=ingredient.canonical,
                    status=HalalStatus.HALAL,
                    reason="Known halal ingredient",
                    rule_name="HALAL_WHITELIST",
                    confidence=0.95
                )

        # Priority 3: Check custom rules
        for rule in self.rules:
            if rule.pattern:
                if re.search(rule.pattern, canonical, re.IGNORECASE):
                    status = self._verdict_to_status(rule.verdict)
                    return IngredientEvidence(
                        ingredient=ingredient.original,
                        normalized_name=ingredient.canonical,
                        status=status,
                        reason=rule.reason or f"Matched rule: {rule.rule_name}",
                        rule_name=rule.rule_name,
                        confidence=rule.confidence
                    )

        # Priority 4: Check for ambiguous markers
        ambiguous_markers = ["enzyme", "flavor", "flavour", "natural", "artificial", "e-", "e4", "e5"]
        for marker in ambiguous_markers:
            if marker in canonical:
                return IngredientEvidence(
                    ingredient=ingredient.original,
                    normalized_name=ingredient.canonical,
                    status=HalalStatus.AMBIGUOUS,
                    reason="Ingredient may contain animal-derived components - verification needed",
                    rule_name="AMBIGUOUS_MARKER",
                    confidence=0.7
                )

        # Default: Unknown
        return IngredientEvidence(
            ingredient=ingredient.original,
            normalized_name=ingredient.canonical,
            status=HalalStatus.UNKNOWN,
            reason="Ingredient not found in database - manual review needed",
            rule_name="UNKNOWN",
            confidence=0.5
        )

    def _verdict_to_status(self, verdict: VerdictLabel) -> HalalStatus:
        """Convert verdict label to halal status"""
        mapping = {
            VerdictLabel.HALAL: HalalStatus.HALAL,
            VerdictLabel.HARAM: HalalStatus.HARAM,
            VerdictLabel.SUSPICIOUS: HalalStatus.AMBIGUOUS,
            VerdictLabel.UNKNOWN: HalalStatus.UNKNOWN,
        }
        return mapping.get(verdict, HalalStatus.UNKNOWN)
