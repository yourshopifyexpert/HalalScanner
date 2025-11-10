# HalalScanner System Architecture

## Overview

HalalScanner is a comprehensive AI-powered system for verifying the halal status of food products through ingredient analysis. The system uses OCR, NLP, rules-based classification, and machine learning to provide accurate verdicts.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      MOBILE APPS                            │
│              (iOS & Android - React Native)                 │
└────────────────┬────────────────────────────────────────────┘
                 │ HTTPS/REST API
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                    API GATEWAY / LOAD BALANCER              │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                  BACKEND API (FastAPI)                      │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ OCR Service  │  │ Normalizer   │  │ Classifier   │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐                       │
│  │ Rules Engine │  │ ML Model     │                       │
│  └──────────────┘  └──────────────┘                       │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                   DATA LAYER                                │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ PostgreSQL   │  │ Redis Cache  │  │ Elasticsearch│    │
│  │ (Primary DB) │  │              │  │ (Search)     │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐                       │
│  │ AWS S3       │  │ RabbitMQ     │                       │
│  │ (Images)     │  │ (Queue)      │                       │
│  └──────────────┘  └──────────────┘                       │
└─────────────────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                  ADMIN CONSOLE (React)                      │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Mobile Application

**Technology**: React Native (Cross-platform)

**Responsibilities**:
- Camera capture and image preprocessing
- Local OCR (Tesseract/ML Kit) for offline mode
- Display results with visual evidence
- Manage scan history locally
- User feedback collection
- Privacy-first design (local-only mode)

**Key Features**:
- Auto-crop and image enhancement
- Barcode scanning
- Offline capability
- Result caching
- History management

### 2. Backend API

**Technology**: Python 3.11, FastAPI

**Architecture**: Microservices-style modular design

#### 2.1 OCR Service
- **Local OCR**: Tesseract with image preprocessing
- **Cloud OCR**: Google Cloud Vision / AWS Textract (fallback)
- **Preprocessing**: Deskew, denoise, adaptive thresholding
- **Language Support**: English, Arabic, Urdu, Turkish, etc.

#### 2.2 Ingredient Normalizer
- **Text Parsing**: Extract ingredient list from raw OCR text
- **Tokenization**: Split into individual ingredients
- **Normalization**: Expand abbreviations, remove quantities
- **Canonicalization**: Map to standard ingredient names
- **Database Matching**: Fuzzy matching with master ingredient DB

#### 2.3 Classification Engine

**Rules Engine** (Priority System):
1. **Blacklist Rules** (Highest priority)
   - Pork and derivatives
   - Alcohol
   - Blood products
   - Explicitly haram ingredients

2. **Whitelist Rules**
   - Plant-based ingredients
   - Minerals and water
   - Clearly halal items

3. **Pattern Matching**
   - Regex-based matching
   - E-number classification
   - Ambiguous markers

**ML Model** (Future Enhancement):
- Transformer-based classifier
- Fine-tuned on labeled ingredient samples
- Handles ambiguous cases
- Confidence scoring

**Decision Logic**:
```python
if any(ingredient == HARAM):
    verdict = HARAM
elif has_certification and all_known:
    verdict = HALAL
elif any(ingredient == AMBIGUOUS):
    verdict = SUSPICIOUS
elif many_unknowns:
    verdict = UNKNOWN
else:
    verdict = HALAL
```

#### 2.4 Manufacturer Outreach Service
- Automated email generation
- Template-based inquiries
- Response tracking
- Integration with ticketing system

### 3. Data Storage

#### PostgreSQL (Primary Database)
**Schema**:
- `users`: User profiles and preferences
- `products`: Product information and barcodes
- `scans`: Scan history and results
- `ingredient_master`: Canonical ingredient database
- `manufacturers`: Manufacturer information
- `halal_certifications`: Certification records
- `rule_definitions`: Classification rules
- `user_feedbacks`: User feedback data

#### Redis (Cache & Session)
- API response caching
- Session management
- Rate limiting
- Real-time counters

#### Elasticsearch (Search & Analytics)
- Product search
- Ingredient fuzzy matching
- Analytics and reporting
- Full-text search

#### AWS S3 (Object Storage)
- Scan images
- OCR results
- ML model artifacts
- Backup data

### 4. Admin Console

**Technology**: React, Material-UI

**Features**:
- Dashboard with statistics
- Rules management (CRUD)
- Uncertain items review
- Ingredient database management
- Manufacturer database
- Certification tracking
- Analytics and reports

## Data Flow

### Scan Processing Flow

