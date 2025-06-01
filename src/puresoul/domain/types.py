from typing import NewType

UserId = NewType("UserId", int)
UserName = NewType("UserName", str)
EmailAddress = NewType("EmailAddress", str)

AlbumId = NewType("AlbumId", int)
AlbumTitle = NewType("AlbumTitle", str)
AlbumDescription = NewType("AlbumDescription", str)
AlbumCoverImage = NewType("AlbumCoverImage", str)

ArtistId = NewType("ArtistId", int)
ArtistNickname = NewType("ArtistNickname", str)

SongTitle = NewType("SongTitle", str)
SongId = NewType("SongId", int)
SongDescription = NewType("SongDescription", str)
SongCoverImage = NewType("SongCoverImage", str)

GenreName = NewType("GenreName", str)
GenreId = NewType("GenreId", int)

PlaylistId = NewType("PlaylistId", int)

AllowedFileFormats = {
    'mp3'
}