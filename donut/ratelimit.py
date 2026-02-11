from __future__ import annotations

import asyncio
import time
from collections import deque
from dataclasses import dataclass, field


@dataclass
class KeyBucket:
    key: str
    requests: deque[float] = field(default_factory=deque)

    def prune(self, window: float) -> None:
        cutoff = time.monotonic() - window
        while self.requests and self.requests[0] <= cutoff:
            self.requests.popleft()

    def available_at(self, limit: int, window: float) -> float:
        self.prune(window)
        if len(self.requests) < limit:
            return 0.0
        return self.requests[0] + window - time.monotonic()

    def record(self) -> None:
        self.requests.append(time.monotonic())


class RateLimiter:
    def __init__(self, api_keys: list[str], requests_per_minute: int = 250):
        self._limit = requests_per_minute
        self._window = 60.0
        self._buckets = [KeyBucket(key=k) for k in api_keys]
        self._index = 0
        self._lock = asyncio.Lock()

    @property
    def keys(self) -> list[str]:
        return [b.key for b in self._buckets]

    def _find_best_bucket(self) -> tuple[KeyBucket, float]:
        min_wait = float("inf")
        best = self._buckets[0]
        start = self._index

        for i in range(len(self._buckets)):
            bucket = self._buckets[(start + i) % len(self._buckets)]
            wait = bucket.available_at(self._limit, self._window)
            if wait <= 0:
                self._index = (start + i + 1) % len(self._buckets)
                return bucket, 0.0
            if wait < min_wait:
                min_wait = wait
                best = bucket

        return best, min_wait

    async def acquire(self) -> str:
        while True:
            async with self._lock:
                bucket, wait = self._find_best_bucket()
                if wait <= 0:
                    bucket.record()
                    return bucket.key

            await asyncio.sleep(wait)
