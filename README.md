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
│   ├── app/             # Next.js App Router pages
│   ├── components/      # React components
│   ├── lib/             # API client & utilities
│   └── types/           # TypeScript types
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
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Frontend: http://localhost:3000
   - Health Check: http://localhost:8000/health

### Local Development (without Docker)

#### Backend

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

#### Frontend

1. **Install dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env.local
   # Edit .env.local with your API URL
   ```

3. **Start development server**:
   ```bash
   npm run dev
   # Or use the start script:
   ./start-dev.sh
   ```

4. **Access the frontend**:
   - Homepage: http://localhost:3000
   - Admin: http://localhost:3000/admin (token: `your-secret-admin-token-here`)

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

## 📋 Development Roadmap

### Week 1 — Backend Core ✅
- [x] FastAPI skeleton with health check
- [x] Docker setup with Postgres & Redis
- [x] Database schema & models (Prisma + SQLAlchemy)
- [x] Product & inventory endpoints
- [x] Admin CRUD APIs with service layer
- [x] Discount calculation engine (rule-based)

### Week 2 — Advanced Backend Features ✅
- [x] **Day 1**: Discount engine with configurable rules
- [x] **Day 2**: Batch discount processing
- [x] **Day 3**: Service layer & testing
- [x] **Day 4**: Redis caching + monitoring

### Week 3 — Frontend MVP (In Progress)
- [x] **Day 1**: Next.js skeleton
  - [x] Homepage with product grid
  - [x] Product detail pages
  - [x] Admin dashboard (token-protected)
  - [x] SWR integration for data fetching
- [ ] **Day 2**: Component polish & state management
- [ ] **Day 3**: Admin CRUD forms
- [ ] **Day 4**: Deploy to Vercel

### Week 4 — ML & Final Polish
- [ ] XGBoost training pipeline
- [ ] Price optimization
- [ ] Performance testing
- [ ] Documentation & deployment

## 🚢 Deployment

### Backend
- Docker container deployment
- Environment variables configuration
- Database migrations

### Frontend (Vercel)
1. Push to GitHub
2. Import project in Vercel
3. Set environment variables:
   - `NEXT_PUBLIC_API_URL`: Backend API URL
   - `ADMIN_TOKEN`: Admin authentication token
4. Deploy!

See `frontend/README.md` for detailed deployment instructions.

## 📝 License

MIT

## 👤 Author

Built with ❤️ for intelligent pricing
