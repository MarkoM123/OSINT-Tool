from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_db_session
from services.assessment_service import AssessmentService
from tasks.jobs import run_assessment_task

router = APIRouter()


class RunAssessmentRequest(BaseModel):
    domain: str = Field(..., description="Domain to assess, e.g. example.com")


class TopFindingResponse(BaseModel):
    title: str
    severity: str
    category: str
    recommendation: str


class AssessmentResponse(BaseModel):
    id: str
    domain: str
    status: str
    score: int | None
    category_scores: dict[str, int | None]
    executive_summary: str | None
    top_findings: list[TopFindingResponse]
    created_at: datetime


@router.post("/run", status_code=status.HTTP_202_ACCEPTED)
async def run_assessment(payload: RunAssessmentRequest, db: AsyncSession = Depends(get_db_session)):
	# Enqueue Celery task to run full assessment
	task = run_assessment_task.delay(payload.domain)
	return {"task_id": task.id}


@router.get("/{assessment_id}", response_model=AssessmentResponse)
async def get_assessment(assessment_id: str, db: AsyncSession = Depends(get_db_session)):
    svc = AssessmentService(db)
    result = await svc.get_assessment(assessment_id)
    if not result:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return result

