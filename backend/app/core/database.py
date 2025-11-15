from prisma import Prisma
from app.core.config import get_settings

settings = get_settings()

# Convert SQLAlchemy URL to Prisma-compatible URL
def get_prisma_url(url: str) -> str:
    """Convert SQLAlchemy database URL to Prisma-compatible format."""
    # Remove SQLAlchemy-specific driver suffix (e.g., +asyncpg)
    return url.replace("+asyncpg", "").replace("+psycopg2", "")

# Global Prisma client instance
prisma = Prisma(
    datasource={
        "url": get_prisma_url(settings.DATABASE_URL)
    }
)


async def connect_db():
    """Connect to the database."""
    if not prisma.is_connected():
        await prisma.connect()
        print("✅ Database connected")


async def disconnect_db():
    """Disconnect from the database."""
    if prisma.is_connected():
        await prisma.disconnect()
        print("❌ Database disconnected")


async def get_db():
    """Dependency for getting database session."""
    return prisma
