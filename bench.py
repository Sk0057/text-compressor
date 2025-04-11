# bench.py
from __future__ import annotations

import pathlib
import time

from text_compressor.compressors import CompressorFactory

CORPUS = pathlib.Path("samples").glob("*.txt")
ROW = "{:<20}{:>10}{:>10}{:>8}{:>9}"

print(ROW.format("File", "Orig KB", "Algo", "Ratio", "Time"))
print("-" * 57)

for txt in CORPUS:
    data = txt.read_text(encoding="utf-8")
    orig_bytes = len(data.encode())
    for algo in ("rle", "huffman"):
        comp = CompressorFactory.get(algo)
        t0 = time.perf_counter()
        blob = comp.compress_text(data)  # helper method in compressors.py
        elapsed = time.perf_counter() - t0
        ratio = len(blob) / orig_bytes
        print(
            ROW.format(
                txt.name[:18] + ("…" if len(txt.name) > 18 else ""),
                f"{orig_bytes//1024}",
                algo,
                f"{ratio:.2f}",
                f"{elapsed:.3f}",
            )
        )
