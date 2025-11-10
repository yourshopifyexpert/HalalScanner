"""Database seed data initialization"""
import logging
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import (
    RuleDefinition, IngredientMaster, Manufacturer,
    HalalCertification, VerdictLabel, HalalStatus
)
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def seed_rules(db: Session):
    """Seed classification rules"""
    rules = [
        # Haram rules (highest priority)
        {
            "rule_name": "PORK_BLACKLIST",
            "rule_type": "blacklist",
            "pattern": r"\b(pork|pig|swine|lard|bacon|ham)\b",
            "verdict": VerdictLabel.HARAM,
            "confidence": 0.99,
            "reason": "Contains pork or pork derivatives",
            "priority": 100
        },
        {
            "rule_name": "ALCOHOL_BLACKLIST",
            "rule_type": "blacklist",
            "pattern": r"\b(alcohol|ethanol|ethyl alcohol|wine|beer|rum|vodka)\b",
            "verdict": VerdictLabel.HARAM,
            "confidence": 0.98,
            "reason": "Contains alcohol",
            "priority": 95
        },
        {
            "rule_name": "BLOOD_BLACKLIST",
            "rule_type": "blacklist",
            "pattern": r"\b(blood|plasma)\b",
            "verdict": VerdictLabel.HARAM,
            "confidence": 0.99,
            "reason": "Contains blood or blood derivatives",
            "priority": 90
        },

        # Ambiguous rules
        {
            "rule_name": "GELATIN_AMBIGUOUS",
            "rule_type": "pattern",
            "pattern": r"\bgelatin\b(?!.*(beef|bovine|fish))",
            "verdict": VerdictLabel.SUSPICIOUS,
            "confidence": 0.9,
            "reason": "Gelatin source not specified - may be from pork",
            "priority": 80
        },
        {
            "rule_name": "ENZYMES_AMBIGUOUS",
            "rule_type": "pattern",
            "pattern": r"\benzyme",
            "verdict": VerdictLabel.SUSPICIOUS,
            "confidence": 0.75,
            "reason": "Enzymes may be animal-derived - verification needed",
            "priority": 70
        },
        {
            "rule_name": "MONO_DIGLYCERIDES_AMBIGUOUS",
            "rule_type": "pattern",
            "pattern": r"\bmono.*diglyceride|glyceride",
            "verdict": VerdictLabel.SUSPICIOUS,
            "confidence": 0.8,
            "reason": "May contain animal-derived fats",
            "priority": 70
        },
        {
            "rule_name": "NATURAL_FLAVORS_AMBIGUOUS",
            "rule_type": "pattern",
            "pattern": r"\bnatural\s+flavo",
            "verdict": VerdictLabel.SUSPICIOUS,
            "confidence": 0.7,
            "reason": "Natural flavors may contain animal-derived carriers",
            "priority": 65
        },

        # Halal whitelist (lower priority)
        {
            "rule_name": "PLANT_BASED_HALAL",
            "rule_type": "whitelist",
            "pattern": r"\b(vegetable|plant|vegan|fruit|grain|legume)\b",
            "verdict": VerdictLabel.HALAL,
            "confidence": 0.95,
            "reason": "Plant-based ingredient",
            "priority": 50
        },
    ]

    for rule_data in rules:
        # Check if rule already exists
        existing = db.query(RuleDefinition).filter(
            RuleDefinition.rule_name == rule_data["rule_name"]
        ).first()

        if not existing:
            rule = RuleDefinition(**rule_data)
            db.add(rule)
            logger.info(f"Added rule: {rule_data['rule_name']}")

    db.commit()
    logger.info(f"Seeded {len(rules)} rules")


