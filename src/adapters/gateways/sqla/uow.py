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
