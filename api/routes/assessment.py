from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_db_session
from tasks.jobs import run_assessment_task

router = APIRouter()


class RunAssessmentRequest(BaseModel):
	domain: str = Field(..., description="Domain to assess, e.g. example.com")


@router.post("/run", status_code=status.HTTP_202_ACCEPTED)
async def run_assessment(payload: RunAssessmentRequest, db: AsyncSession = Depends(get_db_session)):
	# Enqueue Celery task to run full assessment
	task = run_assessment_task.delay(payload.domain)
	return {"task_id": task.id}


@router.get("/{assessment_id}")
async def get_assessment(assessment_id: str, db: AsyncSession = Depends(get_db_session)):
	svc = AssessmentService(db)
	result = await svc.get_assessment(assessment_id)
	if not result:
		raise HTTPException(status_code=404, detail="Assessment not found")
	return result

