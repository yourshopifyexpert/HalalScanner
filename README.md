# HalalScanner - AI-Powered Halal Product Verification System

## Overview
HalalScanner is a comprehensive system that uses OCR, ML, and rules-based classification to determine if food products are halal-compliant. Users scan product labels with their mobile device, and the system analyzes ingredients to provide clear verdicts with evidence.

## Architecture

```
┌─────────────────┐
│   Mobile App    │
│ (React Native)  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│         Backend API (FastAPI)       │
├─────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐│
│  │ OCR Service  │  │ Normalizer   ││
│  └──────────────┘  └──────────────┘│
│  ┌──────────────┐  ┌──────────────┐│
│  │  Classifier  │  │ Manufacturer ││
│  │ (Rules + ML) │  │   Outreach   ││
│  └──────────────┘  └──────────────┘│
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  PostgreSQL + Elasticsearch + S3    │
└─────────────────────────────────────┘
```

## Components

### Mobile App (`/mobile`)
- Cross-platform React Native app
- Camera capture with auto-crop
- On-device OCR (Tesseract/ML Kit)
- Results display with evidence
- History and user feedback
- Privacy-first (local-only mode)

### Backend API (`/backend`)
- FastAPI-based REST API
- Microservices architecture
- Services:
  - **OCR Service**: Cloud-based OCR fallback
  - **Ingredient Normalizer**: Parse and normalize ingredient text
  - **Ingredient Classifier**: Rules engine + ML model
  - **Manufacturer Outreach**: Automated email inquiries
  - **Product Database**: Store scans and history

### Admin Console (`/admin`)
- Manage blacklists/whitelists
- Review uncertain items
- Handle manufacturer responses
- Analytics dashboard

## Tech Stack

**Frontend:**
- React Native (mobile)
- React (admin console)

**Backend:**
- Python 3.11+
- FastAPI
- SQLAlchemy (ORM)
- PostgreSQL
- Elasticsearch
- Redis (caching)

**ML/OCR:**
- Tesseract OCR
- Google Cloud Vision / AWS Textract
- PyTorch / HuggingFace Transformers
- spaCy (NLP)

**Infrastructure:**
- Docker & Docker Compose
- AWS S3 (image storage)
- RabbitMQ (message queue)

## Quick Start

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

### Mobile App
```bash
cd mobile
npm install
npx react-native run-android  # or run-ios
```

### Docker (Full Stack)
```bash
docker-compose up
```

## API Endpoints

- `POST /api/v1/scan` - Submit product scan
- `GET /api/v1/product/{id}` - Get product details
- `POST /api/v1/feedback` - Submit user feedback
- `POST /api/v1/product/{id}/manufacturer-contact` - Contact manufacturer
- `GET /api/v1/admin/uncertain` - List uncertain items (admin)

## Classification Logic

1. **OCR Extraction**: Extract text from label image
2. **Normalization**: Parse ingredients, expand abbreviations, map to canonical names
3. **Rules Engine**: Check against blacklist (haram) and whitelist (halal)
4. **ML Classification**: Classify ambiguous ingredients
5. **Certification Check**: Verify halal certifications
6. **Decision**: Produce label (HALAL/HARAM/SUSPICIOUS/UNKNOWN) with confidence

## Development Roadmap

- [x] System design
- [ ] MVP (Sprints 1-4)
  - [ ] Backend API + rules engine
  - [ ] Mobile app with camera + OCR
  - [ ] Basic manufacturer outreach
- [ ] Phase 2
  - [ ] ML classifier training
  - [ ] Multi-language support
  - [ ] Certification database
- [ ] Phase 3
  - [ ] Advanced features
  - [ ] Enterprise API
  - [ ] Fraud detection

## License
MIT

## Contributing
See CONTRIBUTING.md for guidelines.
