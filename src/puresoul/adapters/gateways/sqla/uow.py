from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession



class SqlaUOW:
    def __init__(self, db_url):
        self.engine = create_async_engine(
            url=db_url
        )

    async def get_session_factory(self) -> AsyncSession:
        session_factory = async_sessionmaker(bind=self.engine, expire_on_commit=False, autoflush=False, autocommit=False)
        async with session_factory() as session:
            yield session

    async def shutdown(self):
        await self.engine.dispose(close=True)

    async def healthcheck(self):
        async with self.engine.connect() as conn:
            res = await conn.scalar(statement=select(1))
            return res
