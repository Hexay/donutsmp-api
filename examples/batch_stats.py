import asyncio
import os

from dotenv import load_dotenv

from donut import DonutClient

load_dotenv()


async def main():
    usernames = ["archivepedro", "hexay"]
    
    async with DonutClient(os.getenv("API_KEY")) as client:
        stats_list = await client.stats.batch(usernames)
        
        for stats in stats_list:
            print(stats)


if __name__ == "__main__":
    asyncio.run(main())

