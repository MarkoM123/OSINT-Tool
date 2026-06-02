import uuid
from sqlalchemy import Column, Integer, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID

from database.base import Base


class Score(Base):
    __tablename__ = "scores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey("assessments.id"), nullable=False)
    overall = Column(Integer, nullable=False)
    email_score = Column(Integer, nullable=False)
    attack_surface_score = Column(Integer, nullable=False)
    credentials_score = Column(Integer, nullable=False)
    technology_score = Column(Integer, nullable=False)
    reputation_score = Column(Integer, nullable=False)
