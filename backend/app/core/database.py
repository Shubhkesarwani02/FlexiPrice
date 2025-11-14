from prisma import Prisma
from app.core.config import get_settings

settings = get_settings()

# Global Prisma client instance
prisma = Prisma(
    datasource={
        "url": settings.DATABASE_URL
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
