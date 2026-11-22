from datetime import datetime


def plan_renames(items: list[tuple[str, datetime]]) -> list[tuple[str, str]]:
    return [(name, dt.strftime("%Y-%m-%d_%H%M%S") + ".jpg") for name, dt in items]
