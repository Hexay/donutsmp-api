from __future__ import annotations

import time
from collections import deque


class RateLimiter:
    def __init__(self, api_keys: list[str], requests_per_minute: int = 250):
        self._keys = api_keys
        self._limit = requests_per_minute
        self._index = 0
        self._timestamps: dict[str, deque[float]] = {k: deque() for k in api_keys}

    @property
    def keys(self) -> list[str]:
        return self._keys

    @property
    def capacity(self) -> int:
        return len(self._keys) * self._limit

    def _prune(self, key: str, now: float) -> None:
        ts = self._timestamps[key]
        cutoff = now - 65
        while ts and ts[0] < cutoff:
            ts.popleft()

    def _available(self, key: str, now: float) -> int:
        self._prune(key, now)
        return self._limit - len(self._timestamps[key])

    def record(self, key: str) -> None:
        now = time.monotonic()
        self._prune(key, now)
        self._timestamps[key].append(now)

    def next_key(self) -> str:
        key = self._keys[self._index]
        self._index = (self._index + 1) % len(self._keys)
        return key

    def distribute(self, count: int) -> list[list[str]]:
        now = time.monotonic()
        available = {k: self._available(k, now) for k in self._keys}
        total_available = sum(available.values())
        
        batch: list[str] = []
        remaining = count
        key_idx = 0
        num_keys = len(self._keys)
        
        while remaining > 0 and total_available > 0:
            key = self._keys[key_idx]
            if available[key] > 0:
                batch.append(key)
                self._timestamps[key].append(now)
                available[key] -= 1
                total_available -= 1
                remaining -= 1
            key_idx = (key_idx + 1) % num_keys
        
        if remaining > 0:
            overflow: list[str] = []
            while remaining > 0:
                key = self._keys[key_idx]
                overflow.append(key)
                remaining -= 1
                key_idx = (key_idx + 1) % num_keys
            return [batch, overflow] if batch else [overflow]
        
        return [batch] if batch else []
