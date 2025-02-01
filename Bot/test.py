from Engine import initialise_db, drop_db
import asyncio


async def refresh_db():
    await drop_db()
    await initialise_db()

asyncio.run(refresh_db())