```
1. User captures image
   ↓
2. Mobile app preprocessing
   - Crop, rotate, enhance
   ↓
3. Local OCR attempt
   - Fast, offline
   ↓
4. If confidence < threshold
   → Upload to backend
   ↓
5. Backend OCR (cloud)
   - Higher accuracy
   ↓
6. Ingredient Normalization
   - Parse text
   - Extract ingredients
   - Normalize tokens
   ↓
7. Classification
   - Rules engine check
   - ML model inference
   - Certification lookup
   ↓
8. Verdict Generation
   - Combine evidence
   - Calculate confidence
   - Generate explanation
   ↓
9. Return result to app
   ↓
10. Display to user
    - Show verdict
    - Evidence list
    - Suggested actions
```

## Security Architecture

### Authentication & Authorization
- User ID generation (anonymous)
- Optional email authentication
- Admin role-based access control (RBAC)

### Data Protection
- TLS/HTTPS for all API calls
- Image encryption at rest (S3 KMS)
- PII encryption in database
- Privacy mode (local-only processing)

### API Security
- Rate limiting (Redis)
- Input validation (Pydantic)
- SQL injection prevention (SQLAlchemy ORM)
- XSS protection
- CORS configuration

## Scalability

### Horizontal Scaling
- Stateless backend API (scale with load balancer)
- Database read replicas
- Redis cluster for caching
- S3 for distributed storage

### Performance Optimization
- CDN for static assets
- Database indexing (products, ingredients)
- Query optimization
- Connection pooling
- Async I/O (FastAPI)

### Caching Strategy
```
L1: Mobile app cache (scan results)
L2: Redis cache (API responses)
L3: Database query cache
L4: CDN cache (static assets)
```

## Monitoring & Observability

### Metrics
- API response times
- Error rates
- Classification accuracy
- User engagement
- Resource utilization

### Logging
- Structured JSON logs
- Log aggregation (ELK stack)
- Error tracking (Sentry)
- Audit trails

### Alerts
- Service health checks
- Error rate thresholds
- Database performance
- API quota limits

## Deployment Architecture

### Development
```
Docker Compose:
- Backend API
- PostgreSQL
- Redis
- Elasticsearch
- RabbitMQ
- Admin Console
```

### Production (Kubernetes)
```
Namespaces:
- halalscanner-prod
  - backend-api (3 replicas)
  - postgres (StatefulSet)
  - redis (StatefulSet)
  - elasticsearch (StatefulSet)
  - admin (2 replicas)
  - ingress-nginx
```

## Future Enhancements

### Phase 2
- ML model training pipeline
- Multi-language support (full)
- Barcode database integration
- Community contributions
- Browser extension

### Phase 3
- Real-time certification verification
- Blockchain-based ingredient tracking
- Advanced fraud detection
- Enterprise API
- White-label solutions

## Technology Stack Summary

**Frontend**:
- React Native (Mobile)
- React + Material-UI (Admin)
- TypeScript

**Backend**:
- Python 3.11
- FastAPI
- SQLAlchemy
- Pydantic

**AI/ML**:
- Tesseract OCR
- spaCy (NLP)
- PyTorch (ML models)
- Google Cloud Vision

**Infrastructure**:
- Docker
- Kubernetes
- PostgreSQL
- Redis
- Elasticsearch
- RabbitMQ
- AWS S3

**DevOps**:
- GitHub Actions (CI/CD)
- Prometheus (Monitoring)
- Grafana (Dashboards)
- Sentry (Error tracking)

## API Design

### RESTful Endpoints

```
POST   /api/v1/scan                    - Submit scan
GET    /api/v1/product/{id}            - Get product
POST   /api/v1/feedback                - Submit feedback
POST   /api/v1/feedback/manufacturer-contact - Contact manufacturer
GET    /api/v1/admin/uncertain         - List uncertain items
GET    /api/v1/admin/rules             - List rules
POST   /api/v1/admin/rules             - Create rule
PUT    /api/v1/admin/rules/{id}        - Update rule
DELETE /api/v1/admin/rules/{id}        - Delete rule
```

### Response Format

```json
{
  "scan_id": "uuid",
  "verdict": "HALAL|HARAM|SUSPICIOUS|UNKNOWN",
  "confidence": 0.95,
  "explanation": [
    {
      "ingredient": "Sugar",
      "status": "HALAL",
      "reason": "Plant-based",
      "confidence": 0.99
    }
  ],
  "suggested_actions": ["..."]
}
```

## Conclusion

HalalScanner is designed as a scalable, maintainable, and accurate system for halal verification. The modular architecture allows for independent scaling and easy feature additions. The privacy-first design ensures user trust, while the rules-based + ML approach provides both accuracy and explainability.
