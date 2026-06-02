from tasks.celery_app import celery_app
from services.assessment_service import AssessmentService
from database.session import AsyncSessionLocal
import logging

logger = logging.getLogger("eip.celery")


@celery_app.task(bind=True, name="tasks.jobs.run_assessment_task", max_retries=3)
def run_assessment_task(self, domain: str) -> str:
	"""Celery task wrapper that orchestrates a full assessment.

	Retries on failure with exponential backoff.
	"""
	import asyncio

	try:
		async def _run():
			async with AsyncSessionLocal() as db:
				svc = AssessmentService(db)
				assessment_id = await svc.run_full_assessment(domain)
				return assessment_id

		assessment_id = asyncio.run(_run())
		logger.info("Assessment task completed, id=%s", assessment_id)
		return str(assessment_id)

	except Exception as exc:
		# exponential backoff in seconds
		retries = getattr(self.request, "retries", 0)
		countdown = min(60 * (2 ** retries), 3600)
		logger.exception("Assessment task failed for domain=%s, retrying in %s seconds", domain, countdown)
		raise self.retry(exc=exc, countdown=countdown)
