from decimal import Decimal
from typing import Optional, List
from datetime import datetime, timedelta

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import Column
from sqlalchemy import Table
from sqlalchemy import ForeignKey
from sqlalchemy import MetaData
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.orm import registry

from src.domain.artist import Artist
from src.domain.iam.constants import Grants
from src.domain.iam.user import BaseUser, UserId, UserName, EmailAddress
from src.domain.playlist import Playlist
from src.domain.song import Song
from src.domain.genre import Genre
from src.domain.subscription.payment_choice import Payment
from src.domain.subscription.tiers import SubscriptionTier
from src.domain.types import GenreId, GenreName, ArtistId, ArtistNickname, SongId, SongTitle, SongDescription, AlbumId, \
    SongCoverImage
from src.domain.subscription.model import ActiveSubscription

metadata = MetaData()
Base_ = declarative_base(metadata=metadata)

class Base(AsyncAttrs, Base_):
    __abstract__ = True


class UserTable(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, nullable=False)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    grants: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    is_adult: Mapped[bool] = mapped_column(nullable=False)
    subscription_id: Mapped[int] = mapped_column(
        ForeignKey('subscriptions.id'),
        nullable=True
    )
    password: Mapped[str] = mapped_column(nullable=False)

    def __repr__(self):
        return f"<UserTable(username={self.username}, grants={self.grants})>"

    def to_domain(self):
        return BaseUser(
            id=UserId(self.id),
            username=UserName(self.username),
            email=EmailAddress(self.email),
            grants=[Grants(grant) for grant in self.grants],
            is_adult=self.is_adult,
            subscription_id=self.subscription_id,
            password=self.password,
        )


playlist_songs_association_table = Table(
    "playlist_songs_association_table",
    Base.metadata,
    Column("playlist_id", ForeignKey("playlist.id"), primary_key=True),
    Column("song_id", ForeignKey("songs.id"), primary_key=True),
)

playlist_genres_association_table = Table(
    "playlist_genres_association_table",
    Base.metadata,
    Column("playlist_id", ForeignKey("playlist.id"), primary_key=True),
    Column("genre_id", ForeignKey("genres.id"), primary_key=True),
)
playlist_artists_association_table = Table(
    "playlist_artists_association_table",
    Base.metadata,
    Column("playlist_id", ForeignKey("playlist.id"), primary_key=True),
    Column("artist_id", ForeignKey("artists.id"), primary_key=True),
)


class PlaylistTable(Base):
    __tablename__ = "playlist"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now())
    songs: Mapped[List["TableSong"]] = relationship(
        "TableSong",
        secondary=playlist_songs_association_table,
        back_populates="playlists",
    )
    genres: Mapped[List["GenreTable"]] = relationship(
        "GenreTable",
        secondary=playlist_genres_association_table,
        back_populates="playlists",
    )
    artists: Mapped[List["ArtistTable"]] = relationship(
        "ArtistTable",
        secondary=playlist_artists_association_table,
        back_populates="playlists",
    )

    def to_domain(self):
        return Playlist(
            playlist_id=self.id,
            author_id=self.author_id,
            songs=[song.to_domain() for song in self.songs],
            genres=[genre.to_domain() for genre in self.genres],
        )

songs_artists_association_table = Table(
    "songs_artists_association_table",
    Base.metadata,
    Column("song_id", ForeignKey("songs.id"), primary_key=True),
    Column("artist_id", ForeignKey("artists.id"), primary_key=True),
)

songs_genres_association_table = Table(
    "songs_genres_association_table",
    Base.metadata,
    Column("song_id", ForeignKey("songs.id"), primary_key=True),
    Column("genre_id", ForeignKey("genres.id"), primary_key=True),
)

artists_genres_association_table = Table(
    "artists_genres_association_table",
    Base.metadata,
    Column("artist_id", ForeignKey("artists.id"), primary_key=True),
    Column("genre_id", ForeignKey("genres.id"), primary_key=True),
)

