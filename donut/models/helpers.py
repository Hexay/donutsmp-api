def format_time(ms: int) -> str:
    seconds = ms // 1000
    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, secs = divmod(remainder, 60)
    parts = []
    if days: parts.append(f"{days}d")
    if hours: parts.append(f"{hours}h")
    if minutes: parts.append(f"{minutes}m")
    if secs or not parts: parts.append(f"{secs}s")
    return " ".join(parts)


def clean_id(item_id: str) -> str:
    return item_id.replace("minecraft:", "").replace("_", " ").title()


def format_date(unix_ms: int) -> str:
    from datetime import datetime
    return datetime.fromtimestamp(unix_ms / 1000).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]




