"""Tests for API endpoints"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data


def test_scan_without_data():
    """Test scan endpoint without data"""
    response = client.post("/api/v1/scan/", json={
        "user_id": "test_user"
    })
    # Should return 400 or 500 due to missing image/text
    assert response.status_code in [400, 422, 500]


def test_invalid_product_id():
    """Test getting non-existent product"""
    response = client.get("/api/v1/product/invalid_id")
    assert response.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
