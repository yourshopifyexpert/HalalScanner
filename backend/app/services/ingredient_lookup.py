"""AI-Powered Ingredient Search Service"""
import logging
import httpx
import re
from typing import Optional, Dict, List
from sqlalchemy.orm import Session
from urllib.parse import quote_plus

from app.models import IngredientMaster, HalalStatus

logger = logging.getLogger(__name__)


class IngredientLookupService:
    """AI-powered service to search and analyze ingredient halal status"""

    def __init__(self, db: Session):
        self.db = db
        self.search_timeout = 10.0
        self.max_search_results = 5

    async def lookup_ingredient(self, ingredient_name: str) -> Optional[Dict]:
        """
        AI-powered ingredient lookup with multi-source analysis
        Returns dict with: status, reason, source_dependent, confidence
        """
        try:
            logger.info(f"🔍 AI Searcher analyzing: {ingredient_name}")

            # Step 1: Quick check against known patterns first (fast path)
            pattern_result = self._check_known_patterns(ingredient_name)
            if pattern_result and pattern_result['confidence'] >= 0.90:
                logger.info(f"✓ High-confidence pattern match for {ingredient_name}")
                return pattern_result

            # Step 2: Perform multi-source web search
            search_results = await self._perform_web_search(ingredient_name)

            if search_results:
                # Step 3: AI-powered analysis of search results
                ai_analysis = self._ai_analyze_results(ingredient_name, search_results)

                if ai_analysis and ai_analysis['confidence'] > 0.60:
                    logger.info(f"✓ AI analysis complete: {ai_analysis['status']} (confidence: {ai_analysis['confidence']:.2f})")
                    return ai_analysis

            # Step 4: Fallback to pattern matching with lower confidence
            logger.info(f"⚠ Using pattern-based fallback for {ingredient_name}")
            return pattern_result if pattern_result else self._unknown_result(ingredient_name)

        except Exception as e:
            logger.error(f"Error in AI searcher for {ingredient_name}: {e}")
            return self._check_known_patterns(ingredient_name)

    async def _perform_web_search(self, ingredient_name: str) -> List[str]:
        """Perform web search and extract relevant text snippets"""
        try:
            search_query = f"{ingredient_name} halal haram islamic permissible"
            logger.info(f"🌐 Searching web for: {search_query}")

            async with httpx.AsyncClient(timeout=self.search_timeout, follow_redirects=True) as client:
                # Use DuckDuckGo HTML search (more results than instant answer API)
                url = f"https://html.duckduckgo.com/html/?q={quote_plus(search_query)}"

                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }

                response = await client.get(url, headers=headers)

                if response.status_code == 200:
                    # Extract text snippets from search results
                    snippets = self._extract_snippets(response.text)
                    logger.info(f"📄 Found {len(snippets)} search result snippets")
                    return snippets

            return []

        except Exception as e:
            logger.error(f"Web search error: {e}")
            return []

    def _extract_snippets(self, html: str) -> List[str]:
        """Extract relevant text snippets from DuckDuckGo HTML results"""
        snippets = []

        # Extract result snippets (simplified HTML parsing)
        # Look for content between result divs
        snippet_pattern = r'class="result__snippet"[^>]*>([^<]+(?:<[^>]+>[^<]+)*)</a>'
        matches = re.findall(snippet_pattern, html, re.IGNORECASE | re.DOTALL)

        for match in matches[:self.max_search_results]:
            # Clean HTML tags and entities
            clean_text = re.sub(r'<[^>]+>', ' ', match)
            clean_text = re.sub(r'&[a-z]+;', ' ', clean_text)
            clean_text = ' '.join(clean_text.split())

            if len(clean_text) > 20:  # Skip very short snippets
                snippets.append(clean_text.lower())

        # If no snippets found with the pattern, try alternative extraction
        if not snippets:
            # Look for any substantial text blocks mentioning halal/haram
            text_blocks = re.findall(r'(?:halal|haram|permissible|forbidden)[^<]{20,200}', html, re.IGNORECASE)
            snippets = [block.lower() for block in text_blocks[:self.max_search_results]]

        return snippets

    def _ai_analyze_results(self, ingredient_name: str, snippets: List[str]) -> Optional[Dict]:
        """
        AI-powered analysis of search results
        Uses intelligent keyword scoring and contextual understanding
        """
        if not snippets:
            return None

        logger.info(f"🤖 AI analyzing {len(snippets)} sources for {ingredient_name}")

        # Combine all snippets for analysis
        combined_text = ' '.join(snippets)
        ingredient_lower = ingredient_name.lower()

        # Advanced keyword scoring system
        halal_indicators = {
            'halal': 3.0,
            'permissible': 2.5,
            'allowed': 2.0,
            'plant-based': 2.5,
            'plant based': 2.5,
            'vegan': 2.0,
            'vegetarian': 1.8,
            'derived from plants': 2.5,
            'synthetic': 2.0,
            'mineral': 2.0,
            'safe to consume': 1.5,
            'no animal': 2.0,
        }

        haram_indicators = {
            'haram': 3.0,
            'forbidden': 2.5,
            'prohibited': 2.5,
            'not halal': 2.8,
            'non-halal': 2.8,
            'pork': 3.5,
            'alcohol': 3.0,
            'from pig': 3.5,
            'animal-derived': 1.5,
            'from animals': 1.2,
            'not permissible': 2.5,
            'avoid': 1.8,
        }

        source_dependent_indicators = {
            'depends on': 3.0,
            'may be': 2.0,
            'can be': 2.0,
            'either': 1.8,
            'source matters': 2.5,
            'animal or plant': 2.5,
            'plant or animal': 2.5,
            'derived from either': 2.5,
            'check source': 2.8,
            'verify': 1.5,
            'uncertain': 2.0,
            'questionable': 2.2,
        }

        # Calculate weighted scores
        halal_score = sum(weight for keyword, weight in halal_indicators.items()
                         if keyword in combined_text)
        haram_score = sum(weight for keyword, weight in haram_indicators.items()
                         if keyword in combined_text)
        ambiguous_score = sum(weight for keyword, weight in source_dependent_indicators.items()
                             if keyword in combined_text)

        # Normalize scores by number of snippets
        num_sources = len(snippets)
        halal_score /= num_sources
        haram_score /= num_sources
        ambiguous_score /= num_sources

        logger.info(f"📊 Scores - Halal: {halal_score:.2f}, Haram: {haram_score:.2f}, Ambiguous: {ambiguous_score:.2f}")

        # AI decision logic with confidence scoring
        total_score = halal_score + haram_score + ambiguous_score

        if total_score < 1.0:
            # Not enough information in search results
            return None

        # Determine status based on highest score and context
        if ambiguous_score > 2.0 or (ambiguous_score > 1.5 and halal_score > 0 and haram_score > 0):
            confidence = min(0.85, 0.65 + (ambiguous_score / 10))
            return {
                'status': HalalStatus.AMBIGUOUS,
                'reason': f"{ingredient_name} - Halal status depends on source. Multiple sources indicate it may be plant or animal-derived. Verification needed.",
                'source_dependent': True,
                'confidence': confidence,
                'should_add_to_db': True,
                'sources_analyzed': num_sources
            }

        elif haram_score > halal_score and haram_score > 1.5:
            confidence = min(0.90, 0.70 + (haram_score / 10))
            return {
                'status': HalalStatus.HARAM,
                'reason': f"{ingredient_name} is generally considered haram based on {num_sources} sources",
                'source_dependent': False,
                'confidence': confidence,
                'should_add_to_db': True,
                'sources_analyzed': num_sources
            }

        elif halal_score > haram_score and halal_score > 1.5:
            confidence = min(0.90, 0.70 + (halal_score / 10))
            return {
                'status': HalalStatus.HALAL,
                'reason': f"{ingredient_name} is generally halal based on {num_sources} sources",
                'source_dependent': False,
                'confidence': confidence,
                'should_add_to_db': True,
                'sources_analyzed': num_sources
            }

        else:
            # Scores are too low or balanced
            return None

    def _unknown_result(self, ingredient_name: str) -> Dict:
        """Return unknown result for ingredient"""
        return {
            'status': HalalStatus.UNKNOWN,
            'reason': f"Could not determine halal status for {ingredient_name}. Manual verification recommended.",
            'source_dependent': False,
            'confidence': 0.50,
            'should_add_to_db': False
        }

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
            'tomato', 'potato', 'onion', 'garlic', 'pepper', 'herb', 'spice',
            'citric', 'ascorbic', 'acid', 'turmeric', 'ginger', 'cinnamon',
            'maltodextrin', 'dextrose', 'glucose', 'fructose', 'syrup',
            'xanthan', 'guar', 'gum', 'pectin', 'agar', 'carrageenan',
            'cellulose', 'beta', 'carotene', 'annatto', 'paprika', 'saffron'
        ]

        # Definitely haram
        haram_ingredients = [
            'pork', 'bacon', 'ham', 'lard', 'alcohol', 'wine', 'beer', 'rum',
            'gelatin', 'pepsin', 'rennet', 'carmine', 'blood', 'plasma'
        ]

        # Source-dependent (ambiguous) - needs verification
        ambiguous_ingredients = [
            'enzyme', 'emulsifier', 'glycerin', 'glycerol', 'mono', 'diglyceride',
            'lecithin', 'shortening', 'vitamin d', 'vitamin a', 'flavor', 'flavoring',
            'whey', 'casein', 'lactose', 'lipase', 'trypsin'
        ]

        # E-numbers that are always halal (plant/mineral/synthetic)
        halal_e_numbers = {
            'e300': 'ascorbic acid', 'e330': 'citric acid', 'e440': 'pectin',
            'e415': 'xanthan gum', 'e412': 'guar gum', 'e407': 'carrageenan',
            'e100': 'curcumin/turmeric', 'e160': 'carotenoids', 'e500': 'sodium carbonate'
        }

        # Check E-numbers
        for e_num, name in halal_e_numbers.items():
            if e_num in name_lower:
                return {
                    'status': HalalStatus.HALAL,
                    'reason': f"{ingredient_name} ({name}) is plant/mineral-based, therefore halal",
                    'source_dependent': False,
                    'confidence': 0.90,
                    'should_add_to_db': True
                }

        # Check if matches any pattern
        for plant in plant_based:
            if plant in name_lower:
                return {
                    'status': HalalStatus.HALAL,
                    'reason': f"{ingredient_name} is plant-based/synthetic, therefore halal",
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
                    'reason': f"{ingredient_name} - Halal status depends on source. May be plant or animal-derived. Verification needed.",
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
