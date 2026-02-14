from __future__ import annotations


class RateLimiter:
    def __init__(self, api_keys: list[str], requests_per_minute: int = 250):
        self._keys = api_keys
        self._limit = requests_per_minute
        self._index = 0

    @property
    def keys(self) -> list[str]:
        return self._keys

    @property
    def capacity(self) -> int:
        return len(self._keys) * self._limit

    def next_key(self) -> str:
        key = self._keys[self._index]
        self._index = (self._index + 1) % len(self._keys)
        return key

    def distribute(self, count: int) -> list[list[str]]:
        batches: list[list[str]] = []
        remaining = count
        while remaining > 0:
            batch_size = min(remaining, self.capacity)
            batch = [self._keys[i % len(self._keys)] for i in range(batch_size)]
            batches.append(batch)
            remaining -= batch_size
        return batches
