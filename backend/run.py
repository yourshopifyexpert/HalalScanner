"""Production startup script for Railway deployment"""
import os
import uvicorn

if __name__ == "__main__":
    # Get port from environment variable (Railway sets this)
    port = int(os.getenv("PORT", 8000))

    print(f"Starting HalalScanner API on port {port}")

    # Run uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
