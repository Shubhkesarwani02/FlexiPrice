# Database setup script for FlexiPrice
# This script can be used to initialize the database with Alembic migrations

import asyncio
from app.core.database import connect_db, disconnect_db, prisma


async def init_db():
    """Initialize database schema."""
    print("🔄 Connecting to database...")
    await connect_db()
    
    print("✅ Database connection successful!")
    print("📝 Run 'alembic upgrade head' to apply migrations")
    
    await disconnect_db()


if __name__ == "__main__":
    asyncio.run(init_db())
