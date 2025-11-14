from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="FlexiPrice API",
    description="Expiry-Based Dynamic Pricing System",
    version="0.1.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok", "service": "flexiprice-api"}

@app.get("/")
async def root():
    return {
        "message": "FlexiPrice API",
        "docs": "/docs",
        "health": "/health"
    }
