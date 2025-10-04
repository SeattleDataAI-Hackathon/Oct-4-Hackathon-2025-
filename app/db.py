# app/db.py
from psycopg_pool import AsyncConnectionPool
from psycopg.rows import dict_row
from .settings import settings

pool: AsyncConnectionPool | None = None

async def init_pool():
    global pool
    # Ensure your NEON_DATABASE_URL contains sslmode=require
    pool = AsyncConnectionPool(
        conninfo=settings.neon_database_url,
        max_size=5,
        kwargs={"autocommit": True},
        open=True,
    )

async def close_pool():
    global pool
    if pool:
        await pool.close()
        pool = None

async def execute(query: str, *args):
    assert pool is not None
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(query, args)

async def fetch(query: str, *args):
    assert pool is not None
    async with pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(query, args)
            return await cur.fetchall()

async def fetchrow(query: str, *args):
    assert pool is not None
    async with pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(query, args)
            return await cur.fetchone()