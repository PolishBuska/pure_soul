import asyncio
from io import BytesIO
from typing import AsyncIterator, Iterator
from contextlib import asynccontextmanager

from litestar.response import Stream


@asynccontextmanager
async def spooled_to_bytesio(spooled_file) -> AsyncIterator[BytesIO]:
    """
    Copy *raw* bytes from a (possibly async) SpooledTemporaryFile into an
    in‑memory BytesIO, rewound to position 0.  Guarantees binary mode.
    """
    loop = asyncio.get_running_loop()

    if hasattr(spooled_file, "buffer"):
        src = spooled_file.buffer
    else:
        src = spooled_file

    await loop.run_in_executor(None, src.seek, 0)

    raw = await loop.run_in_executor(None, src.read)

    buf = BytesIO(raw)
    buf.seek(0)
    try:
        yield buf
    finally:
        buf.close()

CHUNK = 64 * 1024

def bytesio_iterator(buf: BytesIO) -> Iterator[bytes]:
    buf.seek(0)
    while True:
        chunk = buf.read(CHUNK)
        if not chunk:
            break
        yield chunk

def convert_bytesio_to_file_response(stream: BytesIO) -> Stream:
    headers = {
        "Content-Disposition": 'attachment; filename="audio.mp3"',
        "Content-Type": "audio/mpeg",
    }
    return Stream(
        bytesio_iterator(stream),
        media_type="audio/mpeg",
        headers=headers,
    )
