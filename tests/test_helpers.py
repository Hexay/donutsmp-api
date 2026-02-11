import pytest
from donut.helpers import format_number
from donut.models.helpers import clean_id, format_date, format_time


class TestFormatNumber:
    @pytest.mark.parametrize("value,expected", [
        (500, "500"),
        (1_000, "1.00K"),
        (1_500, "1.50K"),
        (1_000_000, "1.00M"),
        (2_500_000, "2.50M"),
        (1_000_000_000, "1.00B"),
        (1_000_000_000_000, "1.00T"),
    ])
    def test_format_number(self, value: float, expected: str):
        assert format_number(value) == expected


class TestFormatTime:
    @pytest.mark.parametrize("ms,expected", [
        (0, "0s"),
        (1000, "1s"),
        (60_000, "1m"),
        (3600_000, "1h"),
        (86400_000, "1d"),
        (90061_000, "1d 1h 1m 1s"),
    ])
    def test_format_time(self, ms: int, expected: str):
        assert format_time(ms) == expected


class TestCleanId:
    @pytest.mark.parametrize("item_id,expected", [
        ("minecraft:diamond_sword", "Diamond Sword"),
        ("diamond_pickaxe", "Diamond Pickaxe"),
        ("minecraft:golden_apple", "Golden Apple"),
    ])
    def test_clean_id(self, item_id: str, expected: str):
        assert clean_id(item_id) == expected


class TestFormatDate:
    def test_format_date(self):
        result = format_date(1700000000000)
        assert "2023-11-14" in result