class GenreTable(Base):
    __tablename__ = 'genres'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now())
    artists: Mapped[List[Artist]] = relationship(
        "ArtistTable",
        secondary=artists_genres_association_table,
        back_populates="genres",
    )
    songs: Mapped[List["TableSong"]] = relationship(
        "TableSong",
        secondary=songs_genres_association_table,
        back_populates="genres",
    )
    playlists: Mapped[List["Playlist"]] = relationship(
        "PlaylistTable",
        secondary=playlist_genres_association_table,
        back_populates="genres",
    )

    def to_domain(self) -> Genre:
        return Genre(
            name=GenreName(self.name),
            created_at=self.created_at,
            updated_at=self.updated_at,
            genre_id=GenreId(self.id)
        )

class ArtistTable(Base):
    __tablename__ = 'artists'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    genres: Mapped[List["GenreTable"]] = relationship(
        "GenreTable",
        secondary=artists_genres_association_table,
        back_populates="artists"
    )
    songs: Mapped[List["TableSong"]] = relationship(
        "TableSong",
        secondary=songs_artists_association_table,
        back_populates="artists"
    )
    playlists: Mapped[List["Playlist"]] = relationship(
        "PlaylistTable",
        secondary=playlist_artists_association_table,
        back_populates="artists"
    )

    def to_domain(self):
        return Artist(
            id=ArtistId(self.id),
            nickname=ArtistNickname(self.name),
            user_id=UserId(self.user_id),
            genres=[genre.to_domain() for genre in self.genres],
        )



class TableSong(Base):
    __tablename__ = 'songs'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    album_id: Mapped[int] = mapped_column(autoincrement=True, nullable=True)
    cover_image: Mapped[str] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(nullable=True, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(nullable=True, onupdate=func.now())
    song_file_path: Mapped[str] = mapped_column(nullable=False)
    original_song_filename: Mapped[str] = mapped_column(nullable=False)
    original_cover_image_filename: Mapped[str] = mapped_column(nullable=True)
    author_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    genres: Mapped[List["GenreTable"]] = relationship(
        "GenreTable",
        secondary=songs_genres_association_table,
        back_populates="songs"
    )

    artists: Mapped[List['ArtistTable']] = relationship(
        "ArtistTable",
        secondary=songs_artists_association_table,
        back_populates="songs"
    )

    playlists: Mapped["PlaylistTable"] = relationship(
        "PlaylistTable",
        secondary=playlist_songs_association_table,
        back_populates="songs"
    )

    def to_domain(self):
        return Song(
            id=SongId(self.id),
            title=SongTitle(self.title),
            description=SongDescription(self.description),
            album_id=AlbumId(self.album_id),
            cover_image=SongCoverImage(self.cover_image),
            created_at=self.created_at,
            updated_at=self.updated_at,
            song_file_path=self.song_file_path,
            original_song_filename=self.original_song_filename,
            original_cover_image_filename=self.original_cover_image_filename,
            artists=[artist for artist in self.artists],
            genres=[genre.to_domain() for genre in self.genres],
        )

class TierTable(Base):
    __tablename__ = 'tiers'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    price: Mapped[float] = mapped_column(nullable=True)
    ending_threshold: Mapped[timedelta] = mapped_column(nullable=True)

    def to_domain(self) -> SubscriptionTier:
        return SubscriptionTier(
            id=self.id,
            price=Decimal(self.price),
            name=self.name,
            ending_threshold=self.ending_threshold,
        )


class SubscriptionTable(Base):
    __tablename__ = 'subscriptions'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    started_at: Mapped[datetime] = mapped_column(nullable=False)
    ended_at: Mapped[datetime] = mapped_column(nullable=False)
    tier_id: Mapped[int] = mapped_column(ForeignKey('tiers.id'))
    payment_id: Mapped[str] = mapped_column(nullable=True)
    payment_method: Mapped[int] = mapped_column(ForeignKey('payment_choices.id'), nullable=True)

    def to_domain(self) -> ActiveSubscription:
        return ActiveSubscription(
            id=self.id,
            started_at=self.started_at,
            ended_at=self.ended_at,
            tier_id=self.tier_id,
            user_id=self.user_id,
            payment_id=self.payment_id,
            payment_method=self.payment_method,
        )

class PaymentChoices(Base):
    __tablename__ = 'payment_choices'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)

    def to_domain(self):
        return Payment(
            id=self.id,
            name=self.name,
            description=self.description,
        )
