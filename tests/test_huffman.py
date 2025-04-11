# tests/test_huffman.py
"""Pytest suite for Huffman codec."""
import random

import pytest

from text_compressor.algorithms.huffman import decode, encode


@pytest.mark.parametrize(
    "text",
    [
        "",  # empty
        "A",  # single char
        "The quick brown fox jumps over the lazy dog",  # pangram
        "😀" * 100,  # unicode emoji
        "ABABABABABABABABABABABAB",  # repetitive pattern
    ],
)
def test_roundtrip(text):
    assert decode(encode(text)) == text


def test_random_strings():
    for _ in range(50):
        length = random.randint(1, 500)
        s = "".join(chr(random.randint(32, 126)) for _ in range(length))
        assert decode(encode(s)) == s
