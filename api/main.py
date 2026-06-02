import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import assessment, company
from core.config import get_settings


def create_app() -> FastAPI:
	settings = get_settings()
	app = FastAPI(title=settings.project_name)

	# basic structured logging configuration
	logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(message)s')

	app.add_middleware(
		CORSMiddleware,
		allow_origins=["*"],
		allow_credentials=True,
		allow_methods=["*"],
		allow_headers=["*"],
	)

	app.include_router(company.router, prefix="/companies", tags=["companies"])
	app.include_router(assessment.router, prefix="/assessments", tags=["assessments"])

	return app


app = create_app()
