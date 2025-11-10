"""Scan API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import base64
import uuid
from datetime import datetime
import logging

from app.database import get_db
from app.schemas import ScanRequest, ScanResponse
from app.services.ocr_chandra import ChandraOCRService
from app.services.normalizer_simple import IngredientNormalizer
from app.services.classifier import IngredientClassifier
from app.models import Scan, Product, User
from app.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=ScanResponse)
async def scan_product(
    request: ScanRequest,
    db: Session = Depends(get_db)
):
    """
    Scan a product and get halal classification

    Process:
    1. Extract text via OCR (if image provided)
    2. Normalize ingredients
    3. Classify ingredients using rules + ML
    4. Return verdict with evidence
    """
    try:
        # Get or create user
        user = db.query(User).filter(User.user_id == request.user_id).first()
        if not user:
            user = User(user_id=request.user_id)
            db.add(user)
            db.commit()
            db.refresh(user)

        # Step 1: OCR extraction (if needed)
        ocr_text = request.ocr_text
        ocr_confidence = 1.0

        if not ocr_text and (request.image_base64 or request.image_url):
            logger.info("Starting OCR extraction...")
            ocr_service = ChandraOCRService()

            try:
                if request.image_base64:
                    logger.info(f"Decoding base64 image, length: {len(request.image_base64)}")
                    # Decode base64 image
                    image_data = base64.b64decode(request.image_base64)
                    logger.info(f"Image decoded, size: {len(image_data)} bytes. Calling OCR...")

                    ocr_result = await ocr_service.extract_text_from_bytes(
                        image_data,
                        language_hint=request.language_hint
                    )
                    logger.info(f"OCR completed! Extracted text: {ocr_result.text[:100]}")
                elif request.image_url:
                    logger.info(f"Fetching image from URL: {request.image_url}")
                    ocr_result = await ocr_service.extract_text_from_url(
                        request.image_url,
                        language_hint=request.language_hint
                    )

                ocr_text = ocr_result.text
                ocr_confidence = ocr_result.confidence

                if ocr_confidence < settings.OCR_CONFIDENCE_THRESHOLD:
                    logger.warning(f"Low OCR confidence: {ocr_confidence}")

            except Exception as e:
                logger.error(f"OCR extraction failed: {e}", exc_info=True)
                # Return fallback text instead of failing
                ocr_text = "Ingredients: Unable to extract text. Please enter ingredients manually."
                ocr_confidence = 0.0

        if not ocr_text:
            raise HTTPException(
                status_code=400,
                detail="No text provided. Please provide OCR text or an image."
            )

        # Step 2: Normalize ingredients
        normalizer = IngredientNormalizer(db)
        normalized_ingredients = await normalizer.normalize(ocr_text)

        logger.info(f"Normalized {len(normalized_ingredients)} ingredients")

        # Step 3: Classify ingredients
        classifier = IngredientClassifier(db)
        classification_result = await classifier.classify(
            normalized_ingredients,
            manufacturer_name=None,  # TODO: Extract from barcode/product
            barcode=request.barcode
        )

        # Step 4: Get or create product (if barcode provided)
        product = None
        if request.barcode:
            product = db.query(Product).filter(Product.barcode == request.barcode).first()
            if not product:
                # Create new product
                product = Product(
                    product_id=str(uuid.uuid4()),
                    barcode=request.barcode,
                    name=f"Product {request.barcode}",  # TODO: Lookup product name
                )
                db.add(product)
                db.commit()
                db.refresh(product)

        # Step 5: Save scan to database
        scan = Scan(
            scan_id=str(uuid.uuid4()),
            user_id=user.id,
            product_id=product.id if product else None,
            image_url=request.image_url,
            ocr_text=ocr_text,
            ocr_confidence=ocr_confidence,
            ocr_language=request.language_hint,
            normalized_ingredients=[ing.dict() for ing in normalized_ingredients],
            verdict=classification_result.verdict,
            confidence=classification_result.confidence,
            explanation=[ev.dict() for ev in classification_result.evidence],
            scan_date=datetime.utcnow()
        )

        db.add(scan)
        db.commit()
        db.refresh(scan)

        # Step 6: Build response
        suggested_actions = []
        if classification_result.verdict in ["SUSPICIOUS", "UNKNOWN"]:
            suggested_actions.append("Ask manufacturer for clarification")
        if classification_result.confidence < 0.8:
            suggested_actions.append("Manual review recommended")

        response = ScanResponse(
            scan_id=scan.scan_id,
            product_id=product.product_id if product else None,
            product_name=product.name if product else None,
            barcode=request.barcode,
            verdict=classification_result.verdict,
            confidence=classification_result.confidence,
            explanation=classification_result.evidence,
            ocr_text=ocr_text,
            normalized_ingredients=[ing.canonical for ing in normalized_ingredients],
            suggested_actions=suggested_actions,
            manufacturer_name=None,  # TODO
            manufacturer_contact_available=False,  # TODO
            scan_date=scan.scan_date
        )

        return response

    except Exception as e:
        logger.error(f"Error processing scan: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload", response_model=ScanResponse)
async def upload_and_scan(
    file: UploadFile = File(...),
    user_id: str = "anonymous",
    barcode: str = None,
    language_hint: str = "en",
    db: Session = Depends(get_db)
):
    """
    Upload an image file and scan it
    """
    # Validate file type
    if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {settings.ALLOWED_IMAGE_TYPES}"
        )

    # Read file content
    image_data = await file.read()

    # Check file size
    if len(image_data) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE} bytes"
        )

    # Convert to base64
    image_base64 = base64.b64encode(image_data).decode('utf-8')

    # Create scan request
    scan_request = ScanRequest(
        image_base64=image_base64,
        user_id=user_id,
        barcode=barcode,
        language_hint=language_hint
    )

    # Process scan
    return await scan_product(scan_request, db)
