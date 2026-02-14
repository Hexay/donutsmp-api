import asyncio
import os
import time

from dotenv import load_dotenv

from donut import DonutClient, format_number

load_dotenv()


async def main():
    keys = os.getenv("API_KEY").split("\n")
    print("Keys: ", len(keys))
    async with DonutClient(keys) as client:
        start = time.time()
        leaderboards = await client.leaderboards.batch("money", 1, 260)

        total = 0
        for leaderboard in leaderboards:
            for entry in leaderboard:
                total += entry.value

        end = time.time()
        formatted_total = format_number(total)
        print(f"Total: {formatted_total} in Time taken: {end - start} seconds")
        

if __name__ == "__main__":
    asyncio.run(main())