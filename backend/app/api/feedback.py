"""Feedback API endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.schemas import FeedbackRequest, FeedbackResponse, ManufacturerContactRequest, ManufacturerContactResponse
from app.models import UserFeedback, Scan, User, ManufacturerContact, Product
from app.services.manufacturer_outreach import ManufacturerOutreachService

router = APIRouter()


@router.post("/", response_model=FeedbackResponse)
async def submit_feedback(
    request: FeedbackRequest,
    db: Session = Depends(get_db)
):
    """Submit user feedback on a scan result"""
    # Verify scan exists
    scan = db.query(Scan).filter(Scan.scan_id == request.scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    # Verify user exists
    user = db.query(User).filter(User.user_id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Create feedback
    feedback = UserFeedback(
        user_id=user.id,
        scan_id=scan.id,
        agree=request.agree,
        suggested_verdict=request.suggested_verdict,
        comment=request.comment
    )

    db.add(feedback)
    db.commit()
    db.refresh(feedback)

    return FeedbackResponse(
        feedback_id=feedback.id,
        message="Thank you for your feedback! It helps improve our accuracy."
    )


@router.post("/manufacturer-contact", response_model=ManufacturerContactResponse)
async def contact_manufacturer(
    request: ManufacturerContactRequest,
    db: Session = Depends(get_db)
):
    """Initiate contact with manufacturer for clarification"""
    # Verify scan exists
    scan = db.query(Scan).filter(Scan.scan_id == request.scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    # Verify product exists
    product = db.query(Product).filter(Product.product_id == request.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if not product.manufacturer:
        raise HTTPException(
            status_code=400,
            detail="Manufacturer information not available for this product"
        )

    if not product.manufacturer.email:
        raise HTTPException(
            status_code=400,
            detail="Manufacturer email not available"
        )

    # Create manufacturer contact record
    contact = ManufacturerContact(
        scan_id=scan.id,
        manufacturer_id=product.manufacturer.id,
        status="pending"
    )

    db.add(contact)
    db.commit()
    db.refresh(contact)

    # Send email asynchronously
    try:
        outreach_service = ManufacturerOutreachService(db)
        await outreach_service.send_inquiry(
            contact_id=contact.id,
            scan=scan,
            product=product,
            additional_message=request.additional_message
        )

        contact.email_sent = True
        contact.sent_at = datetime.utcnow()
        contact.status = "sent"
        db.commit()

        email_sent = True
        message = "Manufacturer inquiry sent successfully"
    except Exception as e:
        email_sent = False
        message = f"Failed to send inquiry: {str(e)}"
        contact.status = "failed"
        db.commit()

    return ManufacturerContactResponse(
        contact_id=contact.id,
        status=contact.status,
        message=message,
        email_sent=email_sent
    )
