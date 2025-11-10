"""API routes"""
from fastapi import APIRouter
from app.api import scan, product, feedback, admin

api_router = APIRouter()

# Include sub-routers
api_router.include_router(scan.router, prefix="/scan", tags=["Scan"])
api_router.include_router(product.router, prefix="/product", tags=["Product"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["Feedback"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
