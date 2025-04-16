# text_compressor/algorithms/huffman.py
"""Huffman‑coding compressor for Text‑Compressor.

Implements a canonical static Huffman code for any UTF‑8 text.  The on‑disk
format is:

    +---------+----------+-----------+--------------+--------------+
    | Header  |  CRC32   | Tree Size |  Tree Bytes  | Enc. Bits... |
    | 5 bytes | 4 bytes  | 2 bytes   |  var. bytes  |   var. bits  |
    +---------+----------+-----------+--------------+--------------+

* Header  = b"HUF1" + version(1).
* Tree    = pre‑order serialisation where internal nodes are marked with 0x00
  and leaves with 0x01 + 1‑byte symbol.
* Encoded bits are padded with 0s to the next byte; total meaningful bits is
  stored in the last 2 bytes of the tree serialisation (so the reader knows
  when to stop).
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import zlib

from text_compressor.utils.bitstream import BitReader, BitWriter
from text_compressor.utils.stats import Stats, Timer

__all__ = [
    "encode",
    "decode",
    "HuffmanCompressor",
]

_MAGIC = b"HUF1\x01"  # 5‑byte header (4‑byte tag + version)


@dataclass(order=True)
class _Node:
    freq: int
    symbol: Optional[int] = None  # None for internal nodes
    left: Optional["_Node"] = None
    right: Optional["_Node"] = None

    def is_leaf(self) -> bool:
        return self.symbol is not None


# ---------------------------------------------------------------------------
# Helper – build tree & code table
# ---------------------------------------------------------------------------


def _build_tree(data: bytes) -> _Node:
    heap: List[_Node] = [_Node(f, s) for s, f in Counter(data).items()]
    heap.sort()  # simple list as priority queue (n is small for text)
    while len(heap) > 1:
        n1, n2 = heap.pop(0), heap.pop(0)
        parent = _Node(n1.freq + n2.freq, None, n1, n2)
        # re‑insert maintaining sort by freq
        idx = 0
        while idx < len(heap) and heap[idx].freq < parent.freq:
            idx += 1
        heap.insert(idx, parent)
    return heap[0]


def _gen_codes(root: _Node) -> Dict[int, str]:
    codes: Dict[int, str] = {}

    def dfs(node: _Node, prefix: str):
        if node.is_leaf():
            codes[node.symbol] = prefix or "0"  # single‑node edge case
        else:
            dfs(node.left, prefix + "0")
            dfs(node.right, prefix + "1")

    dfs(root, "")
    return codes


# ---------------------------------------------------------------------------
# Serialisation helpers
# ---------------------------------------------------------------------------


def _serialize_tree(node: _Node, out: bytearray):
    if node.is_leaf():
        out.append(0x01)
        out.append(node.symbol)  # already 0‑255
    else:
        out.append(0x00)
        _serialize_tree(node.left, out)
        _serialize_tree(node.right, out)


def _deserialize_tree(reader: memoryview, idx: int = 0) -> Tuple[_Node, int]:
    flag = reader[idx]
    idx += 1
    if flag == 0x01:
        sym = reader[idx]
        idx += 1
        return _Node(0, sym), idx
    # internal
    left, idx = _deserialize_tree(reader, idx)
    right, idx = _deserialize_tree(reader, idx)
    return _Node(0, None, left, right), idx


# ---------------------------------------------------------------------------
# Public encode / decode helpers (stateless)
# ---------------------------------------------------------------------------


def encode(text: str) -> bytes:
    """Return Huffman‑compressed bytes for *text* (UTF‑8)."""
    if not text:
        return b""

    data = text.encode("utf-8")

    # 1️⃣  Build tree and code‑map
    root = _build_tree(data)
    codes = _gen_codes(root)

    # 2️⃣  Encode the data bit‑by‑bit
    bw = BitWriter()
    for byte in data:
        for bit in codes[byte]:
            bw.write_bit(int(bit))
    bw.pad_to_byte()
    bitstream = bw.get_bytes()
    total_bits = bw.nbits  # meaningful bits before padding

    # 3️⃣  Serialize tree in pre‑order
    tree_buf = bytearray()
    _serialize_tree(root, tree_buf)  # fills tree_buf
    tree_buf.extend(total_bits.to_bytes(3, "big"))  # 🔹 append bit‑count here

    # 4️⃣  Now compute *tree_size* including the 2‑byte bit‑count
    tree_size = len(tree_buf).to_bytes(2, "big")  # big‑endian

    # 5️⃣  Assemble final archive
    crc = zlib.crc32(data).to_bytes(4, "little")
    header = _MAGIC + crc + tree_size  # 5 + 4 + 2 bytes
    return header + bytes(tree_buf) + bitstream


# algorithms/huffman.py  – inside decode()


def decode(buf: bytes) -> str:
    if not buf:
        return ""

    if buf[:5] != _MAGIC:
        raise ValueError("Invalid Huffman header")

    crc = int.from_bytes(buf[5:9], "little")
    tree_size = int.from_bytes(buf[9:11], "big")
    tree_end = 11 + tree_size
    tree_mv = memoryview(buf[11:tree_end])
    root, idx = _deserialize_tree(tree_mv)
    total_bits = int.from_bytes(tree_mv[idx : idx + 3], "big")

    # 🔹 Special‑case: single‑leaf tree
    if root.is_leaf():
        decoded_bytes = bytes([root.symbol] * (total_bits or 1))
        if zlib.crc32(decoded_bytes) != crc:
            raise ValueError("CRC mismatch – corrupted archive")
        return decoded_bytes.decode("utf-8")

    reader = BitReader(buf[tree_end:], total_bits)
    out = bytearray()
    node = root

    while True:
        try:
            bit = reader.read_bit()
        except EOFError:
            break
        node = node.left if bit == 0 else node.right
        if node.is_leaf():
            out.append(node.symbol)
            node = root

    if zlib.crc32(out) != crc:
        raise ValueError("CRC mismatch – corrupted archive")
    return out.decode("utf-8")


# ---------------------------------------------------------------------------
# Compressor wrapper (for CLI)
# ---------------------------------------------------------------------------


class HuffmanCompressor:
    """File‑oriented compressor used by CLI."""

    ext = ".huff"

    def compress(self, in_path: Path, out_path: Path) -> Stats:
        raw = in_path.read_text(encoding="utf-8")
        with Timer() as t:
            comp = encode(raw)
        out_path.write_bytes(comp)
        return Stats(
            len(raw.encode("utf-8")),
            len(comp),
            len(comp) / len(raw.encode("utf-8")),
            t.elapsed,
        )

    def decompress(self, in_path: Path, out_path: Path) -> Stats:
        comp = in_path.read_bytes()
        with Timer() as t:
            raw = decode(comp)
        out_path.write_text(raw, encoding="utf-8")
        return Stats(
            len(raw.encode("utf-8")),
            len(comp),
            len(comp) / len(raw.encode("utf-8")),
            t.elapsed,
        )
