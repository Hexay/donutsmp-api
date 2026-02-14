from __future__ import annotations

import asyncio
from typing import Any

import aiohttp
import orjson

from .errors import DonutAPIError, NotFoundError, ServerError, UnauthorizedError
from .ratelimit import RateLimiter


class HTTPClient:
    BASE_URL = "https://api.donutsmp.net"

    def __init__(self, api_keys: str | list[str], timeout: float = 30.0):
        keys = [api_keys] if isinstance(api_keys, str) else api_keys
        if not keys:
            raise ValueError("At least one API key is required")
        self._rate_limiter = RateLimiter(keys)
        self._timeout = aiohttp.ClientTimeout(total=timeout)
        self._session: aiohttp.ClientSession | None = None
        self._session_lock = asyncio.Lock()

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is not None and not self._session.closed:
            return self._session
        async with self._session_lock:
            if self._session is None or self._session.closed:
                connector = aiohttp.TCPConnector(
                    limit=1000,
                    ttl_dns_cache=300,
                    keepalive_timeout=30,
                )
                self._session = aiohttp.ClientSession(
                    connector=connector,
                    connector_owner=True,
                    timeout=self._timeout,
                )
        return self._session

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()

    async def _handle_response(self, response: aiohttp.ClientResponse) -> dict[str, Any]:
        if response.status == 401:
            raise UnauthorizedError("Invalid or missing API key")
        if response.status == 404:
            raise NotFoundError("Resource not found")
        if response.status >= 500:
            raise ServerError(f"Server error: {response.status}")
        if response.status == 429:
            return {}
        if not response.ok:
            raise DonutAPIError(f"Request failed: {response.status}")
        return orjson.loads(await response.read())

    async def _request(
        self,
        method: str,
        endpoint: str,
        api_key: str,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        session = await self._get_session()
        headers = {"Authorization": f"Bearer {api_key}"}
        if json is not None:
            headers["Content-Type"] = "application/json"
        async with session.request(
            method,
            f"{self.BASE_URL}{endpoint}",
            params=params,
            data=orjson.dumps(json) if json else None,
            headers=headers,
        ) as response:
            return await self._handle_response(response)

    async def get(self, endpoint: str, json: dict[str, Any] | None = None, **params: Any) -> dict[str, Any]:
        key = self._rate_limiter.next_key()
        return await self._request("GET", endpoint, key, json, params or None)

    async def get_with_key(self, endpoint: str, api_key: str, json: dict[str, Any] | None = None, **params: Any) -> dict[str, Any]:
        self._rate_limiter.record(api_key)
        return await self._request("GET", endpoint, api_key, json, params or None)

    async def put(self, endpoint: str, data: dict[str, Any]) -> dict[str, Any]:
        key = self._rate_limiter.next_key()
        return await self._request("PUT", endpoint, key, data)

    async def __aenter__(self) -> HTTPClient:
        await self._get_session()
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()
