import asyncio
from io import BytesIO
from typing import Tuple, List

from src.puresoul.application.common.file_storage import FileStorage
from src.puresoul.application.common.names_hasher import NamesHasher
from src.puresoul.application.common.user_gateway import UserGateway
from src.puresoul.domain.song import Song


async def adapt_song_filepaths(
        song: Song,
        image_file_storage: FileStorage,
        song_file_storage: FileStorage,
) -> Song:
    song_b, cover_b = song.song_file_path.split('/').pop(0), song.cover_image.split('/').pop(0)
    song.song_file_path.replace(song_b, '')
    song.cover_image.replace(cover_b, '')
    async_tasks = (
        asyncio.to_thread(
            song_file_storage.get_path,
            song.song_file_path
        ),
        asyncio.to_thread(
            image_file_storage.get_path,
            song.cover_image,
        )
    )
    res = await asyncio.gather(*async_tasks)
    song.song_file_path = f"{song_b}/" + res[0]
    song.cover_image_path = f"{cover_b}/" + res[1]
    return song

async def save_song_files(
        song_file_storage: FileStorage,
        cover_image_storage: FileStorage,
        song: Tuple[str, BytesIO, int],
        image_file: Tuple[str, BytesIO, int]
):
    await asyncio.to_thread(
        song_file_storage.save_file,
        file_object=song[1],
        obj_key=song[0] + f"/{song[2]}",
    )
    await asyncio.to_thread(
        cover_image_storage.save_file,
        file_object=image_file[1],
        obj_key=f"{image_file[0]}/{image_file[2]}",
    )

async def artists_exist(
        user_gateway: UserGateway,
        artists: List[int],
) -> bool:
    persisted_artists = await user_gateway.filter_artists(
        params={
            'id': [int(author) for author in artists]
        }
    )
    return all(artist_id in persisted_artists for artist_id in artists)

def get_song_full_paths(
        hasher: NamesHasher,
        curr_user: int,
        image_file_name: str,
        song_file_name: str,
) -> Tuple[str, str]:
    return (
        f"/{curr_user}/"
        f".{hasher.hash_name(image_file_name)}",
        f"{curr_user}/"
        f"{hasher.hash_name(song_file_name)}"
    )