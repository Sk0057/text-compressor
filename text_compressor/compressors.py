############################################
# text_compressor/compressors.py
############################################
"""Factory & common interface that unify RLE and Huffman compressors."""
from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable

from text_compressor.algorithms.rle import RLECompressor  # type: ignore
from text_compressor.algorithms.huffman import HuffmanCompressor  # type: ignore


@runtime_checkable
class Compressor(Protocol):
    """Behaviour every compressor must expose."""

    def compress(self, in_path: Path, out_path: Path) -> None: ...

    def decompress(self, in_path: Path, out_path: Path) -> None: ...


class CompressorFactory:
    """Return a compressor instance for the requested algorithm."""

    _registry = {
        "rle": RLECompressor,
        "huffman": HuffmanCompressor,
    }

    @classmethod
    def get(cls, name: str) -> Compressor:
        key = name.lower()
        if key not in cls._registry:
            raise ValueError(f"Unsupported algorithm: {name}")
        return cls._registry[key]()
