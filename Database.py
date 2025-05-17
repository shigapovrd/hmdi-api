import asyncpg

class Database:
    def __init__(self, config):
        self.config = config
        self.pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(**self.config)
        # Создаем таблицу если она не существует
        async with self.pool.acquire() as connection:
            await connection.execute("""
                CREATE TABLE IF NOT EXISTS requests (
                    id SERIAL PRIMARY KEY,
                    ticket_id TEXT UNIQUE NOT NULL,
                    user_id TEXT NOT NULL,
                    description TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

    async def disconnect(self):
        if self.pool:
            await self.pool.close()

    async def add_request(self, description: str, ticket_id: str, user_id: str):
        async with self.pool.acquire() as connection:
            await connection.execute(
                """
                INSERT INTO requests (ticket_id, user_id, description)
                VALUES ($1, $2, $3)
                """,
                ticket_id, user_id, description
            )

    async def get_request_by_ticket(self, ticket_id: str):
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("""
                SELECT ticket_id, user_id, description, created_at
                FROM requests
                WHERE ticket_id = $1
            """, ticket_id)
            
            if row:
                return {
                    "ticket_id": row['ticket_id'],
                    "user_id": row['user_id'],
                    "description": row['description'],
                    "created_at": row['created_at'].isoformat()
                }
            return None

    async def get_all_requests(self):
        async with self.pool.acquire() as connection:
            rows = await connection.fetch("""
                SELECT ticket_id, user_id, description, created_at 
                FROM requests 
                ORDER BY created_at DESC
            """)
            return [
                {
                    "ticket_id": row['ticket_id'],
                    "user_id": row['user_id'],
                    "description": row['description'],
                    "created_at": row['created_at'].isoformat()
                }
                for row in rows
            ]