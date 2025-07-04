import psycopg2
from sqlalchemy import make_url


def ensure_test_db_exists(sync_db_url: str):
    url = make_url(sync_db_url)
    admin_url = url.set(database="postgres", username="admin", password="admin123", host="localhost")

    conn = psycopg2.connect(
        dbname=admin_url.database,
        user=admin_url.username,
        password=admin_url.password,
        host=admin_url.host,
        port=admin_url.port,
    )
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{url.database}'")
        if not cur.fetchone():
            print('creating database')
            cur.execute(f"CREATE DATABASE {url.database}")
    conn.close()

def truncate_all_tables(db_url: str):
    url = make_url(db_url)

    conn = psycopg2.connect(
        dbname=url.database,
        user=url.username,
        password=url.password,
        host=url.host,
        port=url.port,
    )
    conn.autocommit = True

    with conn.cursor() as cur:
        cur.execute("SET session_replication_role = replica;")

        cur.execute("""
            SELECT tablename FROM pg_tables WHERE schemaname = 'public';
        """)
        tables = [row[0] for row in cur.fetchall()]

        for table in tables:
            cur.execute(f'TRUNCATE TABLE "{table}" RESTART IDENTITY CASCADE;')

        cur.execute("SET session_replication_role = origin;")

    conn.close()