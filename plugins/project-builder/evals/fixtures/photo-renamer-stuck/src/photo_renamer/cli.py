import argparse
import os
import sys
from pathlib import Path

from photo_renamer.core.plan import plan_renames
from photo_renamer.io.files import list_photos


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="photo-renamer")
    p.add_argument("folder")
    p.add_argument("--dry_run", action="store_true")  # flag name has an underscore
    args = p.parse_args(argv)
    folder = Path(args.folder)
    pairs = plan_renames(list_photos(folder))
    for old, new in pairs:
        print(f"{old} -> {new}")
        if not getattr(args, "dry-run", False):
            os.rename(folder / old, folder / new)
    print(f"{len(pairs)} renamed, 0 skipped" + (" (dry run)" if args.dry_run else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
