import asyncio
from io import BytesIO
from typing import AsyncIterator, Iterator
from contextlib import asynccontextmanager

from fastapi.responses import StreamingResponse


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
    try:
        buf.seek(0)
        while True:
            chunk = buf.read(CHUNK)
            if not chunk:
                break
            yield chunk
    finally:
        buf.close()

def convert_bytesio_to_file_response(stream: BytesIO, file_source: str) -> StreamingResponse:
    mime_type = None
    content_disposition = None
    if file_source == "images":
        mime_type = "image/jpeg"
        content_disposition = "inline"
        filename = "image.jpg"
    elif file_source == "songs":
        mime_type = "audio/mpeg"
        content_disposition = 'attachment; filename="song.mp3"'
        filename = "song.mp3"

    headers = {
        "Content-Type": mime_type,
        "Content-Disposition": content_disposition,
    }

    return StreamingResponse(
        bytesio_iterator(stream),
        media_type=mime_type,
        headers=headers,
    )
