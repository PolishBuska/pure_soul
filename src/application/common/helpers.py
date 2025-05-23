import asyncio

from src.application.common.file_storage import FileStorage
from src.domain.song import Song


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
