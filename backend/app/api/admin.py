"""Admin API endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List

from app.database import get_db
from app.schemas import UncertainItemResponse, VerdictLabel
from app.models import Scan, Product, RuleDefinition

router = APIRouter()


@router.get("/uncertain", response_model=List[UncertainItemResponse])
async def get_uncertain_items(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get list of uncertain/suspicious items for manual review"""
    # Get scans with SUSPICIOUS or UNKNOWN verdicts
    scans = db.query(Scan).filter(
        Scan.verdict.in_([VerdictLabel.SUSPICIOUS, VerdictLabel.UNKNOWN])
    ).order_by(desc(Scan.scan_date)).offset(skip).limit(limit).all()

    result = []
    for scan in scans:
        # Extract ambiguous ingredients from explanation
        ambiguous_ingredients = []
        if scan.explanation:
            for item in scan.explanation:
                if isinstance(item, dict) and item.get('status') in ['AMBIGUOUS', 'UNKNOWN']:
                    ambiguous_ingredients.append(item.get('ingredient', ''))

        # Count total scans for this product
        scan_count = 1
        if scan.product_id:
            scan_count = db.query(Scan).filter(
                Scan.product_id == scan.product_id
            ).count()

        result.append(UncertainItemResponse(
            scan_id=scan.scan_id,
            product_name=scan.product.name if scan.product else "Unknown Product",
            verdict=scan.verdict,
            confidence=scan.confidence,
            ambiguous_ingredients=ambiguous_ingredients,
            scan_count=scan_count,
            scan_date=scan.scan_date
        ))

    return result


@router.get("/rules")
async def get_rules(
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """Get all classification rules"""
    query = db.query(RuleDefinition)

    if active_only:
        query = query.filter(RuleDefinition.active == True)

    rules = query.order_by(desc(RuleDefinition.priority)).all()

    return [
        {
            "id": rule.id,
            "rule_name": rule.rule_name,
            "rule_type": rule.rule_type,
            "pattern": rule.pattern,
            "verdict": rule.verdict,
            "confidence": rule.confidence,
            "reason": rule.reason,
            "active": rule.active,
            "priority": rule.priority
        }
        for rule in rules
    ]


@router.post("/rules")
async def create_rule(
    rule_data: dict,
    db: Session = Depends(get_db)
):
    """Create a new classification rule"""
    rule = RuleDefinition(**rule_data)
    db.add(rule)
    db.commit()
    db.refresh(rule)

    return {"id": rule.id, "message": "Rule created successfully"}


@router.put("/rules/{rule_id}")
async def update_rule(
    rule_id: int,
    rule_data: dict,
    db: Session = Depends(get_db)
):
    """Update an existing rule"""
    rule = db.query(RuleDefinition).filter(RuleDefinition.id == rule_id).first()

    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    for key, value in rule_data.items():
        setattr(rule, key, value)

    db.commit()

    return {"message": "Rule updated successfully"}


@router.delete("/rules/{rule_id}")
async def delete_rule(
    rule_id: int,
    db: Session = Depends(get_db)
):
    """Delete a rule (soft delete by setting active=False)"""
    rule = db.query(RuleDefinition).filter(RuleDefinition.id == rule_id).first()

    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    rule.active = False
    db.commit()

    return {"message": "Rule deactivated successfully"}
