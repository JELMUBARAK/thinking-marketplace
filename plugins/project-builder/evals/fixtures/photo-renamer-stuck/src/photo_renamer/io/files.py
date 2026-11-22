from datetime import datetime
from pathlib import Path


def list_photos(folder: Path) -> list[tuple[str, datetime]]:
    return [(p.name, datetime.fromtimestamp(p.stat().st_mtime)) for p in sorted(folder.glob("*.jpg"))]
