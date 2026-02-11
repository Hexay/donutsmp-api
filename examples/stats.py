import asyncio
import os

from dotenv import load_dotenv

from donut import DonutClient

load_dotenv()


async def main():
    async with DonutClient(os.getenv("API_KEY")) as client:

        stats = await client.stats('archivepedro')
        print(stats)

if __name__ == "__main__":
    asyncio.run(main())