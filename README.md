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
│   │   ├── models/      # SQLAlchemy models
│   │   ├── schemas/     # Pydantic schemas
│   │   ├── api/         # API routes
│   │   ├── core/        # Core configuration
│   │   └── services/    # Business logic
│   ├── alembic/         # Database migrations
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

## 📋 Week 1 Goals

- [x] FastAPI skeleton with health check
- [x] Docker setup with Postgres & Redis
- [ ] Database schema & models
- [ ] Product & inventory endpoints
- [ ] Basic tests
- [ ] Alembic migrations

## 📝 License

MIT

## 👤 Author

Built with ❤️ for intelligent pricing
