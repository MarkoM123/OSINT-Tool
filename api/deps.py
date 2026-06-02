from typing import AsyncGenerator

from database.session import get_db

async def get_db_session() -> AsyncGenerator:
	async for s in get_db():
		yield s
