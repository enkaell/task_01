import asyncio
from database import execute_mapping_of_tables

async def mapping_handler():
    # Just call a db inside service level
    await execute_mapping_of_tables()

