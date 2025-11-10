"""Product API endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List

from app.database import get_db
from app.schemas import ProductResponse, ProductDetailResponse, ScanResponse
from app.models import Product, Scan, Manufacturer

router = APIRouter()


@router.get("/{product_id}", response_model=ProductDetailResponse)
async def get_product(
    product_id: str,
    db: Session = Depends(get_db)
):
    """Get detailed product information including scan history"""
    product = db.query(Product).filter(Product.product_id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Get latest scan for verdict
    latest_scan = db.query(Scan).filter(
        Scan.product_id == product.id
    ).order_by(desc(Scan.scan_date)).first()

    if not latest_scan:
        raise HTTPException(status_code=404, detail="No scans found for this product")

    # Get all scans
    scans = db.query(Scan).filter(
        Scan.product_id == product.id
    ).order_by(desc(Scan.scan_date)).limit(10).all()

    # Build response
    response = ProductDetailResponse(
        product_id=product.product_id,
        name=product.name,
        barcode=product.barcode,
        manufacturer_name=product.manufacturer.name if product.manufacturer else None,
        category=product.category,
        latest_verdict=latest_scan.verdict,
        confidence=latest_scan.confidence,
        scan_count=len(scans),
        created_at=product.created_at,
        updated_at=product.updated_at,
        scans=[],  # TODO: Convert scans to ScanResponse
        certifications=[]  # TODO: Get certifications
    )

    return response


@router.get("/barcode/{barcode}", response_model=ProductResponse)
async def get_product_by_barcode(
    barcode: str,
    db: Session = Depends(get_db)
):
    """Get product by barcode"""
    product = db.query(Product).filter(Product.barcode == barcode).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Get latest scan
    latest_scan = db.query(Scan).filter(
        Scan.product_id == product.id
    ).order_by(desc(Scan.scan_date)).first()

    scan_count = db.query(Scan).filter(Scan.product_id == product.id).count()

    response = ProductResponse(
        product_id=product.product_id,
        name=product.name,
        barcode=product.barcode,
        manufacturer_name=product.manufacturer.name if product.manufacturer else None,
        category=product.category,
        latest_verdict=latest_scan.verdict if latest_scan else "UNKNOWN",
        confidence=latest_scan.confidence if latest_scan else 0.0,
        scan_count=scan_count,
        created_at=product.created_at,
        updated_at=product.updated_at
    )

    return response


@router.get("/", response_model=List[ProductResponse])
async def list_products(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """List all products"""
    products = db.query(Product).offset(skip).limit(limit).all()

    result = []
    for product in products:
        latest_scan = db.query(Scan).filter(
            Scan.product_id == product.id
        ).order_by(desc(Scan.scan_date)).first()

        scan_count = db.query(Scan).filter(Scan.product_id == product.id).count()

        result.append(ProductResponse(
            product_id=product.product_id,
            name=product.name,
            barcode=product.barcode,
            manufacturer_name=product.manufacturer.name if product.manufacturer else None,
            category=product.category,
            latest_verdict=latest_scan.verdict if latest_scan else "UNKNOWN",
            confidence=latest_scan.confidence if latest_scan else 0.0,
            scan_count=scan_count,
            created_at=product.created_at,
            updated_at=product.updated_at
        ))

    return result
