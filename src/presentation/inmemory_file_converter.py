import asyncio
from contextlib import asynccontextmanager
from io import BytesIO


@asynccontextmanager
async def to_bytesio_async(spooled_file):
    loop = asyncio.get_running_loop()
    raw_bytes = await loop.run_in_executor(None, spooled_file.read, None)
    buffer = BytesIO(raw_bytes)
    buffer.seek(0)
    try:
        yield buffer
    finally:
        buffer.close()