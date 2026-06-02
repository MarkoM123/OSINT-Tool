from datetime import datetime
import uuid

from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, JSON, Text, Float
from sqlalchemy.dialects.postgresql import UUID

from database.base import Base


class Finding(Base):
    __tablename__ = "findings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey("assessments.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    evidence = Column(JSON, default={})
    evidence_source = Column(String(128), default="")
    confidence = Column(Float, default=0.0)
    severity = Column(String(32), default="medium")
    category = Column(String(64), default="uncategorized")
    recommendation = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
