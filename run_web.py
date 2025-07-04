import asyncio

from puresoul.main.web import main

if __name__ == "__main__":
    asyncio.run(
        main(
        db_url = 'postgresql+asyncpg://admin:admin123@localhost:5432/pure_soul',
        token_secret = 'secret',
        s3_uri = 'http://127.0.0.1:9000',
        s3_access_key_id = 'mRa7SfDQPxvAr7OX1loRaAyfHf2JX4PC9iqhBUU8',
        s3_secret_key = 'cPXy2dJM4im3iRjApIWw',
        )
    )
