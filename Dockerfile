FROM python:3.11-slim

WORKDIR /app

# Copy backend requirements and install dependencies
COPY backend/requirements-production.txt ./requirements.txt
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

# Run the application using Python startup script
CMD ["python", "run.py"]
