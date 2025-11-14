from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.models import Base


class InventoryBatch(Base):
    """Inventory batch model for tracking product batches with expiry dates."""
    
    __tablename__ = "inventory_batches"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    batch_code = Column(String, nullable=True)
    quantity = Column(Integer, nullable=False)
    expiry_date = Column(Date, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    product = relationship("Product", back_populates="inventory_batches")
    batch_discounts = relationship(
        "BatchDiscount", 
        back_populates="batch", 
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<InventoryBatch(id={self.id}, batch_code='{self.batch_code}', expiry={self.expiry_date})>"
