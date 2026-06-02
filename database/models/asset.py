from datetime import datetime
import uuid

from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID

from database.base import Base


class Asset(Base):
    __tablename__ = "assets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    hostname = Column(String(512), nullable=False, index=True)
    asset_type = Column(String(64), nullable=False)
    metadata = Column(JSON, default={})
    discovered_at = Column(DateTime, default=datetime.utcnow)
