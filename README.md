# FlexiPrice - Expiry-Based Dynamic Pricing System

An intelligent discount system that automatically adjusts product prices based on expiry dates using ML-powered recommendations.

## 🚀 Tech Stack

- **Backend**: FastAPI (Python 3.11)
- **Database**: PostgreSQL + Redis
- **Workers**: Celery
- **Frontend**: Next.js (React)
- **ML**: XGBoost/LightGBM
- **Infrastructure**: Docker, GitHub Actions

## 🏗️ Project Structure

```
FlexiPrice/
├── backend/              # FastAPI application
│   ├── app/
│   │   ├── main.py      # FastAPI entry point
│   │   ├── schemas/     # Pydantic schemas
│   │   ├── api/         # API routes
│   │   ├── core/        # Core configuration
│   │   └── services/    # Business logic
│   ├── prisma/          # Prisma schema
│   ├── tests/           # Backend tests
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/            # Next.js application
├── ml/                  # ML models & training
├── docker-compose.yml
└── README.md
```

## 🛠️ Development Setup

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Node.js 18+ (for frontend)

### Quick Start

1. **Clone and setup environment**:
   ```bash
   cd FlexiPrice
   cp backend/.env.example backend/.env
   ```

2. **Start services with Docker**:
   ```bash
   docker-compose up -d
   ```

3. **Access the application**:
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

### Local Development (without Docker)

1. **Setup Python virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On macOS/Linux
   ```

2. **Install dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Start PostgreSQL and Redis** (via Docker):
   ```bash
   docker-compose up -d postgres redis
   ```

4. **Run the application**:
   ```bash
   uvicorn app.main:app --reload
   ```

## 📚 API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Available Endpoints

#### Products (`/api/v1/admin/products`)
- `POST /api/v1/admin/products` - Create product
- `GET /api/v1/admin/products` - List products
- `GET /api/v1/admin/products/with-discounts` - Products with discount info
- `GET /api/v1/admin/products/{id}` - Get product by ID
- `PUT /api/v1/admin/products/{id}` - Update product
- `DELETE /api/v1/admin/products/{id}` - Delete product

#### Inventory (`/api/v1/admin/inventory`)
- `POST /api/v1/admin/inventory` - Add inventory batch
- `GET /api/v1/admin/inventory` - List batches
- `GET /api/v1/admin/inventory/expiring` - Get expiring batches
- `GET /api/v1/admin/inventory/product/{id}` - Get product batches
- `PUT /api/v1/admin/inventory/{id}` - Update batch
- `DELETE /api/v1/admin/inventory/{id}` - Delete batch

### Quick Test
```bash
# Run automated API tests
./scripts/test_api.sh
```

## 📋 Week 1 Goals

- [x] FastAPI skeleton with health check
- [x] Docker setup with Postgres & Redis
- [x] Database schema & models (Prisma + SQLAlchemy)
- [x] Product & inventory endpoints
- [x] Admin CRUD APIs with service layer
- [x] Discount calculation engine (rule-based)
- [ ] Celery scheduler setup
- [ ] Basic tests

## 📋 Week 2 Goals

- [x] **Day 1**: Discount engine with configurable rules ✅
- [ ] **Day 2**: Celery scheduler for auto-recomputation
- [ ] **Day 3**: Storefront price API endpoints
- [ ] **Day 4**: Redis caching + job monitoring

## 📝 License

MIT

## 👤 Author

Built with ❤️ for intelligent pricing
