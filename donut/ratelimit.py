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
        cutoff = now - 60
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
        
        batches: list[list[str]] = []
        remaining = count
        
        while remaining > 0:
            batch: list[str] = []
            for key in self._keys:
                take = min(remaining, available[key])
                batch.extend([key] * take)
                available[key] -= take
                remaining -= take
                if remaining == 0:
                    break
            
            if batch:
                batches.append(batch)
            else:
                batch_size = min(remaining, self.capacity)
                batch = [self._keys[i % len(self._keys)] for i in range(batch_size)]
                batches.append(batch)
                remaining -= batch_size
        
        return batches
