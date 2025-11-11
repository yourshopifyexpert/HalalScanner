"""Online Ingredient Lookup Service"""
import logging
import httpx
from typing import Optional, Dict
from sqlalchemy.orm import Session

from app.models import IngredientMaster, HalalStatus

logger = logging.getLogger(__name__)


class IngredientLookupService:
    """Service to look up ingredient halal status online"""

    def __init__(self, db: Session):
        self.db = db
        self.search_timeout = 5.0

    async def lookup_ingredient(self, ingredient_name: str) -> Optional[Dict]:
        """
        Look up ingredient halal status online
        Returns dict with: status, reason, source_dependent, confidence
        """
        try:
            # Search using web search for halal status
            search_query = f"{ingredient_name} halal haram status islamic"

            async with httpx.AsyncClient(timeout=self.search_timeout) as client:
                # Use DuckDuckGo instant answer API (free, no auth)
                response = await client.get(
                    "https://api.duckduckgo.com/",
                    params={
                        "q": search_query,
                        "format": "json",
                        "no_html": 1,
                        "skip_disambig": 1
                    }
                )

                if response.status_code == 200:
                    result = response.json()
                    abstract = result.get('AbstractText', '').lower()

                    if abstract:
                        return self._analyze_search_result(ingredient_name, abstract)

            # Fallback: Check against known patterns
            return self._check_known_patterns(ingredient_name)

        except Exception as e:
            logger.error(f"Error looking up ingredient {ingredient_name}: {e}")
            return None

    def _analyze_search_result(self, ingredient_name: str, text: str) -> Dict:
        """Analyze search result text to determine halal status"""
        text_lower = text.lower()
        ingredient_lower = ingredient_name.lower()

        # Check for definitive halal indicators
        halal_keywords = ['halal', 'permissible', 'allowed', 'plant-based', 'vegan', 'vegetarian']
        haram_keywords = ['haram', 'forbidden', 'prohibited', 'pork', 'alcohol', 'non-halal']
        source_dependent_keywords = ['depends on', 'may be', 'can be', 'source matters', 'animal or plant']

        halal_count = sum(1 for kw in halal_keywords if kw in text_lower)
        haram_count = sum(1 for kw in haram_keywords if kw in text_lower)
        source_dependent = any(kw in text_lower for kw in source_dependent_keywords)

        # Determine status
        if source_dependent or (halal_count > 0 and haram_count > 0):
            return {
                'status': HalalStatus.AMBIGUOUS,
                'reason': f"Halal status depends on source - {ingredient_name} can be plant or animal-derived",
                'source_dependent': True,
                'confidence': 0.75,
                'should_add_to_db': True
            }
        elif haram_count > halal_count:
            return {
                'status': HalalStatus.HARAM,
                'reason': f"{ingredient_name} is generally considered haram",
                'source_dependent': False,
                'confidence': 0.80,
                'should_add_to_db': True
            }
        elif halal_count > haram_count:
            return {
                'status': HalalStatus.HALAL,
                'reason': f"{ingredient_name} is generally halal",
                'source_dependent': False,
                'confidence': 0.85,
                'should_add_to_db': True
            }
        else:
            return {
                'status': HalalStatus.UNKNOWN,
                'reason': f"Could not determine halal status for {ingredient_name}",
                'source_dependent': False,
                'confidence': 0.50,
                'should_add_to_db': False
            }

    def _check_known_patterns(self, ingredient_name: str) -> Dict:
        """Check ingredient against known patterns"""
        name_lower = ingredient_name.lower()

        # Common plant-based ingredients (always halal)
        plant_based = [
            'flour', 'sugar', 'salt', 'water', 'oil', 'starch', 'vinegar',
            'vegetable', 'fruit', 'grain', 'rice', 'wheat', 'corn', 'soy',
            'tomato', 'potato', 'onion', 'garlic', 'pepper', 'herb', 'spice'
        ]

        # Definitely haram
        haram_ingredients = [
            'pork', 'bacon', 'ham', 'lard', 'alcohol', 'wine', 'beer',
            'gelatin', 'pepsin', 'rennet', 'carmine', 'blood'
        ]

        # Source-dependent (ambiguous)
        ambiguous_ingredients = [
            'enzyme', 'emulsifier', 'glycerin', 'glycerol', 'mono', 'diglyceride',
            'lecithin', 'shortening', 'vitamin', 'flavor', 'flavoring'
        ]

        # Check if matches any pattern
        for plant in plant_based:
            if plant in name_lower:
                return {
                    'status': HalalStatus.HALAL,
                    'reason': f"{ingredient_name} is plant-based, therefore halal",
                    'source_dependent': False,
                    'confidence': 0.90,
                    'should_add_to_db': True
                }

        for haram in haram_ingredients:
            if haram in name_lower:
                return {
                    'status': HalalStatus.HARAM,
                    'reason': f"{ingredient_name} contains {haram} which is haram",
                    'source_dependent': False,
                    'confidence': 0.95,
                    'should_add_to_db': True
                }

        for ambig in ambiguous_ingredients:
            if ambig in name_lower:
                return {
                    'status': HalalStatus.AMBIGUOUS,
                    'reason': f"{ingredient_name} may be plant or animal-derived. Source verification needed.",
                    'source_dependent': True,
                    'confidence': 0.80,
                    'should_add_to_db': True
                }

        # Unknown
        return {
            'status': HalalStatus.UNKNOWN,
            'reason': f"Halal status unknown for {ingredient_name}. Manual verification recommended.",
            'source_dependent': False,
            'confidence': 0.50,
            'should_add_to_db': False
        }

    def add_ingredient_to_database(
        self,
        canonical_name: str,
        aliases: list,
        halal_status: HalalStatus,
        notes: str
    ) -> IngredientMaster:
        """Add newly discovered ingredient to database"""
        try:
            # Check if already exists
            existing = self.db.query(IngredientMaster).filter(
                IngredientMaster.canonical_name == canonical_name.upper()
            ).first()

            if existing:
                logger.info(f"Ingredient {canonical_name} already exists in database")
                return existing

            # Create new ingredient
            new_ingredient = IngredientMaster(
                canonical_name=canonical_name.upper(),
                aliases=aliases,
                halal_status=halal_status,
                category="Auto-discovered",
                notes=notes
            )

            self.db.add(new_ingredient)
            self.db.commit()
            self.db.refresh(new_ingredient)

            logger.info(f"Added new ingredient to database: {canonical_name} - {halal_status}")
            return new_ingredient

        except Exception as e:
            logger.error(f"Error adding ingredient to database: {e}")
            self.db.rollback()
            return None
