import uuid

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class Score(Base):
    __tablename__ = "scores"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    assessment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("assessments.id"), nullable=False
    )
    overall: Mapped[int] = mapped_column(Integer, nullable=False)
    email_score: Mapped[int] = mapped_column(Integer, nullable=False)
    attack_surface_score: Mapped[int] = mapped_column(Integer, nullable=False)
    credentials_score: Mapped[int] = mapped_column(Integer, nullable=False)
    technology_score: Mapped[int] = mapped_column(Integer, nullable=False)
    reputation_score: Mapped[int] = mapped_column(Integer, nullable=False)
