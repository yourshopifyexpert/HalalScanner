"""Database models"""
from sqlalchemy import Column, Integer, String, DateTime, Float, Text, JSON, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
from app.database import Base


class VerdictLabel(str, enum.Enum):
    """Product verdict labels"""
    HALAL = "HALAL"
    HARAM = "HARAM"
    SUSPICIOUS = "SUSPICIOUS"
    UNKNOWN = "UNKNOWN"


class HalalStatus(str, enum.Enum):
    """Ingredient halal status"""
    HALAL = "HALAL"
    HARAM = "HARAM"
    AMBIGUOUS = "AMBIGUOUS"
    UNKNOWN = "UNKNOWN"


class User(Base):
    """User model"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True)
    privacy_mode = Column(Boolean, default=True)  # Local-only mode
    language = Column(String, default="en")
    region = Column(String, default="US")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    scans = relationship("Scan", back_populates="user")
    feedbacks = relationship("UserFeedback", back_populates="user")


class Manufacturer(Base):
    """Manufacturer/Brand model"""
    __tablename__ = "manufacturers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    website = Column(String)
    email = Column(String)
    phone = Column(String)
    country = Column(String)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    products = relationship("Product", back_populates="manufacturer")
    certifications = relationship("HalalCertification", back_populates="manufacturer")


class HalalCertification(Base):
    """Halal certification model"""
    __tablename__ = "halal_certifications"

    id = Column(Integer, primary_key=True, index=True)
    manufacturer_id = Column(Integer, ForeignKey("manufacturers.id"))
    cert_body = Column(String, nullable=False)  # e.g., "IFANCA", "HFA"
    cert_id = Column(String)
    valid_from = Column(DateTime)
    valid_to = Column(DateTime)
    scope = Column(Text)  # What products does this cover
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    manufacturer = relationship("Manufacturer", back_populates="certifications")


class Product(Base):
    """Product model"""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(String, unique=True, index=True, nullable=False)
    barcode = Column(String, index=True)
    name = Column(String, nullable=False)
    manufacturer_id = Column(Integer, ForeignKey("manufacturers.id"))
    category = Column(String)  # e.g., "Snacks", "Dairy", "Meat"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    manufacturer = relationship("Manufacturer", back_populates="products")
    scans = relationship("Scan", back_populates="product")


class Scan(Base):
    """Scan model - each scan of a product"""
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)

    # Image data
    image_url = Column(String)  # S3 URL or local path
    image_hash = Column(String)  # For deduplication

    # OCR results
    ocr_text = Column(Text)
    ocr_confidence = Column(Float)
    ocr_language = Column(String)

    # Parsed ingredients
    normalized_ingredients = Column(JSON)  # List of normalized ingredient objects

    # Classification results
    verdict = Column(SQLEnum(VerdictLabel), nullable=False)
    confidence = Column(Float, nullable=False)
    explanation = Column(JSON)  # Detailed explanation with matched rules

    # Manufacturer contact
    manufacturer_contacted = Column(Boolean, default=False)
    manufacturer_response = Column(Text)
    manufacturer_response_date = Column(DateTime)

    # Timestamps
    scan_date = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="scans")
    product = relationship("Product", back_populates="scans")
    feedbacks = relationship("UserFeedback", back_populates="scan")


class IngredientMaster(Base):
    """Master ingredient database"""
    __tablename__ = "ingredient_master"

    id = Column(Integer, primary_key=True, index=True)
    canonical_name = Column(String, unique=True, nullable=False, index=True)
    aliases = Column(JSON)  # List of alternative names
    halal_status = Column(SQLEnum(HalalStatus), default=HalalStatus.UNKNOWN)
    category = Column(String)  # e.g., "Sweetener", "Preservative", "Emulsifier"
    e_number = Column(String)  # E-number if applicable
    sources = Column(JSON)  # Sources of information
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class RuleDefinition(Base):
    """Classification rule definitions"""
    __tablename__ = "rule_definitions"

    id = Column(Integer, primary_key=True, index=True)
    rule_name = Column(String, unique=True, nullable=False)
    rule_type = Column(String, nullable=False)  # "blacklist", "whitelist", "pattern"
    pattern = Column(String)  # Regex or keyword
    verdict = Column(SQLEnum(VerdictLabel))
    confidence = Column(Float, default=0.99)
    reason = Column(Text)
    active = Column(Boolean, default=True)
    priority = Column(Integer, default=0)  # Higher priority rules checked first
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class UserFeedback(Base):
    """User feedback on scan results"""
    __tablename__ = "user_feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    scan_id = Column(Integer, ForeignKey("scans.id"))

    agree = Column(Boolean)  # Does user agree with the verdict?
    suggested_verdict = Column(SQLEnum(VerdictLabel))
    comment = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="feedbacks")
    scan = relationship("Scan", back_populates="feedbacks")


class ManufacturerContact(Base):
    """Track manufacturer contact attempts"""
    __tablename__ = "manufacturer_contacts"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"))
    manufacturer_id = Column(Integer, ForeignKey("manufacturers.id"))

    email_sent = Column(Boolean, default=False)
    email_body = Column(Text)
    response_received = Column(Boolean, default=False)
    response_text = Column(Text)
    status = Column(String, default="pending")  # pending, sent, replied, no_reply

    sent_at = Column(DateTime)
    response_at = Column(DateTime)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
