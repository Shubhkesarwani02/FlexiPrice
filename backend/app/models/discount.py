from sqlalchemy import Column, Integer, Numeric, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.models import Base


class BatchDiscount(Base):
    """Batch discount model for storing computed discounts per batch."""
    
    __tablename__ = "batch_discounts"
    
    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("inventory_batches.id", ondelete="CASCADE"), nullable=False)
    computed_price = Column(Numeric(12, 2), nullable=False)
    discount_pct = Column(Numeric(5, 2), nullable=False)
    valid_from = Column(DateTime(timezone=True), server_default=func.now())
    valid_to = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    ml_recommended = Column(Boolean, default=False)
    
    # Relationships
    batch = relationship("InventoryBatch", back_populates="batch_discounts")
    
    def __repr__(self):
        return f"<BatchDiscount(id={self.id}, batch_id={self.batch_id}, discount={self.discount_pct}%)>"
