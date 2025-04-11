# utils/bitstream.py
"""Bit‑level read/write helpers for Text‑Compressor.

Two utility classes are provided:
* **BitWriter** – append individual bits or fixed‑width fields and obtain the resulting bytes object.
* **BitReader** – consume bits from an immutable bytes object at bit‑precision.

Design goals
------------
* **MSB‑first** ordering inside each byte (network / PNG style).
* Track the *exact* number of meaningful bits so padding zeros never confuse the reader or the test harness.
* Pure‑Python, dependency‑free, easy to unit‑test.
"""
from __future__ import annotations

from typing import List, Optional

__all__ = ["BitWriter", "BitReader"]


# ---------------------------------------------------------------------------
# BitWriter
# ---------------------------------------------------------------------------
class BitWriter:
    """Accumulates bits and produces a *bytes* object on demand."""

    __slots__ = ("_buffer", "_bit_pos", "_nbits")

    def __init__(self) -> None:
        self._buffer: List[int] = [0]  # working byte list
        self._bit_pos: int = 0  # next position inside current byte (0‑7)
        self._nbits: int = 0  # total *meaningful* bits written

    # ------------------------------------------------------------------
    # Write helpers
    # ------------------------------------------------------------------
    def write_bit(self, bit: int) -> None:
        if bit not in (0, 1):
            raise ValueError("bit must be 0 or 1, got %r" % bit)
        byte_idx = len(self._buffer) - 1
        self._buffer[byte_idx] |= bit << (7 - self._bit_pos)
        self._bit_pos += 1
        self._nbits += 1
        if self._bit_pos == 8:
            self._buffer.append(0)
            self._bit_pos = 0

    def write_bits(self, value: int, width: int) -> None:
        if width < 0:
            raise ValueError("width must be non‑negative")
        if value < 0 or value >= 1 << width:
            raise ValueError("value %d does not fit in %d bits" % (value, width))
        for i in reversed(range(width)):
            self.write_bit((value >> i) & 1)

    def pad_to_byte(self, pad_bit: int = 0) -> None:
        """Pad with *pad_bit* until byte‑aligned.

        Padding bits are **structural**; they are *not* counted in ``nbits``."""
        if pad_bit not in (0, 1):
            raise ValueError("pad_bit must be 0 or 1")
        if self._bit_pos == 0:
            return  # already aligned
        pad_needed = 8 - self._bit_pos  # 1–7 bits
        for _ in range(pad_needed):
            # write_bit increases _nbits; roll back afterwards
            self.write_bit(pad_bit)
        self._nbits -= pad_needed  # exclude structural padding

    # ------------------------------------------------------------------
    # Output helpers
    # ------------------------------------------------------------------
    def get_bytes(self) -> bytes:
        """Return accumulated data as *bytes* (no stray empty byte)."""
        if self._bit_pos == 0 and len(self._buffer) > 1:
            return bytes(self._buffer[:-1])
        return bytes(self._buffer)

    # Properties --------------------------------------------------------
    @property
    def nbits(self) -> int:
        """Total meaningful bits written."""
        return self._nbits

    # Context manager ---------------------------------------------------
    def __enter__(self) -> "BitWriter":
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


# ---------------------------------------------------------------------------
# BitReader
# ---------------------------------------------------------------------------
class BitReader:
    """Iterates over bits from an immutable *bytes* object (MSB first)."""

    __slots__ = ("_data", "_total_bits", "_bits_read", "_byte_idx", "_bit_pos")

    def __init__(self, data: bytes, total_bits: Optional[int] = None):
        if not isinstance(data, (bytes, bytearray)):
            raise TypeError("data must be bytes‑like")
        self._data = data
        self._total_bits = total_bits if total_bits is not None else len(data) * 8
        self._bits_read = 0
        self._byte_idx = 0
        self._bit_pos = 0

    # ------------------------------------------------------------------
    # Read helpers
    # ------------------------------------------------------------------
    def read_bit(self) -> int:
        if self._bits_read >= self._total_bits:
            raise EOFError("No more bits to read")
        byte = self._data[self._byte_idx]
        bit = (byte >> (7 - self._bit_pos)) & 1
        self._bit_pos += 1
        self._bits_read += 1
        if self._bit_pos == 8:
            self._bit_pos = 0
            self._byte_idx += 1
        return bit

    def read_bits(self, width: int) -> int:
        if width < 0:
            raise ValueError("width must be non‑negative")
        value = 0
        for _ in range(width):
            value = (value << 1) | self.read_bit()
        return value

    def bits_left(self) -> int:
        return self._total_bits - self._bits_read

    # Iterable interface
    def __iter__(self):
        return self

    def __next__(self):
        try:
            return self.read_bit()
        except EOFError as exc:
            raise StopIteration from exc
