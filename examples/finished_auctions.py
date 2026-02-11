import asyncio
import os
import time
from dotenv import load_dotenv
from donut import DonutClient, PurchaseItem

load_dotenv()

CACHE_TTL_MS = 3 * 60 * 1000
seen_auctions: dict[str, int] = {}


def make_cache_key(auction: PurchaseItem) -> str:
    return f"{auction.item.id}-{auction.item.count}-{auction.price}-{auction.seller.uuid}-{auction.unixMillisDateSold}"


def clean_cache():
    cutoff = int(time.time() * 1000) - CACHE_TTL_MS
    expired = [k for k, ts in seen_auctions.items() if ts < cutoff]
    for k in expired:
        del seen_auctions[k]


def filter_new_auctions(auctions: list[PurchaseItem]) -> list[PurchaseItem]:
    clean_cache()
    now = int(time.time() * 1000)
    new_auctions = []
    for auction in auctions:
        key = make_cache_key(auction)
        if key not in seen_auctions:
            seen_auctions[key] = now
            new_auctions.append(auction)
    return new_auctions


async def main():
    async with DonutClient(os.getenv("API_KEY")) as client:
        while True:
            auctions = await client.auction.transactions(page=1)
            print("\n\n\n")
            for auction in filter_new_auctions(list(auctions)):
                print(auction)
            await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())