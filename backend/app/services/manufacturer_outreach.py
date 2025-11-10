"""Manufacturer Outreach Service"""
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sqlalchemy.orm import Session
from typing import Optional

from app.models import ManufacturerContact, Scan, Product, Manufacturer
from app.config import settings

logger = logging.getLogger(__name__)


class ManufacturerOutreachService:
    """Service for automated manufacturer contact and inquiry"""

    def __init__(self, db: Session):
        self.db = db

    async def send_inquiry(
        self,
        contact_id: int,
        scan: Scan,
        product: Product,
        additional_message: Optional[str] = None
    ) -> bool:
        """Send inquiry email to manufacturer"""

        if not product.manufacturer or not product.manufacturer.email:
            raise ValueError("Manufacturer email not available")

        manufacturer = product.manufacturer

        # Generate email content
        subject = f"Halal Certification Inquiry - {product.name}"
        body = self._generate_email_body(
            manufacturer=manufacturer,
            product=product,
            scan=scan,
            additional_message=additional_message
        )

        try:
            # Send email
            success = await self._send_email(
                to_email=manufacturer.email,
                subject=subject,
                body=body
            )

            if success:
                # Update contact record
                contact = self.db.query(ManufacturerContact).filter(
                    ManufacturerContact.id == contact_id
                ).first()

                if contact:
                    contact.email_body = body
                    self.db.commit()

                logger.info(f"Successfully sent inquiry to {manufacturer.name}")
                return True
            else:
                logger.error(f"Failed to send inquiry to {manufacturer.name}")
                return False

        except Exception as e:
            logger.error(f"Error sending inquiry email: {e}", exc_info=True)
            return False

    def _generate_email_body(
        self,
        manufacturer: Manufacturer,
        product: Product,
        scan: Scan,
        additional_message: Optional[str] = None
    ) -> str:
        """Generate inquiry email body"""

        # Extract ambiguous ingredients
        ambiguous_ingredients = []
        if scan.explanation:
            for item in scan.explanation:
                if isinstance(item, dict) and item.get('status') in ['AMBIGUOUS', 'UNKNOWN']:
                    ambiguous_ingredients.append(item.get('ingredient', ''))

        body = f"""Dear {manufacturer.name} Team,

Assalamu Alaikum / Peace be upon you,

We are reaching out on behalf of a consumer who is inquiring about the halal status of the following product:

Product Name: {product.name}
{f'Barcode: {product.barcode}' if product.barcode else ''}

The consumer has scanned this product using our halal verification app and would like clarification on the following ingredients:

{chr(10).join(f"- {ing}" for ing in ambiguous_ingredients[:10])}

We would greatly appreciate if you could provide information on:

1. Whether this product is certified halal by a recognized certification body
2. The source of any animal-derived ingredients (especially gelatin, enzymes, glycerin, and emulsifiers)
3. Whether any alcohol is used in processing or as an ingredient
4. Any relevant halal certification details (certificate number, certifying body, expiration date)

"""

        if additional_message:
            body += f"""
Additional message from consumer:
{additional_message}

"""

        body += """
Your response will help consumers make informed decisions about product purchases. We will update our database with your information to assist other users as well.

Thank you for your time and cooperation.

Best regards,
HalalScanner Team

---
This is an automated inquiry sent via the HalalScanner app.
To update your product information or provide certification details, please reply to this email.
"""

        return body

    async def _send_email(
        self,
        to_email: str,
        subject: str,
        body: str
    ) -> bool:
        """Send email via SMTP"""

        if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
            logger.warning("SMTP credentials not configured, email not sent")
            return False

        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = settings.SMTP_FROM
            msg['To'] = to_email
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'plain'))

            # Connect to SMTP server
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)

            return True

        except Exception as e:
            logger.error(f"SMTP error: {e}", exc_info=True)
            return False

    async def process_reply(
        self,
        contact_id: int,
        reply_text: str
    ) -> bool:
        """Process manufacturer reply (for future automation)"""
        # TODO: Implement reply processing
        # - Parse reply for certification details
        # - Extract halal status
        # - Update product database
        # - Notify user

        contact = self.db.query(ManufacturerContact).filter(
            ManufacturerContact.id == contact_id
        ).first()

        if not contact:
            return False

        contact.response_received = True
        contact.response_text = reply_text
        contact.status = "replied"
        self.db.commit()

        logger.info(f"Processed reply for contact {contact_id}")
        return True
