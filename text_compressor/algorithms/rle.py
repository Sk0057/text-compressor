# algorithms/rle.py
"""Run‑Length Encoding (RLE) algorithm – encode & decode helpers
and a high‑level *RLECompressor* class compatible with the project‑wide
*Compressor* interface (compress / decompress / returns Stats)."""
from __future__ import annotations

from pathlib import Path
from text_compressor.utils.stats import (
    Stats,
    Timer,
)  # Stats & Timer helpers will be added later

__all__ = ["encode", "decode", "RLECompressor"]

_MAGIC = b"RLE1"  # 4‑byte header
_VERSION = 1  # 1‑byte version

###############################################################################
# Low‑level encode / decode working on *str*  →  *bytes* and vice‑versa.
###############################################################################


def encode(text: str) -> bytes:
    """Return RLE‑compressed *bytes* for the given UTF‑8 string."""
    if not text:
        return b""

    data = text.encode("utf-8")  # 🔹 convert to bytes first
    out = bytearray()
    prev = data[0]
    count = 1
    for b in data[1:]:
        if b == prev and count < 255:
            count += 1
        else:
            out.extend((count, prev))
            prev, count = b, 1
    out.extend((count, prev))
    return bytes(out)


def decode(buf: bytes) -> str:
    """Inverse of *encode* – returns the original UTF‑8 string."""
    if not buf:
        return ""

    if len(buf) % 2 != 0:
        raise ValueError("Corrupted RLE stream length")

    out = bytearray()
    it = iter(buf)
    for count, value in zip(it, it):
        out.extend([value] * count)
    return out.decode("utf-8")


###############################################################################
# High‑level file compressor
###############################################################################


class RLECompressor:
    """File‑oriented wrapper that writes/reads header, CRC, etc."""

    def compress(self, in_path: Path, out_path: Path) -> Stats:
        timer = Timer()
        text = Path(in_path).read_text(encoding="utf-8")
        payload = encode(text)

        with open(out_path, "wb") as f:
            f.write(_MAGIC)
            f.write(_VERSION.to_bytes(1, "little"))
            f.write(payload)

        return Stats(
            orig_bytes=len(text.encode("utf-8")),
            comp_bytes=len(payload) + 5,
            seconds=timer.stop(),
        )

    def decompress(self, in_path: Path, out_path: Path) -> Stats:
        timer = Timer()
        with open(in_path, "rb") as f:
            header = f.read(4)
            if header != _MAGIC:
                raise ValueError("Not an RLE archive")
            version = int.from_bytes(f.read(1), "little")
            if version != _VERSION:
                raise ValueError("Unsupported RLE version")
            payload = f.read()

        text = decode(payload)
        Path(out_path).write_text(text, encoding="utf-8")
        return Stats(
            orig_bytes=len(text.encode("utf-8")),
            comp_bytes=len(payload) + 5,
            seconds=timer.stop(),
        )
