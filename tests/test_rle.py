###############################################################################
# tests/test_rle.py
###############################################################################

import random

import pytest

from text_compressor.algorithms.rle import decode, encode


@pytest.mark.parametrize(
    "text",
    [
        "",  # empty
        "A",  # single char
        "AAAAA",  # single run < 255
        "A" * 300,  # run > 255
        "ABABABAB",  # alternating
        "😀😀😀😀😀",  # unicode (UTF‑8) – will encode ord points
    ],
)
def test_roundtrip(text):
    assert decode(encode(text)) == text


def test_random_roundtrip():
    alphabet = "ABC"
    for _ in range(100):
        text = "".join(random.choice(alphabet) for _ in range(random.randint(1, 512)))
        assert decode(encode(text)) == text
