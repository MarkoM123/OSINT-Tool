from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_db_session
from services.company_service import CompanyService

router = APIRouter()


class CompanyCreate(BaseModel):
	name: str = Field(...)
	domain: str = Field(...)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_company(payload: CompanyCreate, db: AsyncSession = Depends(get_db_session)):
	svc = CompanyService(db)
	company = await svc.create(payload.name, payload.domain)
	if not company:
		raise HTTPException(status_code=400, detail="Unable to create company")
	return {"id": str(company.id), "name": company.name, "domain": company.domain}
