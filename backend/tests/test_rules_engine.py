"""Tests for Rules Engine"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.services.rules_engine import RulesEngine
from app.schemas import NormalizedIngredient, HalalStatus
from app.models import RuleDefinition, IngredientMaster

# Test database setup
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db_session():
    """Create test database session"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


def test_haram_ingredient_detection(db_session):
    """Test detection of haram ingredients"""
    rules_engine = RulesEngine(db_session)

    # Test pork detection
    ingredient = NormalizedIngredient(
        original="pork gelatin",
        canonical="PORK_GELATIN",
        aliases=[],
        confidence=0.9
    )

    evidence = rules_engine.classify_ingredient(ingredient)
    assert evidence.status == HalalStatus.HARAM
    assert "pork" in evidence.reason.lower()


def test_halal_ingredient_detection(db_session):
    """Test detection of halal ingredients"""
    rules_engine = RulesEngine(db_session)

    ingredient = NormalizedIngredient(
        original="water",
        canonical="WATER",
        aliases=[],
        confidence=1.0
    )

    evidence = rules_engine.classify_ingredient(ingredient)
    assert evidence.status == HalalStatus.HALAL


def test_ambiguous_gelatin(db_session):
    """Test ambiguous gelatin (source not specified)"""
    rules_engine = RulesEngine(db_session)

    ingredient = NormalizedIngredient(
        original="gelatin",
        canonical="GELATIN",
        aliases=[],
        confidence=0.9
    )

    evidence = rules_engine.classify_ingredient(ingredient)
    assert evidence.status == HalalStatus.AMBIGUOUS


def test_beef_gelatin_halal(db_session):
    """Test beef gelatin is halal"""
    rules_engine = RulesEngine(db_session)

    ingredient = NormalizedIngredient(
        original="beef gelatin",
        canonical="BEEF_GELATIN",
        aliases=[],
        confidence=0.9
    )

    evidence = rules_engine.classify_ingredient(ingredient)
    assert evidence.status == HalalStatus.HALAL


def test_ingredient_database_lookup(db_session):
    """Test ingredient lookup from database"""
    # Add test ingredient to database
    test_ingredient = IngredientMaster(
        canonical_name="TEST_INGREDIENT",
        aliases=["test", "testing"],
        halal_status=HalalStatus.HALAL,
        notes="Test ingredient"
    )
    db_session.add(test_ingredient)
    db_session.commit()

    rules_engine = RulesEngine(db_session)

    ingredient = NormalizedIngredient(
        original="test",
        canonical="TEST_INGREDIENT",
        aliases=[],
        confidence=0.9
    )

    evidence = rules_engine.classify_ingredient(ingredient)
    assert evidence.status == HalalStatus.HALAL
    assert evidence.rule_name == "DATABASE"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
