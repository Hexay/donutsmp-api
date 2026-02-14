from __future__ import annotations

from collections.abc import Iterator
from typing import Any, Generic, Literal, TypeVar

from pydantic import BaseModel, field_validator

from ..helpers import format_number
from .helpers import clean_id, format_date, format_time

AuctionSort = Literal["lowest_price", "highest_price", "recently_listed", "last_listed"]

T = TypeVar("T")


class ListResponse(BaseModel, Generic[T]):
    status: int | None = None
    result: list[T] | None = None

    def __iter__(self) -> Iterator[T]:  # type: ignore[override]
        return iter(self.result or [])

    def __len__(self) -> int:
        return len(self.result or [])

    def __getitem__(self, index: int) -> T:
        if self.result is None:
            raise IndexError("No results")
        return self.result[index]

    def __str__(self) -> str:
        if not self.result:
            return "No results"
        return "\n".join(f"{i+1}. {item}" for i, item in enumerate(self.result))


class SingleResponse(BaseModel, Generic[T]):
    status: int | None = None
    result: T | None = None

    def __str__(self) -> str:
        return str(self.result) if self.result else "No result"


class Seller(BaseModel):
    name: str | None = None
    uuid: str | None = None

    def __str__(self) -> str:
        return self.name or self.uuid or "Unknown"


class Trim(BaseModel):
    material: str | None = None
    pattern: str | None = None


class Enchantments(BaseModel):
    levels: dict[str, int] | None = None

    def __str__(self) -> str:
        if not self.levels:
            return ""
        return ", ".join(f"{k.title()} {v}" for k, v in self.levels.items())


class ItemData(BaseModel):
    enchantments: Enchantments | None = None
    trim: Trim | None = None


class ContainerItem(BaseModel):
    id: str | None = None
    display_name: str | None = None
    count: int | None = None
    enchants: ItemData | None = None

    def __str__(self) -> str:
        name = self.display_name or (clean_id(self.id) if self.id else "Unknown")
        return f"{name} x{self.count}" if self.count and self.count > 1 else name


class Item(BaseModel):
    id: str | None = None
    display_name: str | None = None
    count: int | None = None
    lore: list[str] | None = None
    enchants: ItemData | None = None
    contents: list[ContainerItem] | None = None

    def __str__(self) -> str:
        name = self.display_name or (clean_id(self.id) if self.id else "Unknown")
        parts = [f"{name} x{self.count}" if self.count and self.count > 1 else name]
        if self.enchants and self.enchants.enchantments and self.enchants.enchantments.levels:
            parts.append(f"[{self.enchants.enchantments}]")
        if self.contents:
            parts.append(f"({len(self.contents)} items)")
        return " ".join(parts)


class AuctionEntry(BaseModel):
    item: Item | None = None
    price: float | None = None
    seller: Seller | None = None
    time_left: int | None = None

    def __str__(self) -> str:
        item_str = str(self.item) if self.item else "Unknown Item"
        price_str = format_number(self.price) if self.price else "?"
        seller_str = str(self.seller) if self.seller else "Unknown"
        time_str = format_time(self.time_left) if self.time_left else "?"
        return f"{item_str} | {price_str} | by {seller_str} | {time_str}"


class AuctionResponse(ListResponse[AuctionEntry]):
    pass


class AuctionRequestBody(BaseModel):
    search: str | None = None
    sort: AuctionSort | None = None


class PurchaseItem(BaseModel):
    item: Item | None = None
    price: float | None = None
    seller: Seller | None = None
    unixMillisDateSold: int | None = None

    def __str__(self) -> str:
        item_str = str(self.item) if self.item else "Unknown Item"
        price_str = format_number(self.price) if self.price else "?"
        seller_str = str(self.seller) if self.seller else "Unknown"
        date_str = format_date(self.unixMillisDateSold) if self.unixMillisDateSold else "?"
        return f"{item_str} | {price_str} | from {seller_str} | {date_str}"


class TransactionHistoryResponse(ListResponse[PurchaseItem]):
    pass


class LeaderboardEntry(BaseModel):
    username: str | None = None
    uuid: str | None = None
    value: float = 0

    @field_validator("value", mode="before")
    @classmethod
    def parse_value(cls, v: Any) -> float:
        return float(v) if v else 0

    def __str__(self) -> str:
        return f"{self.username or 'Unknown'}: {self.value}"


class LeaderboardResponse(ListResponse[LeaderboardEntry]):
    pass


class LookupResult(BaseModel):
    username: str | None = None
    rank: str | None = None
    location: str | None = None

    def __str__(self) -> str:
        parts = [self.username or "Unknown"]
        if self.rank: parts.append(f"[{self.rank}]")
        if self.location: parts.append(f"@ {self.location}")
        return " ".join(parts)


class LookupResponse(SingleResponse[LookupResult]):
    pass


class Stats(BaseModel):
    username: str | None = None
    money: str | None = None
    shards: str | None = None
    playtime: str | None = None
    kills: str | None = None
    deaths: str | None = None
    mobs_killed: str | None = None
    broken_blocks: str | None = None
    placed_blocks: str | None = None
    money_made_from_sell: str | None = None
    money_spent_on_shop: str | None = None

    _LABELS = {
        "money": "Money", "shards": "Shards", "playtime": "Playtime",
        "kills": "Kills", "deaths": "Deaths", "mobs_killed": "Mobs Killed",
        "broken_blocks": "Blocks Broken", "placed_blocks": "Blocks Placed",
        "money_made_from_sell": "Sell Income", "money_spent_on_shop": "Shop Spent",
    }

    def __str__(self) -> str:
        header = self.username or "Unknown"
        lines = [f"{self._LABELS[f]}: {v}" for f in self._LABELS if (v := getattr(self, f))]
        return f"{header}\n" + "\n".join(lines) if lines else header


class StatsResponse(SingleResponse[Stats]):
    pass