def seed_ingredients(db: Session):
    """Seed master ingredient database"""
    ingredients = [
        # Common halal ingredients
        {
            "canonical_name": "WATER",
            "aliases": ["water", "aqua", "h2o"],
            "halal_status": HalalStatus.HALAL,
            "category": "Base",
            "notes": "Always halal"
        },
        {
            "canonical_name": "SUGAR",
            "aliases": ["sugar", "sucrose", "cane sugar", "beet sugar"],
            "halal_status": HalalStatus.HALAL,
            "category": "Sweetener",
            "notes": "Plant-based, halal"
        },
        {
            "canonical_name": "SALT",
            "aliases": ["salt", "sodium chloride", "sea salt"],
            "halal_status": HalalStatus.HALAL,
            "category": "Seasoning",
            "notes": "Mineral, halal"
        },
        {
            "canonical_name": "WHEAT_FLOUR",
            "aliases": ["wheat flour", "flour", "enriched flour"],
            "halal_status": HalalStatus.HALAL,
            "category": "Grain",
            "notes": "Plant-based, halal"
        },
        {
            "canonical_name": "VEGETABLE_OIL",
            "aliases": ["vegetable oil", "soybean oil", "canola oil", "palm oil"],
            "halal_status": HalalStatus.HALAL,
            "category": "Fat/Oil",
            "notes": "Plant-based, halal"
        },

        # Haram ingredients
        {
            "canonical_name": "PORK_GELATIN",
            "aliases": ["pork gelatin", "porcine gelatin"],
            "halal_status": HalalStatus.HARAM,
            "category": "Gelling Agent",
            "notes": "Derived from pork"
        },
        {
            "canonical_name": "LARD",
            "aliases": ["lard", "pork fat"],
            "halal_status": HalalStatus.HARAM,
            "category": "Fat/Oil",
            "notes": "Pork fat"
        },
        {
            "canonical_name": "ALCOHOL",
            "aliases": ["alcohol", "ethanol", "ethyl alcohol"],
            "halal_status": HalalStatus.HARAM,
            "category": "Solvent",
            "notes": "Intoxicating substance"
        },

        # Ambiguous ingredients
        {
            "canonical_name": "GELATIN",
            "aliases": ["gelatin", "gelatine"],
            "halal_status": HalalStatus.AMBIGUOUS,
            "category": "Gelling Agent",
            "notes": "Source must be specified - can be from pork, beef, or fish"
        },
        {
            "canonical_name": "GLYCERIN",
            "aliases": ["glycerin", "glycerol", "glycerine"],
            "halal_status": HalalStatus.AMBIGUOUS,
            "category": "Humectant",
            "notes": "Can be plant or animal-derived"
        },
        {
            "canonical_name": "MONO_AND_DIGLYCERIDES",
            "aliases": ["mono and diglycerides", "monoglycerides", "e471"],
            "halal_status": HalalStatus.AMBIGUOUS,
            "category": "Emulsifier",
            "e_number": "E471",
            "notes": "Can be plant or animal-derived"
        },
        {
            "canonical_name": "ENZYMES",
            "aliases": ["enzymes", "enzyme"],
            "halal_status": HalalStatus.AMBIGUOUS,
            "category": "Processing Aid",
            "notes": "Source must be specified - can be microbial or animal"
        },
        {
            "canonical_name": "NATURAL_FLAVORS",
            "aliases": ["natural flavors", "natural flavoring"],
            "halal_status": HalalStatus.AMBIGUOUS,
            "category": "Flavoring",
            "notes": "May contain animal-derived carriers"
        },

        # Common E-numbers
        {
            "canonical_name": "CITRIC_ACID",
            "aliases": ["citric acid", "e330"],
            "halal_status": HalalStatus.HALAL,
            "category": "Acidifier",
            "e_number": "E330",
            "notes": "Plant-derived, halal"
        },
        {
            "canonical_name": "ASCORBIC_ACID",
            "aliases": ["ascorbic acid", "vitamin c", "e300"],
            "halal_status": HalalStatus.HALAL,
            "category": "Antioxidant",
            "e_number": "E300",
            "notes": "Synthetic or plant-derived, halal"
        },
    ]

    for ing_data in ingredients:
        # Check if ingredient already exists
        existing = db.query(IngredientMaster).filter(
            IngredientMaster.canonical_name == ing_data["canonical_name"]
        ).first()

        if not existing:
            ingredient = IngredientMaster(**ing_data)
            db.add(ingredient)
            logger.info(f"Added ingredient: {ing_data['canonical_name']}")

    db.commit()
    logger.info(f"Seeded {len(ingredients)} ingredients")


def seed_manufacturers(db: Session):
    """Seed sample manufacturer data"""
    manufacturers = [
        {
            "name": "Example Halal Foods Inc.",
            "website": "https://example-halal.com",
            "email": "info@example-halal.com",
            "country": "USA"
        },
        {
            "name": "Global Snacks Co.",
            "website": "https://globalsnacks.com",
            "email": "support@globalsnacks.com",
            "country": "USA"
        },
    ]

    for mfr_data in manufacturers:
        existing = db.query(Manufacturer).filter(
            Manufacturer.name == mfr_data["name"]
        ).first()

        if not existing:
            manufacturer = Manufacturer(**mfr_data)
            db.add(manufacturer)
            logger.info(f"Added manufacturer: {mfr_data['name']}")

    db.commit()
    logger.info(f"Seeded {len(manufacturers)} manufacturers")

    # Add sample certification
    mfr = db.query(Manufacturer).filter(
        Manufacturer.name == "Example Halal Foods Inc."
    ).first()

    if mfr:
        existing_cert = db.query(HalalCertification).filter(
            HalalCertification.manufacturer_id == mfr.id
        ).first()

        if not existing_cert:
            cert = HalalCertification(
                manufacturer_id=mfr.id,
                cert_body="IFANCA",
                cert_id="IFANCA-12345",
                valid_from=datetime.utcnow() - timedelta(days=180),
                valid_to=datetime.utcnow() + timedelta(days=180),
                scope="All products",
                verified=True
            )
            db.add(cert)
            db.commit()
            logger.info("Added sample halal certification")


def seed_database():
    """Main function to seed all data"""
    logger.info("Starting database seeding...")

    # Initialize database (import here to avoid circular dependency)
    from app.database import init_db
    init_db()

    # Create session
    db = SessionLocal()

    try:
        seed_rules(db)
        seed_ingredients(db)
        seed_manufacturers(db)

        logger.info("Database seeding completed successfully!")

    except Exception as e:
        logger.error(f"Error seeding database: {e}", exc_info=True)
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seed_database()
