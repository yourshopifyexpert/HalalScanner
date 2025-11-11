"""Ingredient Classifier - Combines Rules Engine + ML"""
import logging
from typing import List, Optional
from sqlalchemy.orm import Session

from app.schemas import (
    VerdictLabel, HalalStatus, IngredientEvidence,
    NormalizedIngredient, ClassificationResult
)
from app.services.rules_engine import RulesEngine
from app.services.ingredient_lookup import IngredientLookupService
from app.models import HalalCertification, Manufacturer
from app.config import settings

logger = logging.getLogger(__name__)


class IngredientClassifier:
    """
    Main classifier combining rules engine and ML model

    Decision logic:
    1. Run rules engine on all ingredients
    2. If any HARAM found → HARAM verdict
    3. If halal certification exists → boost confidence
    4. If ambiguous ingredients → SUSPICIOUS
    5. If ML model available, consult for ambiguous cases
    6. Compute final verdict and confidence
    """

    def __init__(self, db: Session):
        self.db = db
        self.rules_engine = RulesEngine(db)
        self.lookup_service = IngredientLookupService(db)
        self.ml_model = None  # Placeholder for ML model

    async def classify(
        self,
        ingredients: List[NormalizedIngredient],
        manufacturer_name: Optional[str] = None,
        barcode: Optional[str] = None
    ) -> ClassificationResult:
        """Classify all ingredients and produce final verdict"""

        if not ingredients:
            return ClassificationResult(
                verdict=VerdictLabel.UNKNOWN,
                confidence=0.0,
                evidence=[],
                reasoning="No ingredients detected"
            )

        # Step 1: Classify each ingredient using rules engine
        evidence_list = []
        for ingredient in ingredients:
            evidence = self.rules_engine.classify_ingredient(ingredient)

            # If ingredient is UNKNOWN, try online lookup
            if evidence.status == HalalStatus.UNKNOWN:
                logger.info(f"Ingredient '{ingredient.canonical}' not in database, looking up online...")

                lookup_result = await self.lookup_service.lookup_ingredient(ingredient.canonical)

                if lookup_result:
                    logger.info(f"Online lookup result for '{ingredient.canonical}': {lookup_result['status']}")

                    # Update evidence with lookup result
                    evidence = IngredientEvidence(
                        ingredient=ingredient.original,
                        normalized_name=ingredient.canonical,
                        status=lookup_result['status'],
                        reason=lookup_result['reason'],
                        rule_name="ONLINE_LOOKUP",
                        confidence=lookup_result['confidence']
                    )

                    # Add to database if it's a confirmed halal/haram/ambiguous ingredient
                    if lookup_result.get('should_add_to_db', False):
                        self.lookup_service.add_ingredient_to_database(
                            canonical_name=ingredient.canonical,
                            aliases=[ingredient.original.lower(), ingredient.canonical.lower()],
                            halal_status=lookup_result['status'],
                            notes=f"Auto-discovered via online lookup. {lookup_result['reason']}"
                        )
                        logger.info(f"Added '{ingredient.canonical}' to database with status {lookup_result['status']}")

            evidence_list.append(evidence)

        # Step 2: Check for halal certification
        has_certification = False
        if manufacturer_name:
            has_certification = self._check_certification(manufacturer_name)

        # Step 3: Apply ML model to ambiguous ingredients
        if self.ml_model:
            evidence_list = await self._apply_ml_model(evidence_list, ingredients)

        # Step 4: Compute final verdict
        verdict, confidence = self._compute_verdict(
            evidence_list,
            has_certification
        )

        # Step 5: Generate reasoning
        reasoning = self._generate_reasoning(evidence_list, verdict, has_certification)

        logger.info(
            f"Classification complete: {verdict} (confidence: {confidence:.2f}) "
            f"for {len(ingredients)} ingredients"
        )

        return ClassificationResult(
            verdict=verdict,
            confidence=confidence,
            evidence=evidence_list,
            reasoning=reasoning
        )

    def _check_certification(self, manufacturer_name: str) -> bool:
        """Check if manufacturer has valid halal certification"""
        manufacturer = self.db.query(Manufacturer).filter(
            Manufacturer.name.ilike(f"%{manufacturer_name}%")
        ).first()

        if not manufacturer:
            return False

        # Check for valid certifications
        from datetime import datetime
        valid_certs = self.db.query(HalalCertification).filter(
            HalalCertification.manufacturer_id == manufacturer.id,
            HalalCertification.verified == True,
            HalalCertification.valid_to >= datetime.utcnow()
        ).count()

        return valid_certs > 0

    async def _apply_ml_model(
        self,
        evidence_list: List[IngredientEvidence],
        ingredients: List[NormalizedIngredient]
    ) -> List[IngredientEvidence]:
        """
        Apply ML model to refine ambiguous classifications
        (Placeholder for future ML integration)
        """
        # TODO: Implement ML model inference
        # For now, just return the original evidence
        logger.info("ML model not yet implemented, using rules-only classification")
        return evidence_list

    def _compute_verdict(
        self,
        evidence_list: List[IngredientEvidence],
        has_certification: bool
    ) -> tuple[VerdictLabel, float]:
        """Compute final product verdict from ingredient evidence"""

        if not evidence_list:
            return VerdictLabel.UNKNOWN, 0.0

        # Count statuses
        status_counts = {
            HalalStatus.HARAM: 0,
            HalalStatus.HALAL: 0,
            HalalStatus.AMBIGUOUS: 0,
            HalalStatus.UNKNOWN: 0
        }

        total_confidence = 0.0
        for evidence in evidence_list:
            status_counts[evidence.status] += 1
            total_confidence += evidence.confidence

        avg_confidence = total_confidence / len(evidence_list)

        # Decision logic
        # Priority 1: Any HARAM ingredient → HARAM verdict
        if status_counts[HalalStatus.HARAM] > 0:
            haram_evidence = [e for e in evidence_list if e.status == HalalStatus.HARAM]
            max_confidence = max(e.confidence for e in haram_evidence)
            return VerdictLabel.HARAM, max_confidence

        # Priority 2: Ambiguous ingredients → SUSPICIOUS
        if status_counts[HalalStatus.AMBIGUOUS] > 0:
            # If certified halal, boost to HALAL but lower confidence
            if has_certification:
                return VerdictLabel.HALAL, 0.75
            else:
                return VerdictLabel.SUSPICIOUS, avg_confidence * 0.8

        # Priority 3: Unknown ingredients → SUSPICIOUS or UNKNOWN
        if status_counts[HalalStatus.UNKNOWN] > 0:
            unknown_ratio = status_counts[HalalStatus.UNKNOWN] / len(evidence_list)

            if unknown_ratio > 0.5:
                return VerdictLabel.UNKNOWN, avg_confidence * 0.6
            else:
                # Some unknowns but mostly halal
                if has_certification:
                    return VerdictLabel.HALAL, 0.8
                else:
                    return VerdictLabel.SUSPICIOUS, avg_confidence * 0.7

        # Priority 4: All HALAL → HALAL verdict
        if status_counts[HalalStatus.HALAL] == len(evidence_list):
            confidence = avg_confidence
            if has_certification:
                confidence = min(0.98, confidence + 0.1)  # Boost confidence
            return VerdictLabel.HALAL, confidence

        # Default: SUSPICIOUS
        return VerdictLabel.SUSPICIOUS, avg_confidence * 0.7

    def _generate_reasoning(
        self,
        evidence_list: List[IngredientEvidence],
        verdict: VerdictLabel,
        has_certification: bool
    ) -> str:
        """Generate human-readable reasoning for the verdict"""

        reasoning_parts = []

        # Count by status
        haram_count = sum(1 for e in evidence_list if e.status == HalalStatus.HARAM)
        ambiguous_count = sum(1 for e in evidence_list if e.status == HalalStatus.AMBIGUOUS)
        unknown_count = sum(1 for e in evidence_list if e.status == HalalStatus.UNKNOWN)
        halal_count = sum(1 for e in evidence_list if e.status == HalalStatus.HALAL)

        if verdict == VerdictLabel.HARAM:
            haram_ingredients = [e.ingredient for e in evidence_list if e.status == HalalStatus.HARAM]
            reasoning_parts.append(
                f"Product contains {haram_count} haram ingredient(s): {', '.join(haram_ingredients[:3])}"
            )

        elif verdict == VerdictLabel.SUSPICIOUS:
            if ambiguous_count > 0:
                reasoning_parts.append(
                    f"{ambiguous_count} ingredient(s) are ambiguous and require manufacturer verification"
                )
            if unknown_count > 0:
                reasoning_parts.append(
                    f"{unknown_count} ingredient(s) are not in our database"
                )

        elif verdict == VerdictLabel.HALAL:
            reasoning_parts.append(
                f"All {halal_count} ingredients appear to be halal"
            )
            if has_certification:
                reasoning_parts.append("Manufacturer has valid halal certification")

        elif verdict == VerdictLabel.UNKNOWN:
            reasoning_parts.append(
                f"Unable to determine halal status - {unknown_count} unknown ingredients"
            )

        return ". ".join(reasoning_parts)
