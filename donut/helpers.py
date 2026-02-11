def format_number(num: float) -> str:
    if num >= 1_000_000_000_000:
        return f"{num/1_000_000_000_000:.2f}T"
    if num >= 1_000_000_000:
        return f"{num/1_000_000_000:.2f}B"
    if num >= 1_000_000:
        return f"{num/1_000_000:.2f}M"
    if num >= 1_000:
        return f"{num/1_000:.2f}K"
    return f"{num:.0f}"