import asyncpg

class Database:
    def __init__(self, config):
        self.config = config
        self.pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(**self.config)

    async def disconnect(self):
        if self.pool:
            await self.pool.close()

    async def add_request(self, description: str, ticket_id: str):
        async with self.pool.acquire() as connection:
            await connection.execute(
                """
                INSERT INTO requests (ticket_id, description)
                VALUES ($1, $2)
                """,
                ticket_id, description
            )

    async def get_all_requests(self):
        async with self.pool.acquire() as connection:
            rows = await connection.fetch("SELECT description FROM requests")
            return [
                {
                    "description": row['description']
                }
                for row in rows
            ]