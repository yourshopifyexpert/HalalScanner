"""Tests for Ingredient Normalizer"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.services.normalizer import IngredientNormalizer

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


@pytest.mark.asyncio
async def test_basic_normalization(db_session):
    """Test basic ingredient normalization"""
    normalizer = IngredientNormalizer(db_session)

    text = "Ingredients: water, sugar, salt, flour"
    result = await normalizer.normalize(text)

    assert len(result) >= 4
    ingredient_names = [ing.canonical for ing in result]
    assert "WATER" in ingredient_names or "water" in [ing.original for ing in result]


@pytest.mark.asyncio
async def test_ingredient_extraction(db_session):
    """Test extraction of ingredients section"""
    normalizer = IngredientNormalizer(db_session)

    text = """
    Product Name: Test Product
    Ingredients: water, sugar, salt
    Nutrition Facts: 100 calories
    """

    result = await normalizer.normalize(text)
    assert len(result) >= 3


@pytest.mark.asyncio
async def test_comma_separated_parsing(db_session):
    """Test parsing of comma-separated ingredients"""
    normalizer = IngredientNormalizer(db_session)

    text = "water, sugar, salt, flour, yeast"
    result = await normalizer.normalize(text)

    assert len(result) >= 5


@pytest.mark.asyncio
async def test_empty_text(db_session):
    """Test handling of empty text"""
    normalizer = IngredientNormalizer(db_session)

    result = await normalizer.normalize("")
    assert len(result) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
