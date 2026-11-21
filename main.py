#!/usr/bin/env python3
"""SKYHOLD - make.fun entry program.

The poster for this entry is a finished image asset (asset.png, kept next
to this program). This program does not redraw it. It checks that the
asset is a genuine PNG inside the competition limits, then delivers it as
entry.png in the output directory.

Behaviour:
  * the asset is read from the same directory as this program;
  * the asset must start with the PNG signature (89 50 4E 47 0D 0A 1A 0A),
    be at most 1,048,576 bytes, and be at most 1024x1024 pixels (the
    dimensions come from the IHDR chunk, and every chunk's CRC is checked,
    so a truncated or corrupted file is refused);
  * the output directory is $MAKEFUN_OUTPUT_DIR when set, otherwise
    /output when it exists, otherwise ./output next to this program;
  * stale files inside the output directory are removed, but the output
    directory itself is never removed;
  * entry.png is written through a temporary file plus rename, so a
    reader never sees a half-written file.
"""

from __future__ import annotations

import os
import struct
import sys
import tempfile
import zlib
from pathlib import Path

MAX_BYTES = 1_048_576
MAX_WIDTH = 1024
MAX_HEIGHT = 1024
ASSET_NAME = "asset.png"
ENTRY_NAME = "entry.png"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


class AssetError(ValueError):
    """The poster asset failed validation."""


def read_png_dimensions(data: bytes) -> tuple[int, int]:
    """Return (width, height) from a PNG stream, checking chunk CRCs.

    Every chunk is walked through to IEND, so a truncated file or a
    corrupted chunk anywhere in the stream is refused; the dimensions
    come from the IHDR chunk, which must be the first chunk.
    """
    if len(data) < 8 or data[:8] != PNG_SIGNATURE:
        raise AssetError("not a PNG file: missing PNG signature")
    pos = 8
    total = len(data)
    width = height = None
    first = True
    while True:
        if pos + 8 > total:
            raise AssetError("PNG data ended before the IEND chunk")
        (length,) = struct.unpack(">I", data[pos:pos + 4])
        chunk_type = data[pos + 4:pos + 8]
        body_start = pos + 8
        body_end = body_start + length
        if body_end + 4 > total:
            raise AssetError(f"truncated PNG chunk {chunk_type!r}")
        stored_crc, = struct.unpack(">I", data[body_end:body_end + 4])
        actual_crc = zlib.crc32(chunk_type)
        actual_crc = zlib.crc32(data[body_start:body_end], actual_crc)
        if actual_crc != stored_crc:
            raise AssetError(f"bad CRC in PNG chunk {chunk_type!r}")
        if first and chunk_type != b"IHDR":
            raise AssetError("first PNG chunk is not IHDR")
        first = False
        if chunk_type == b"IHDR":
            if length != 13:
                raise AssetError("bad IHDR chunk length in PNG header")
            width, height = struct.unpack(">II", data[body_start:body_start + 8])
        if chunk_type == b"IEND":
            break
        pos = body_end + 4
    if width is None or height is None:
        raise AssetError("no IHDR chunk found in PNG data")
    return width, height


def load_and_validate(asset_path: Path) -> tuple[bytes, int, int]:
    """Read the asset, validate it, return (data, width, height)."""
    try:
        data = asset_path.read_bytes()
    except OSError as exc:
        raise AssetError(f"cannot read {asset_path}: {exc}") from exc
    if len(data) > MAX_BYTES:
        raise AssetError(
            f"asset too large: {len(data)} bytes (limit {MAX_BYTES})"
        )
    width, height = read_png_dimensions(data)
    if width > MAX_WIDTH or height > MAX_HEIGHT:
        raise AssetError(
            f"asset too big: {width}x{height} "
            f"(limit {MAX_WIDTH}x{MAX_HEIGHT})"
        )
    return data, width, height


def resolve_output_dir() -> Path:
    """Pick the output directory: env var, /output, or ./output."""
    env_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "").strip()
    if env_dir:
        return Path(env_dir)
    if Path("/output").is_dir():
        return Path("/output")
    return Path(__file__).resolve().parent / "output"


def clear_stale_files(out_dir: Path) -> int:
    """Remove stale files inside out_dir; never touch out_dir itself."""
    removed = 0
    for item in out_dir.iterdir():
        if item.is_file() or item.is_symlink():
            item.unlink()
            removed += 1
    return removed


def write_entry(out_dir: Path, data: bytes) -> Path:
    """Write entry.png via a temporary file plus atomic rename."""
    target = out_dir / ENTRY_NAME
    fd, tmp_name = tempfile.mkstemp(
        prefix=".entry-", suffix=".tmp", dir=out_dir
    )
    try:
        with os.fdopen(fd, "wb") as tmp:
            tmp.write(data)
            tmp.flush()
            os.fsync(tmp.fileno())
        os.replace(tmp_name, target)
    except BaseException:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise
    return target


def main() -> int:
    here = Path(__file__).resolve().parent
    asset_path = here / ASSET_NAME
    try:
        data, width, height = load_and_validate(asset_path)
    except AssetError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    out_dir = resolve_output_dir()
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        removed = clear_stale_files(out_dir)
        target = write_entry(out_dir, data)
    except OSError as exc:
        print(f"error: cannot write output in {out_dir}: {exc}", file=sys.stderr)
        return 1
    print(
        f"SKYHOLD entry written: {target} "
        f"({width}x{height} PNG, {len(data)} bytes; "
        f"{removed} stale file(s) removed)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
