import asyncio
import os
from dotenv import load_dotenv
from donut import DonutClient, format_number
import time
load_dotenv()


async def main():
    async with DonutClient(os.getenv("API_KEY")) as client:

        start = time.time()
        leaderboards = await client.leaderboards.batch("money", 1, 100)

        total = 0
        for leaderboard in leaderboards:
            for entry in leaderboard:
                total += float(entry.value or 0)

        end = time.time()
        formatted_total = format_number(total)
        print(f"Total: {formatted_total} in Time taken: {end - start} seconds")
        

if __name__ == "__main__":
    asyncio.run(main())