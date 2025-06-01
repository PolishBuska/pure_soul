from typing import Any, Dict, List

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, update
from sqlalchemy.orm import selectinload

from puresoul.application.common.user_gateway import UserGateway
from puresoul.domain.artist import Artist
from puresoul.domain.iam.user import BaseUser, UserId

from puresoul.domain.exceptions import AlreadyExistsException
from puresoul.domain.types import ArtistId

from .tables import UserTable, ArtistTable, GenreTable


class SqlaUserGateway(UserGateway):
    def __init__(self, uow: AsyncSession):
        self.uow = uow

    def _prepare_search_params(self, params: Dict[str, Any], model):
        res = []
        print(params)
        for k, v in params.items():
            column = getattr(model, k, None)
            if column is None:
                continue
            if isinstance(v, list):
                res.append(column.in_(v))
            else:
                res.append(column == v)
        return res

    async def create_user(self, user: BaseUser) -> UserId:
        try:
            stmt = insert(UserTable).values(
                username=user.username,
                email=user.email,
                grants=user.grants,
                is_adult=user.is_adult,
                subscription_id=user.subscription_id,
                password=user.password
            ).returning(UserTable.id)
            flushed = await self.uow.execute(stmt)
            user_id = flushed.scalar_one()
            return UserId(user_id)
        except IntegrityError:
            raise AlreadyExistsException(f'the user: {user.username, user.email} already exists')

    async def filter_artists(self, params: Dict[str, Any]) -> List[int]:
        where_clause = self._prepare_search_params(params=params, model=ArtistTable)
        query = select(ArtistTable).where(*where_clause)
        res = await self.uow.scalars(query)
        return [m.id for m in res] if res else []

    async def get_user(self, user_id: int) -> BaseUser:
        try:
            query = select(UserTable).where(UserTable.id == user_id)
            res = await self.uow.scalar(query)
            return res.to_domain()
        except Exception as e:
            print(f"something went wrong {str(e)}")

    async def get_user_by_email(self, email: str) -> BaseUser | None:
        query = select(UserTable).where(UserTable.email == email)
        res = await self.uow.scalar(query)
        if res is None:
            return None
        return res.to_domain()

    async def create_artist(
            self,
            user: Artist
    ) -> ArtistId:
        genres_query = select(GenreTable).where(GenreTable.id.in_(user.genres))
        genres_orm = await self.uow.scalars(genres_query)
        new_artist = ArtistTable(
            genres=list(genres_orm),
            name=user.nickname,
            user_id=user.user_id
        )
        self.uow.add(new_artist)
        await self.uow.flush()
        return ArtistId(new_artist.id)


    async def update_user_sub(self, user: BaseUser) -> int:
        stmt = update(UserTable).where(UserTable.id == user.id).values(
            subscription_id=user.subscription_id,
            grants=user.grants
        ).returning(UserTable.id)
        flushed = await self.uow.execute(stmt)
        user_id = flushed.scalar_one()
        return user_id

    async def get_artist_by_user_id(self, user_id: UserId) -> Artist:
        query = select(ArtistTable).where(ArtistTable.id == user_id)
        res = await self.uow.scalar(query)
        return res.to_domain()

    async def find_artist_by_names(self, names: List[str]) -> List[Artist]:
        query = select(ArtistTable).options(selectinload(ArtistTable.genres)).where(ArtistTable.name.in_(names))
        res = await self.uow.scalars(query)
        return [ar.to_domain() for ar in res]

    async def update_user(self, user: BaseUser) -> None:
        ...