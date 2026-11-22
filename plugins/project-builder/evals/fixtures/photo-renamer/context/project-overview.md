# photo-renamer

## Overview

A command-line tool that renames the photos in a folder to `YYYY-MM-DD_HHMMSS.<ext>`, using the date each photo
was taken (EXIF). It is for one user tidying phone exports on Windows. A dry-run mode shows every
planned rename before anything changes.

## Goals

1. Rename a folder of 500 photos in under 10 seconds.
2. Zero overwritten files, ever.
3. A dry run shows exactly what a real run would do.

## Core Flow

1. User runs `photo-renamer <folder> --dry-run`.
2. Tool prints `old -> new` for each photo, then a summary.
3. User runs `photo-renamer <folder>` without `--dry-run`.
4. Tool renames the files and prints the same lines and summary.

## Features

### Renaming
- Name from the EXIF date taken; skip files that have no date.
- Clash handling: add `_1`, `_2` and so on.

### Safety
- `--dry-run` previews and renames nothing.

## Scope

### In Scope
- JPEG and HEIC files in one folder (not subfolders).

### Out of Scope
- GUI, cloud folders, video files, editing EXIF, recursive folders, undo.

## Success Criteria

1. `--dry-run` on a test folder prints one correct line per photo and renames nothing.
2. A real run renames every dated photo and overwrites nothing.
3. `pytest` passes.
