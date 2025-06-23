import asyncio
from typing import List, Set

from sqlalchemy import select, insert, or_, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from puresoul.application.common.music_gateway import MusicGateway
from puresoul.application.common.dto import AlbumDTO
from puresoul.domain.album import Album
from puresoul.domain.playlist import Playlist
from puresoul.domain.song import Song

from .tables import GenreTable, PlaylistTable, TableSong, ArtistTable, AlbumModel


class SqlaMusicGateway(MusicGateway):
    def __init__(self, uow: AsyncSession):
        self.uow = uow

    async def fetch_genres(self, genres: List[int] | Set[int]) -> List[GenreTable]:
        genres_query = select(GenreTable).where(GenreTable.id.in_(genres))
        genres_orm = await self.uow.scalars(genres_query)
        return list(genres_orm)

    async def fetch_artists(self, artists: List[int] | Set[int]) -> List[ArtistTable]:
        artists_query = select(ArtistTable).where(ArtistTable.id.in_(artists))
        artists_orm = await self.uow.scalars(artists_query)
        return list(artists_orm)

    async def add_song_model(self, song: Song) -> TableSong:
        new_song = TableSong(
            description=song.description,
            song_file_path=song.song_file_path,
            cover_image=song.cover_image,
            author_id=song.author_id,
            album_id=1,
            title=song.title,
            original_song_filename=song.original_song_filename,
            original_cover_image_filename=song.original_cover_image_filename
        )
        self.uow.add(new_song)
        await self.uow.flush()
        await self.uow.refresh(new_song)
        return new_song

    async def add_songs(self, songs: List[Song]) -> List[Song]:
        all_artists_ids = {artist for song in songs for artist in song.artists}
        all_genres_ids = {genre for song in songs for genre in song.genres}
        extra = await asyncio.gather(*(self.fetch_artists(all_artists_ids), self.fetch_genres(all_genres_ids)))
        artists, genres = extra[0], extra[1]
        upload_tasks = [self.add_song_model(song) for song in songs]
        res = await asyncio.gather(*upload_tasks)
        return_songs = zip(res, songs)
        artist_map = {a.id: a for a in artists}
        genre_map = {g.id: g for g in genres}
        for song_model, song in zip(res, songs):
            song_model.artists = [artist_map[aid] for aid in song.artists]
            song_model.genres = [genre_map[gid] for gid in song.genres]

        await self.uow.flush()
        return [model.to_domain() for model, _ in return_songs]

    async def add_song(self, song: Song):
        extra = await asyncio.gather(*(self.fetch_artists(song.artists), self.fetch_genres(song.genres)))
        artists, genres = extra[0], extra[1]
        new_song = await self.add_song_model(song)
        new_song.genres = genres
        new_song.artists = artists
        await self.uow.flush()
        return new_song.id
    async def get_genres(self):
        query = select(GenreTable)
        result = await self.uow.scalars(query)
        genres = result.unique().all()
        return [genre.to_domain() for genre in genres]

    async def get_playlists(
            self,
            page: int,
            page_size: int,
            genres: List[int],
            artists: List[int],
    ):
        offset = (page - 1) * page_size

        query = (
            select(PlaylistTable)
            .options(
                selectinload(PlaylistTable.songs),
                selectinload(PlaylistTable.genres),
                selectinload(PlaylistTable.artists),
            )
            .filter(
                PlaylistTable.genres.any(GenreTable.id.in_(genres)) if genres else True,
                PlaylistTable.artists.any(ArtistTable.id.in_(artists)) if artists else True,
            )
            .offset(offset)
            .limit(page_size)
        )

        result = await self.uow.execute(query)
        return [playlist.to_domain() for playlist in result]

    async def get_playlists_with_tracks_existing(
            self,
            tracks: List[int],
            page: int,
            page_size: int,
    ) -> List[Playlist]:
        offset = (page - 1) * page_size
        query = (
            select(PlaylistTable).options(
                selectinload(PlaylistTable.songs))
        ).filter(
            PlaylistTable.songs.any(TableSong.id.in_(tracks)) if tracks else True,
        ).offset(offset).limit(page_size)
        result = await self.uow.scalars(query)
        return [playlist.to_domain() for playlist in result]

    async def get_users_tracks(
            self,
            genres: List[int],
            artists: List[int],
    ) -> List[Song]:
        query = (
            select(TableSong).options(
                selectinload(TableSong.genres),
            ).filter(
                TableSong.genres.any(GenreTable.id.in_(genres))
            )
        )
        result = await self.uow.scalars(query)
        return [song.to_domain() for song in result]

    async def get_song_by_id(
            self,
            song_id: int,
    ) -> Song:
        query = select(TableSong).options(
            selectinload(TableSong.genres),
            selectinload(TableSong.artists),
        ).where(TableSong.id == song_id)
        result = await self.uow.scalar(query)
        return result.to_domain()

    async def search_songs(
            self,
            page: int,
            page_size: int,
            genres: List[int],
            artists: List[int],
            search: str
    ):
        search_pattern = f"%{search}%"

        filters = [or_(
            TableSong.title.ilike(search_pattern),
            TableSong.genres.any(GenreTable.name.ilike(search_pattern)),
            TableSong.artists.any(ArtistTable.name.ilike(search_pattern)),
        )]
        validated_page = max(1, min(page, 1_000_0))
        offset = (validated_page - 1) * page_size

        if genres:
            filters.append(TableSong.genres.any(GenreTable.id.in_(genres)))

        if artists:
            filters.append(TableSong.artists.any(ArtistTable.id.in_(artists)))

        query = (
            select(TableSong)
            .filter(*filters)
            .options(
                selectinload(TableSong.genres),
                selectinload(TableSong.artists)
            )
            .order_by(TableSong.created_at.desc())
            .limit(page_size)
            .offset(offset)
        )

        result = await self.uow.scalars(query)
        return [m.to_domain() for m in result]
    async def create_album(self, album: AlbumDTO) -> Album:
        meta = await asyncio.gather(
            self.fetch_artists(
                artists=album.artists
            ),
            self.fetch_genres(
                genres=album.album_genres,
            )
        )
        artists, genres = meta[0], meta[1]
        new_album_model = AlbumModel(
            artists=artists,
            genres=genres,
            name=album.album_name,
            description=album.album_description,
            is_released=False
        )
        self.uow.add(new_album_model)
        await self.uow.flush()
        return new_album_model.to_domain()

    async def get_album_by_id(
            self,
            album_id: int,
    ) -> Album:
        query = select(
            AlbumModel
        ).where(
            AlbumModel.id == album_id
        ).options(
            selectinload(AlbumModel.artists),
            selectinload(AlbumModel.genres),
            selectinload(AlbumModel.songs)
        )
        orm_mo = await self.uow.scalar(query)
        return orm_mo.to_domain()

    async def update_album(self, album: Album) -> int:
        stmt = update(AlbumModel.is_released).where(AlbumModel.id == album.id).values(
            is_released=True
        ).returning(AlbumModel.id)
        flushed = await self.uow.execute(stmt)
        return flushed.scalar_one()

    async def get_album_author_id(
            self,
            album_id: int,
    ) -> int:
        query = select(AlbumModel.author_id).where(AlbumModel.id == album_id)
        return await self.uow.scalar(query)
