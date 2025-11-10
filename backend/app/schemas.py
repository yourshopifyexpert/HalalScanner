"""Pydantic schemas for API request/response validation"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class VerdictLabel(str, Enum):
    """Product verdict labels"""
    HALAL = "HALAL"
    HARAM = "HARAM"
    SUSPICIOUS = "SUSPICIOUS"
    UNKNOWN = "UNKNOWN"


class HalalStatus(str, Enum):
    """Ingredient halal status"""
    HALAL = "HALAL"
    HARAM = "HARAM"
    AMBIGUOUS = "AMBIGUOUS"
    UNKNOWN = "UNKNOWN"


# Request Schemas
class ScanRequest(BaseModel):
    """Request schema for product scan"""
    image_base64: Optional[str] = None
    image_url: Optional[str] = None
    barcode: Optional[str] = None
    ocr_text: Optional[str] = None
    user_id: str
    language_hint: str = "en"


class FeedbackRequest(BaseModel):
    """Request schema for user feedback"""
    scan_id: str
    user_id: str
    agree: bool
    suggested_verdict: Optional[VerdictLabel] = None
    comment: Optional[str] = None


class ManufacturerContactRequest(BaseModel):
    """Request schema for contacting manufacturer"""
    scan_id: str
    product_id: str
    additional_message: Optional[str] = None


# Response Schemas
class IngredientEvidence(BaseModel):
    """Evidence for an ingredient classification"""
    ingredient: str
    normalized_name: str
    status: HalalStatus
    reason: str
    rule_name: Optional[str] = None
    confidence: float


class ScanResponse(BaseModel):
    """Response schema for scan result"""
    scan_id: str
    product_id: Optional[str] = None
    product_name: Optional[str] = None
    barcode: Optional[str] = None

    verdict: VerdictLabel
    confidence: float
    explanation: List[IngredientEvidence]

    ocr_text: Optional[str] = None
    normalized_ingredients: List[str]

    suggested_actions: List[str] = []
    manufacturer_name: Optional[str] = None
    manufacturer_contact_available: bool = False

    scan_date: datetime

    class Config:
        from_attributes = True


class ProductResponse(BaseModel):
    """Response schema for product details"""
    product_id: str
    name: str
    barcode: Optional[str] = None
    manufacturer_name: Optional[str] = None
    category: Optional[str] = None

    latest_verdict: VerdictLabel
    confidence: float
    scan_count: int

    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProductDetailResponse(ProductResponse):
    """Detailed product response with scan history"""
    scans: List[ScanResponse] = []
    certifications: List[Dict[str, Any]] = []


class FeedbackResponse(BaseModel):
    """Response schema for feedback submission"""
    feedback_id: int
    message: str = "Feedback received successfully"


class ManufacturerContactResponse(BaseModel):
    """Response schema for manufacturer contact"""
    contact_id: int
    status: str
    message: str
    email_sent: bool


class UncertainItemResponse(BaseModel):
    """Response for uncertain/suspicious items (admin)"""
    scan_id: str
    product_name: str
    verdict: VerdictLabel
    confidence: float
    ambiguous_ingredients: List[str]
    scan_count: int
    scan_date: datetime


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    services: Dict[str, bool]


# Internal Schemas
class NormalizedIngredient(BaseModel):
    """Normalized ingredient structure"""
    original: str
    canonical: str
    aliases: List[str] = []
    confidence: float


class OCRResult(BaseModel):
    """OCR extraction result"""
    text: str
    confidence: float
    language: str
    bounding_boxes: Optional[List[Dict[str, Any]]] = None


class ClassificationResult(BaseModel):
    """Classification result from classifier service"""
    verdict: VerdictLabel
    confidence: float
    evidence: List[IngredientEvidence]
    reasoning: str
