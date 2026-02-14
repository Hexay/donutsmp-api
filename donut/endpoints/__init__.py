from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Literal, TypeVar, Callable, Awaitable

from ..models import (
    AuctionRequestBody,
    AuctionResponse,
    AuctionSort,
    LeaderboardResponse,
    LookupResponse,
    StatsResponse,
    TransactionHistoryResponse,
)

if TYPE_CHECKING:
    from ..http import HTTPClient

LeaderboardCategory = Literal[
    "money", "shards", "playtime", "kills", "deaths",
    "mobskilled", "brokenblocks", "placedblocks", "sell", "shop"
]

T = TypeVar("T")
U = TypeVar("U")


async def run_batched(
    items: list[T],
    keys: list[list[str]],
    fetch: Callable[[T, str], Awaitable[U]],
) -> list[U]:
    results: list[U] = []
    offset = 0
    for i, batch_keys in enumerate(keys):
        batch_items = items[offset:offset + len(batch_keys)]
        if i > 0:
            await asyncio.sleep(60)
        batch_results = await asyncio.gather(*[fetch(item, key) for item, key in zip(batch_items, batch_keys)])
        results.extend(batch_results)
        offset += len(batch_keys)
    return results


class AuctionEndpoint:
    def __init__(self, http: HTTPClient):
        self._http = http

    async def list(
        self, page: int = 1, search: str | None = None, sort: AuctionSort | None = None
    ) -> AuctionResponse:
        body = AuctionRequestBody(search=search, sort=sort)
        data = await self._http.get(f"/v1/auction/list/{page}", json=body.model_dump(exclude_none=True))
        return AuctionResponse.model_validate(data)

    async def transactions(self, page: int = 1) -> TransactionHistoryResponse:
        data = await self._http.get(f"/v1/auction/transactions/{page}")
        return TransactionHistoryResponse.model_validate(data)


class LeaderboardsEndpoint:
    def __init__(self, http: HTTPClient):
        self._http = http

    async def __call__(self, category: LeaderboardCategory, page: int = 1) -> LeaderboardResponse:
        data = await self._http.get(f"/v1/leaderboards/{category}/{page}")
        return LeaderboardResponse.model_validate(data)

    async def batch(
        self,
        category: LeaderboardCategory,
        start_page: int = 1,
        end_page: int = 10,
    ) -> list[LeaderboardResponse]:
        pages = list(range(start_page, end_page + 1))
        keys = self._http._rate_limiter.distribute(len(pages))

        async def fetch(page: int, key: str) -> LeaderboardResponse:
            data = await self._http.get_with_key(f"/v1/leaderboards/{category}/{page}", key)
            return LeaderboardResponse.model_validate(data)

        return await run_batched(pages, keys, fetch)

    async def money(self, page: int = 1) -> LeaderboardResponse:
        return await self("money", page)

    async def shards(self, page: int = 1) -> LeaderboardResponse:
        return await self("shards", page)

    async def playtime(self, page: int = 1) -> LeaderboardResponse:
        return await self("playtime", page)

    async def kills(self, page: int = 1) -> LeaderboardResponse:
        return await self("kills", page)

    async def deaths(self, page: int = 1) -> LeaderboardResponse:
        return await self("deaths", page)

    async def mobs_killed(self, page: int = 1) -> LeaderboardResponse:
        return await self("mobskilled", page)

    async def broken_blocks(self, page: int = 1) -> LeaderboardResponse:
        return await self("brokenblocks", page)

    async def placed_blocks(self, page: int = 1) -> LeaderboardResponse:
        return await self("placedblocks", page)

    async def sell(self, page: int = 1) -> LeaderboardResponse:
        return await self("sell", page)

    async def shop(self, page: int = 1) -> LeaderboardResponse:
        return await self("shop", page)


class LookupEndpoint:
    def __init__(self, http: HTTPClient):
        self._http = http

    async def __call__(self, username: str) -> LookupResponse:
        data = await self._http.get(f"/v1/lookup/{username}")
        return LookupResponse.model_validate(data)

    async def batch(self, usernames: list[str]) -> list[LookupResponse]:
        keys = self._http._rate_limiter.distribute(len(usernames))

        async def fetch(username: str, key: str) -> LookupResponse:
            data = await self._http.get_with_key(f"/v1/lookup/{username}", key)
            return LookupResponse.model_validate(data)

        return await run_batched(usernames, keys, fetch)


class StatsEndpoint:
    def __init__(self, http: HTTPClient):
        self._http = http

    async def __call__(self, username: str) -> StatsResponse:
        data = await self._http.get(f"/v1/stats/{username}")
        return StatsResponse.model_validate(data)

    async def batch(self, usernames: list[str]) -> list[StatsResponse]:
        keys = self._http._rate_limiter.distribute(len(usernames))

        async def fetch(username: str, key: str) -> StatsResponse:
            data = await self._http.get_with_key(f"/v1/stats/{username}", key)
            return StatsResponse.model_validate(data)

        return await run_batched(usernames, keys, fetch)
