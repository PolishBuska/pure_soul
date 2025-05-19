import asyncio
from io import BytesIO
from typing import AsyncIterator
from contextlib import asynccontextmanager

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