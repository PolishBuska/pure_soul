import pytest


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_genres(client):

    payments = await client.get("/api/v1/ams/genres")
    assert payments.status_code == 200
