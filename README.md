# DonutSMP API Wrapper

![PyPI - Version](https://img.shields.io/pypi/v/donutsmp-api)
![PyPI - Downloads](https://img.shields.io/pypi/dm/donutsmp-api)

An async Python wrapper for the DonutSMP API with full type safety using Pydantic models.

## Installation

```bash
pip install donutsmp-api
```

## Quick Start

```python
import asyncio
from donut import DonutClient

async def main():
    async with DonutClient("your-api-key") as client:
        stats = await client.stats("archivepedro")
        print(stats)

asyncio.run(main())
```

## Features

- Fully async with `aiohttp`
- Type-safe responses via Pydantic models
- Built-in rate limiting (configurable)
- Support for multiple API keys (automatic rotation)

## API Reference

### Client Configuration

```python
client = DonutClient(
    api_keys="key",              # Single key or list of keys
    timeout=30.0,                # Request timeout in seconds
    requests_per_minute=250      # Rate limit
)
```

### Stats

```python
stats = await client.stats("username")
```

### Leaderboards

```python
# Single page
leaderboard = await client.leaderboards("money", page=1)

# Batch fetch multiple pages
pages = await client.leaderboards.batch("money", start_page=1, end_page=100)

# Category shortcuts
await client.leaderboards.money(page=1)
await client.leaderboards.kills(page=1)
await client.leaderboards.playtime(page=1)
```

**Available categories:** `money`, `shards`, `playtime`, `kills`, `deaths`, `mobskilled`, `brokenblocks`, `placedblocks`, `sell`, `shop`

### Auction House

```python
# List active auctions
auctions = await client.auction.list(page=1, search="diamond", sort="price_asc")

# Recent transactions
transactions = await client.auction.transactions(page=1)
```

### Player Lookup

```python
# Single lookup
player = await client.lookup("username")

# Batch lookup
players = await client.lookup.batch(["user1", "user2", "user3"])
```

## Examples

See the [examples](./examples) directory for more usage patterns:

- [`stats.py`](./examples/stats.py) - Basic stats lookup
- [`batch_leaderboard.py`](./examples/batch_leaderboard.py) - Fetching multiple leaderboard pages
- [`finished_auctions.py`](./examples/finished_auctions.py) - Polling for new auction transactions
- [`leaderboard_estimation.py`](./examples/leaderboard_estimation.py) - Estimating total server wealth using adaptive sampling

## License

MIT
