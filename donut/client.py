from __future__ import annotations

from typing import Any

from .http import HTTPClient
from .endpoints import (
    AuctionEndpoint,
    LeaderboardsEndpoint,
    LookupEndpoint,
    StatsEndpoint,
)


class DonutClient:
    def __init__(
        self,
        api_keys: str | list[str],
        timeout: float = 30.0,
        requests_per_minute: int = 250,
    ):
        self._http = HTTPClient(api_keys, timeout, requests_per_minute)
        self.auction = AuctionEndpoint(self._http)
        self.leaderboards = LeaderboardsEndpoint(self._http)
        self.lookup = LookupEndpoint(self._http)
        self.stats = StatsEndpoint(self._http)

    async def close(self) -> None:
        await self._http.close()

    async def __aenter__(self) -> DonutClient:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

