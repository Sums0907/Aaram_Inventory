from uuid import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, ForeignKey, UniqueConstraint
from src.foundation.database.models import BaseModel

class MatchRelationshipModel(BaseModel):
    __tablename__ = "matching_relationships"

    match_job_id: Mapped[UUID] = mapped_column(ForeignKey("matching_jobs.id"), nullable=False, index=True)
    
    source_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True) # e.g. PAYMENT
    source_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    
    target_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True) # e.g. SALES_ORDER
    target_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    
    relationship_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True) # e.g. PAYMENT_TO_ORDER
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="MATCHED") # MATCHED, MANUALLY_MATCHED
    
    # We want to ensure uniqueness of the exact edge to prevent duplicate matches
    __table_args__ = (
        UniqueConstraint('source_type', 'source_id', 'target_type', 'target_id', 'relationship_type', name='uq_match_relationship'),
    )
