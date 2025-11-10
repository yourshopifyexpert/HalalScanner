"""Database configuration and session management"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Create database engine
# SQLite-specific settings for better compatibility
if settings.DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        pool_pre_ping=True
    )
else:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20
    )

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database (create all tables)"""
    import app.models  # Import models to register them
    Base.metadata.create_all(bind=engine)

    # Seed database with initial data if tables are empty
    try:
        from app.seed_data import seed_rules, seed_ingredients, seed_manufacturers
        from app.models import RuleDefinition
        import logging

        logger = logging.getLogger(__name__)
        db = SessionLocal()

        try:
            # Check if database is already seeded
            rule_count = db.query(RuleDefinition).count()
            if rule_count == 0:
                logger.info("Database is empty. Seeding initial data...")
                seed_rules(db)
                seed_ingredients(db)
                seed_manufacturers(db)
                logger.info("Database seeded successfully!")
            else:
                logger.info(f"Database already contains {rule_count} rules. Skipping seed.")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error during database seeding: {e}")
