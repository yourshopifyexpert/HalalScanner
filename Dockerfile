FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (minimal for production)
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install dependencies
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application code
COPY backend ./backend

# Set working directory to backend
WORKDIR /app/backend

# Create database directory
RUN mkdir -p /app/backend/data

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app/backend
ENV PORT=8000

# Run the application
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
