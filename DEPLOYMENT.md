# HalalScanner Deployment Guide

## Prerequisites

- Docker & Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)
- PostgreSQL 15+ (if not using Docker)
- AWS account (for S3 image storage - optional)
- SMTP credentials (for manufacturer outreach - optional)

## Quick Start with Docker

The easiest way to run the entire stack:

```bash
# Clone the repository
git clone <repo-url>
cd HalalScanner

# Create .env file
cp backend/.env.example backend/.env
# Edit backend/.env with your configuration

# Start all services
docker-compose up -d

# Initialize database
docker-compose exec backend python app/seed_data.py

# Access services:
# - Backend API: http://localhost:8000
# - Admin Console: http://localhost:3000
# - API Docs: http://localhost:8000/docs
```

## Production Deployment

### 1. Backend API Deployment

#### Option A: Docker (Recommended)

```bash
cd backend

# Build image
docker build -t halalscanner-backend:latest .

# Run with production settings
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL="postgresql://user:pass@host:5432/db" \
  -e REDIS_URL="redis://host:6379/0" \
  -e SECRET_KEY="your-secret-key" \
  -e ENVIRONMENT="production" \
  -e DEBUG="False" \
  halalscanner-backend:latest
```

#### Option B: Manual Deployment

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Initialize database
python app/seed_data.py

# Run with Gunicorn (production)
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

### 2. Database Setup

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database and user
CREATE DATABASE halalscanner;
CREATE USER halaluser WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE halalscanner TO halaluser;
```

### 3. Admin Console Deployment

```bash
cd admin

# Install dependencies
npm install

# Build for production
npm run build

# Serve with nginx or any static file server
# Files will be in ./build directory
```

#### Nginx Configuration

```nginx
server {
    listen 80;
    server_name admin.halalscanner.com;

    root /var/www/halalscanner-admin;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 4. Mobile App Deployment

#### Android

```bash
cd mobile

# Install dependencies
npm install

# Build release APK
cd android
./gradlew assembleRelease

# APK will be in: android/app/build/outputs/apk/release/
```

#### iOS

```bash
cd mobile

# Install dependencies
npm install
cd ios && pod install && cd ..

# Open in Xcode
open ios/HalalScanner.xcworkspace

# Build for release in Xcode
```

## Environment Variables

### Backend (.env)

```bash
# Database
DATABASE_URL=postgresql://user:pass@host:5432/halalscanner

# Redis
REDIS_URL=redis://host:6379/0

# Elasticsearch (optional)
ELASTICSEARCH_URL=http://host:9200

# AWS S3
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
S3_BUCKET=halalscanner-uploads

# Google Cloud Vision (optional)
GOOGLE_CLOUD_VISION_API_KEY=your_key

# Email (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Security
SECRET_KEY=generate-a-secure-random-key

# Application
ENVIRONMENT=production
DEBUG=False
```

### Mobile App

Edit `mobile/src/config/api.ts`:

```typescript
export const API_BASE_URL = 'https://api.halalscanner.com';
```

## Kubernetes Deployment (Optional)

```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/

# Services will be created:
# - Backend API
# - PostgreSQL
# - Redis
# - Admin Console
```

## Monitoring & Logging

### Application Logs

```bash
# Docker logs
docker-compose logs -f backend

# View specific service
docker-compose logs -f postgres
```

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Database check
docker-compose exec postgres pg_isready
```

## Backup & Recovery

### Database Backup

```bash
# Backup
docker-compose exec postgres pg_dump -U halaluser halalscanner > backup.sql

# Restore
docker-compose exec -T postgres psql -U halaluser halalscanner < backup.sql
```

### S3 Backup

Images are stored in S3 with versioning enabled (recommended).

## Scaling Considerations

### Backend Scaling

- Run multiple backend instances behind a load balancer
- Use Redis for session management
- Configure Celery for async tasks (manufacturer outreach)

### Database Scaling

- Enable read replicas for PostgreSQL
- Use connection pooling (pgBouncer)
- Implement caching with Redis

### Mobile App

- Use CDN for API endpoints
- Implement offline mode
- Cache OCR results locally

## Security Checklist

- [ ] Change default passwords
- [ ] Enable HTTPS/TLS
- [ ] Configure firewall rules
- [ ] Enable rate limiting
- [ ] Set up monitoring and alerts
- [ ] Regular security updates
- [ ] Backup strategy in place
- [ ] API key rotation policy
- [ ] GDPR/CCPA compliance review

## Troubleshooting

### Backend won't start

- Check database connection
- Verify environment variables
- Check logs: `docker-compose logs backend`

### OCR not working

- Ensure Tesseract is installed
- Check image format and size
- Verify Google Cloud Vision API key (if using)

### Database connection errors

- Check PostgreSQL is running
- Verify DATABASE_URL format
- Check network connectivity

## Support

For issues and questions:
- GitHub Issues: <repo-url>/issues
- Documentation: docs/
- Email: support@halalscanner.com
