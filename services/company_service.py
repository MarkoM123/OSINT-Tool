from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.company import Company


class CompanyService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, name: str, domain: str) -> Company | None:
        stmt = select(Company).where(Company.domain == domain)
        res = await self.db.execute(stmt)
        existing = res.scalars().first()
        if existing:
            return existing

        company = Company(name=name, domain=domain)
        self.db.add(company)
        await self.db.commit()
        await self.db.refresh(company)
        return company
