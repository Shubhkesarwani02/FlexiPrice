# FlexiPrice - Dynamic Expiry-Based Pricing System

[![Status](https://img.shields.io/badge/status-production--ready-brightgreen)]()
[![Tests](https://img.shields.io/badge/tests-18%2F18_passing-success)]()
[![Python](https://img.shields.io/badge/python-3.11+-blue)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-teal)]()
[![Next.js](https://img.shields.io/badge/Next.js-16-black)]()

> **Intelligent inventory management and dynamic pricing platform** that reduces food waste through ML-powered, expiry-aware discount recommendations. Built with FastAPI, PostgreSQL, Next.js, and XGBoost.

---

## 🎯 Overview

FlexiPrice is an enterprise-grade dynamic pricing system designed for perishable goods retailers. It automatically adjusts product prices based on expiry dates, inventory levels, and historical sales data to maximize revenue while minimizing waste.

### Key Features

- 🤖 **ML-Powered Recommendations** - XGBoost model predicts optimal discount levels
- ⚡ **Real-Time Price Computation** - Rule-based engine + ML suggestions  
- 📊 **Comprehensive Analytics** - Sales trends, conversion metrics, A/B test results
- 🧪 **A/B Testing Framework** - Compare rule-based vs ML-driven pricing
- 🔄 **Automated Batch Processing** - Celery workers handle bulk discount calculations
- 🎨 **Modern Admin Dashboard** - Next.js frontend with real-time updates
- 🐳 **Fully Dockerized** - Production-ready containerized deployment

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (Next.js 16)                   │
│  ┌────────────┬───────────────┬─────────────────────────┐  │
│  │ Storefront │ Admin Panel   │ Analytics Dashboard     │  │
│  │ (Products) │ (Management)  │ (Charts & Metrics)      │  │
│  └────────────┴───────────────┴─────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │ REST API
┌────────────────────────▼────────────────────────────────────┐
│              Backend API (FastAPI + Python 3.11)            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Product Management  │  Inventory Tracking           │  │
│  │  Discount Engine     │  ML Predictions               │  │
│  │  Analytics Service   │  A/B Testing                  │  │
│  └──────────────────────────────────────────────────────┘  │
└────────┬────────────────────┬────────────────────┬──────────┘
         │                    │                    │
┌────────▼────────┐  ┌────────▼────────┐  ┌───────▼──────────┐
│  PostgreSQL 15  │  │   Redis Cache   │  │  Celery Workers  │
│  (Prisma ORM)   │  │   (Broker)      │  │  (Batch Jobs)    │
└─────────────────┘  └─────────────────┘  └──────────────────┘
```

### Technology Stack

**Backend:**
- FastAPI 0.104+ - High-performance async API framework
- Python 3.11+ - Modern Python with type hints
- Prisma Client - Type-safe ORM for PostgreSQL
- PostgreSQL 15 - Robust relational database  
- Redis 7 - In-memory cache and message broker
- Celery - Distributed task queue for batch processing
- XGBoost - ML model for purchase probability prediction

**Frontend:**
- Next.js 16 - React framework with Turbopack
- TypeScript - Type-safe frontend development
- TailwindCSS 4 - Utility-first styling
- SWR - Data fetching and caching
- Recharts - Analytics visualizations

**DevOps:**
- Docker & Docker Compose - Containerization
- GitHub Actions ready - CI/CD pipeline support

---

## 🚀 Quick Start

### Prerequisites

- Docker Desktop or Docker Engine 20.10+
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)

### Option 1: One-Command Setup

```bash
# Clone and start everything
git clone https://github.com/Shubhkesarwani02/FlexiPrice.git
cd FlexiPrice
./scripts/quick_start.sh
```

### Option 2: Manual Setup

```bash
# 1. Start backend services
docker-compose up -d

# 2. Wait for services to be ready (30 seconds)
sleep 30

# 3. Verify backend
curl http://localhost:8000/health
# Expected: {"status":"ok","service":"flexiprice-api","version":"0.1.0"}

# 4. Start frontend
cd frontend
npm install
npm run dev

# 5. Access the application
# - Frontend: http://localhost:3000
# - Admin Panel: http://localhost:3000/admin
# - API Docs: http://localhost:8000/docs
```

### Verify Installation

```bash
# Run comprehensive system validation
python3 backend/scripts/quick_validation.py

# Expected output: "18/18 tests passed - System fully operational!"
```

---

## 📖 API Documentation

### Core Endpoints

#### Product Management
```http
GET    /api/v1/admin/products          # List all products with computed prices
POST   /api/v1/admin/products          # Create new product
GET    /api/v1/admin/products/{sku}    # Get product details
PUT    /api/v1/admin/products/{sku}    # Update product
```

#### Inventory Management
```http
GET    /api/v1/admin/inventory         # List all inventory batches
POST   /api/v1/admin/inventory         # Add new batch with expiry
GET    /api/v1/admin/inventory/{id}    # Get batch details
PUT    /api/v1/admin/inventory/{id}    # Update batch quantity
```

#### Discount Engine
```http
GET    /api/v1/admin/discounts         # List active discounts
POST   /api/v1/admin/discounts/compute/{batch_id}  # Compute discount
GET    /api/v1/admin/discounts/preview/{batch_id}  # Preview discount
POST   /api/v1/admin/discounts/compute-all         # Batch recompute
```

#### ML Recommendations
```http
GET    /api/v1/admin/ml/recommend
       ?product_id={sku}
       &days_to_expiry={days}
       &inventory={qty}
       
# Returns: Top-k discount recommendations with uplift predictions
```

#### Analytics
```http
GET    /api/v1/admin/analytics                      # Summary metrics
GET    /api/v1/admin/analytics/sales-vs-expiry      # Expiry impact chart
GET    /api/v1/admin/analytics/discount-vs-units    # Discount effectiveness
```

#### A/B Testing
```http
GET    /api/v1/admin/experiments                    # List experiments
POST   /api/v1/admin/experiments/assign             # Assign products to groups
GET    /api/v1/admin/experiments/analytics/comparison  # Performance comparison
```

### Interactive API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 💡 Usage Examples

### 1. Create Product and Add Inventory

```bash
# Create a product
curl -X POST http://localhost:8000/api/v1/admin/products \
  -H "Content-Type: application/json" \
  -d '{
    "sku": "MILK-001",
    "name": "Organic Whole Milk 1L",
    "category": "Dairy",
    "base_price": 4.99
  }'

# Add inventory batch (expires in 5 days)
curl -X POST http://localhost:8000/api/v1/admin/inventory \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 1,
    "batch_code": "BATCH-2025-001",
    "quantity": 50,
    "expiry_date": "2025-11-20"
  }'
```

### 2. Get ML-Powered Discount Recommendations

```bash
curl "http://localhost:8000/api/v1/admin/ml/recommend?\
product_id=MILK-001&\
days_to_expiry=5&\
inventory=50&\
top_k=3"

# Response:
{
  "recommendations": [
    {
      "discount_pct": 35.0,
      "purchase_probability": 0.78,
      "expected_revenue": 162.18,
      "uplift": 0.23
    },
    {
      "discount_pct": 40.0,
      "purchase_probability": 0.85,
      "expected_revenue": 149.85,
      "uplift": 0.30
    },
    {
      "discount_pct": 30.0,
      "purchase_probability": 0.71,
      "expected_revenue": 174.65,
      "uplift": 0.16
    }
  ],
  "model_info": {
    "model_type": "XGBoost",
    "auc_score": 0.87,
    "trained_at": "2025-11-15T19:26:42Z"
  }
}
```

### 3. Setup A/B Test

```python
# Assign products to experiment groups
import requests

# Control group (rule-based)
requests.post("http://localhost:8000/api/v1/admin/experiments/assign", json={
    "product_ids": [1, 2, 3],
    "experiment_group": "CONTROL"
})

# ML variant group
requests.post("http://localhost:8000/api/v1/admin/experiments/assign", json={
    "product_ids": [4, 5, 6],
    "experiment_group": "ML_VARIANT"
})

# After running experiment, compare results
response = requests.get(
    "http://localhost:8000/api/v1/admin/experiments/analytics/comparison"
)
print(response.json())
# Shows conversion rates, revenue, and statistical significance
```

---

## 🧪 Testing

### Run All Tests

```bash
# Quick validation (18 tests)
python3 backend/scripts/quick_validation.py

# Comprehensive test suite
./scripts/run_all_tests.sh

# Docker-based pytest
docker exec flexiprice-backend pytest tests/ -v

# Specific test categories
docker exec flexiprice-backend pytest tests/test_discount_engine.py -v
docker exec flexiprice-backend pytest tests/test_comprehensive_system.py -v
```

### Test Coverage

| Component | Tests | Status |
|-----------|-------|--------|
| Backend API | 6/6 | ✅ Pass |
| Frontend | 4/4 | ✅ Pass |
| Database | 2/2 | ✅ Pass |
| ML System | 1/1 | ✅ Pass |
| Analytics | 3/3 | ✅ Pass |
| Experiments | 2/2 | ✅ Pass |
| **TOTAL** | **18/18** | ✅ **100%** |

---

## 🔧 Configuration

### Environment Variables

Create `.env` file in project root:

```bash
# Database
DATABASE_URL=postgresql://flexiprice:flexiprice_dev_password@postgres:5432/flexiprice_db

# Redis
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0

# API
API_V1_PREFIX=/api/v1
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]

# ML Configuration
ML_MODEL_PATH=./models
DISCOUNT_CALCULATION_SCHEDULE=0 */6 * * *

# Discount Rules
MIN_DISCOUNT_PCT=5.0
MAX_DISCOUNT_PCT=80.0
EXPIRY_THRESHOLD_DAYS=30
PRICE_FLOOR_MULTIPLIER=0.20
```

### Discount Rules (YAML)

Configure discount logic in `backend/config/discount_rules.yaml`:

```yaml
rules:
  - condition:
      days_to_expiry: <= 2
      category: "*"
    discount_pct: 60.0
    reason: "Critical expiry"
    
  - condition:
      days_to_expiry: <= 7
      category: ["Dairy", "Meat", "Seafood"]
    discount_pct: 40.0
    reason: "High-risk perishables"
    
  - condition:
      days_to_expiry: <= 14
      inventory_level: >= 100
    discount_pct: 25.0
    reason: "Overstocked item"
    
  - condition:
      days_to_expiry: <= 30
    discount_pct: 15.0
    reason: "Standard expiry discount"

# Price floor: Never go below 20% of base price
price_floor_multiplier: 0.20
```

---

## 🔬 ML Model Training

### Train New Model

```bash
# Generate synthetic training data
python3 backend/scripts/generate_synthetic_data.py

# Train XGBoost model
python3 backend/scripts/train_model.py

# Model will be saved to: backend/models/xgb_recommend.json
```

### Model Features

The ML model uses these engineered features:
- `base_price` - Product price
- `days_to_expiry` - Time until expiration
- `discount_pct` - Discount percentage
- `inventory_level` - Current stock quantity
- `category` - Product category (encoded)
- `urgency_score` - Computed urgency metric
- `price_tier` - Low/medium/high categorization

### Model Performance Metrics

```json
{
  "auc_score": 0.87,
  "accuracy": 0.82,
  "precision": 0.79,
  "recall": 0.85,
  "f1_score": 0.82,
  "training_samples": 50000,
  "trained_at": "2025-11-15T19:26:42Z"
}
```

---

## 📊 Database Schema

### Core Tables

```sql
-- Products
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    sku TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    category TEXT,
    base_price NUMERIC(12,2) NOT NULL,
    experiment_group "ExperimentGroup",  -- CONTROL | ML_VARIANT
    created_at TIMESTAMP DEFAULT now()
);

-- Inventory Batches
CREATE TABLE inventory_batches (
    id SERIAL PRIMARY KEY,
    product_id INT REFERENCES products(id),
    batch_code TEXT,
    quantity INT NOT NULL,
    expiry_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT now()
);

-- Batch Discounts
CREATE TABLE batch_discounts (
    id SERIAL PRIMARY KEY,
    batch_id INT REFERENCES inventory_batches(id),
    computed_price NUMERIC(12,2) NOT NULL,
    discount_pct NUMERIC(5,2) NOT NULL,
    valid_from TIMESTAMP DEFAULT now(),
    valid_to TIMESTAMP,
    expires_at TIMESTAMP,
    ml_recommended BOOLEAN DEFAULT false
);

-- Experiment Metrics
CREATE TABLE experiment_metrics (
    id SERIAL PRIMARY KEY,
    product_id INT REFERENCES products(id),
    experiment_group "ExperimentGroup" NOT NULL,
    impressions INT DEFAULT 0,
    conversions INT DEFAULT 0,
    revenue NUMERIC(12,2) DEFAULT 0,
    units_sold INT DEFAULT 0,
    period_start TIMESTAMP NOT NULL,
    period_end TIMESTAMP NOT NULL
);
```

---

## 🚢 Deployment

### Docker Production Build

```bash
# Build optimized production images
docker-compose -f docker-compose.prod.yml build

# Start with production settings
docker-compose -f docker-compose.prod.yml up -d

# Scale workers
docker-compose -f docker-compose.prod.yml up -d --scale celery-worker=4
```

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Database connectivity
docker exec flexiprice-postgres pg_isready -U flexiprice

# Redis connectivity
docker exec flexiprice-redis redis-cli ping

# Celery workers
docker exec flexiprice-celery-worker celery -A app.celery_app inspect active
```

### Monitoring

```bash
# View logs
docker-compose logs -f backend
docker-compose logs -f celery-worker

# Check Celery tasks
docker exec flexiprice-celery-worker celery -A app.celery_app inspect stats

# Database queries
docker exec flexiprice-postgres psql -U flexiprice -d flexiprice_db -c \
  "SELECT COUNT(*) FROM products;"
```

---

## 📁 Project Structure

```
FlexiPrice/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/     # API route handlers
│   │   ├── core/                 # Config, DB, discount engine
│   │   ├── models/               # (Prisma models in schema)
│   │   ├── schemas/              # Pydantic models
│   │   ├── services/             # Business logic layer
│   │   ├── celery_app.py         # Celery configuration
│   │   ├── main.py               # FastAPI application
│   │   └── tasks.py              # Background tasks
│   ├── config/
│   │   └── discount_rules.yaml   # Pricing rules
│   ├── data/
│   │   └── synthetic_purchases.csv
│   ├── models/                   # Trained ML models
│   │   ├── xgb_recommend.json
│   │   ├── feature_names.json
│   │   └── metrics.json
│   ├── prisma/
│   │   ├── schema.prisma         # Database schema
│   │   └── migrations/           # SQL migrations
│   ├── scripts/                  # Utility scripts
│   │   ├── train_model.py
│   │   ├── generate_synthetic_data.py
│   │   ├── quick_validation.py
│   │   └── init_db.py
│   ├── tests/                    # Test suites
│   │   ├── test_comprehensive_system.py
│   │   ├── test_discount_engine.py
│   │   └── test_batch_processing.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── admin/
│   │   │   ├── page.tsx          # Admin dashboard
│   │   │   ├── analytics/        # Analytics views
│   │   │   └── experiments/      # A/B test UI
│   │   ├── product/[sku]/        # Product detail pages
│   │   ├── layout.tsx
│   │   └── page.tsx              # Storefront
│   ├── components/
│   │   ├── ProductCard.tsx
│   │   ├── ProductForm.tsx
│   │   ├── InventoryForm.tsx
│   │   └── *Chart.tsx            # Analytics charts
│   ├── lib/
│   │   └── api.ts                # API client
│   ├── types/
│   │   └── index.ts              # TypeScript definitions
│   ├── next.config.ts
│   ├── package.json
│   └── tsconfig.json
├── scripts/
│   ├── quick_start.sh            # One-command setup
│   └── run_all_tests.sh          # Test runner
├── docker-compose.yml            # Dev environment
├── docker-compose.prod.yml       # Production config
└── README.md
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Use TypeScript for all frontend code
- Write tests for new features
- Update documentation
- Run `./scripts/run_all_tests.sh` before submitting PR

---

## 📝 License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgments

- **FastAPI** - Modern, fast web framework
- **Next.js** - React framework for production
- **Prisma** - Next-generation ORM
- **XGBoost** - ML gradient boosting framework
- **Celery** - Distributed task queue

---

## 📧 Support

- **Documentation**: [API Docs](http://localhost:8000/docs)
- **Issues**: [GitHub Issues](https://github.com/Shubhkesarwani02/FlexiPrice/issues)

---

## 🎯 Roadmap

- [ ] Real-time inventory tracking with IoT sensors
- [ ] Customer segmentation and personalized pricing
- [ ] Mobile app for store managers
- [ ] Multi-store support and franchising
- [ ] Advanced forecasting with LSTM models
- [ ] Integration with POS systems
- [ ] Automated reordering based on demand predictions

---

**Made with ❤️ for reducing food waste and maximizing profitability**
