import pytest
from donut.models import (
    AuctionEntry,
    ContainerItem,
    Enchantments,
    Item,
    ItemData,
    LeaderboardEntry,
    LeaderboardResponse,
    ListResponse,
    LookupResult,
    PurchaseItem,
    Seller,
    SingleResponse,
    Stats,
    Trim,
)


class TestListResponse:
    def test_empty_response(self):
        response: ListResponse[str] = ListResponse(result=None)
        assert len(response) == 0
        assert str(response) == "No results"

    def test_iteration(self):
        response: ListResponse[str] = ListResponse(result=["a", "b", "c"])
        assert list(response) == ["a", "b", "c"]
        assert len(response) == 3

    def test_indexing(self):
        response: ListResponse[str] = ListResponse(result=["a", "b"])
        assert response[0] == "a"
        assert response[1] == "b"

    def test_index_error_on_empty(self):
        response: ListResponse[str] = ListResponse(result=None)
        with pytest.raises(IndexError):
            _ = response[0]


class TestSingleResponse:
    def test_with_result(self):
        response: SingleResponse[str] = SingleResponse(result="test")
        assert str(response) == "test"

    def test_without_result(self):
        response: SingleResponse[str] = SingleResponse(result=None)
        assert str(response) == "No result"


class TestSeller:
    def test_str_with_name(self):
        seller = Seller(name="Player1", uuid="abc-123")
        assert str(seller) == "Player1"

    def test_str_with_uuid_only(self):
        seller = Seller(uuid="abc-123")
        assert str(seller) == "abc-123"

    def test_str_unknown(self):
        seller = Seller()
        assert str(seller) == "Unknown"


class TestEnchantments:
    def test_str_with_levels(self):
        enchants = Enchantments(levels={"sharpness": 5, "fire_aspect": 2})
        assert "Sharpness 5" in str(enchants)
        assert "Fire_Aspect 2" in str(enchants)

    def test_str_empty(self):
        enchants = Enchantments()
        assert str(enchants) == ""


class TestContainerItem:
    def test_str_with_display_name(self):
        item = ContainerItem(display_name="Cool Sword", count=1)
        assert str(item) == "Cool Sword"

    def test_str_with_count(self):
        item = ContainerItem(display_name="Diamond", count=64)
        assert str(item) == "Diamond x64"

    def test_str_from_id(self):
        item = ContainerItem(id="minecraft:diamond_sword", count=1)
        assert str(item) == "Diamond Sword"


class TestItem:
    def test_basic_str(self):
        item = Item(display_name="Test Item", count=1)
        assert str(item) == "Test Item"

    def test_str_with_count(self):
        item = Item(display_name="Diamond", count=32)
        assert str(item) == "Diamond x32"

    def test_str_with_enchants(self):
        item = Item(
            display_name="Sword",
            enchants=ItemData(enchantments=Enchantments(levels={"sharpness": 5}))
        )
        assert "Sharpness 5" in str(item)

    def test_str_with_contents(self):
        item = Item(
            display_name="Shulker Box",
            contents=[ContainerItem(display_name="Item")]
        )
        assert "(1 items)" in str(item)


class TestLeaderboardEntry:
    def test_value_parsing(self):
        entry = LeaderboardEntry(username="Player", value="1000")  # type: ignore
        assert entry.value == 1000.0

    def test_value_default(self):
        entry = LeaderboardEntry(username="Player")
        assert entry.value == 0

    def test_str(self):
        entry = LeaderboardEntry(username="Player", value=500)
        assert str(entry) == "Player: 500.0"


class TestLookupResult:
    def test_str_full(self):
        result = LookupResult(username="Player", rank="VIP", location="Spawn")
        assert str(result) == "Player [VIP] @ Spawn"

    def test_str_minimal(self):
        result = LookupResult()
        assert str(result) == "Unknown"


class TestAuctionEntry:
    def test_str(self):
        entry = AuctionEntry(
            item=Item(display_name="Diamond"),
            price=1000,
            seller=Seller(name="Player"),
            time_left=60000
        )
        result = str(entry)
        assert "Diamond" in result
        assert "1.00K" in result
        assert "Player" in result


class TestPurchaseItem:
    def test_str(self):
        item = PurchaseItem(
            item=Item(display_name="Sword"),
            price=500,
            seller=Seller(name="Seller"),
            unixMillisDateSold=1700000000000
        )
        result = str(item)
        assert "Sword" in result
        assert "500" in result
        assert "Seller" in result


class TestStats:
    def test_str(self):
        stats = Stats(money="1000", kills="50", deaths="10")
        result = str(stats)
        assert "Money: 1000" in result
        assert "Kills: 50" in result
        assert "Deaths: 10" in result

    def test_str_empty(self):
        stats = Stats()
        assert str(stats) == ""

