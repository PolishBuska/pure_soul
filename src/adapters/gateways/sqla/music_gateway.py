from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.application.common.music_gateway import MusicGateway
from src.domain.playlist import Playlist
from src.domain.song import Song

from .tables import GenreTable, PlaylistTable, playlist_genres_association_table, TableSong, ArtistTable


class SqlaMusicGateway(MusicGateway):
    def __init__(self, uow: AsyncSession):
        self.uow = uow

    async def add_song(self, song: Song):
        genres_query = select(GenreTable).where(GenreTable.id.in_(song.genres))
        artists_query = select(ArtistTable).where(ArtistTable.id.in_(song.artists))
        genres_orm = await self.uow.scalars(genres_query)
        artists_orm = await self.uow.scalars(artists_query)
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
        new_song.genres = list(genres_orm)
        new_song.artists = list(artists_orm)

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
