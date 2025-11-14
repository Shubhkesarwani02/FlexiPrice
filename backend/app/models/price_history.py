from sqlalchemy import Column, Integer, Numeric, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.models import Base


class PriceHistory(Base):
    """Price history model for tracking price changes over time."""
    
    __tablename__ = "price_history"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    price = Column(Numeric(12, 2), nullable=False)
    discount_pct = Column(Numeric(5, 2), default=0.0)
    reason = Column(String, nullable=True)  # "expiry", "ml_recommended", "manual", etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    product = relationship("Product", back_populates="price_history")
    
    def __repr__(self):
        return f"<PriceHistory(id={self.id}, product_id={self.product_id}, price={self.price})>"
