# ---------------------------------------------------------------------------
# Pytest suite – tests/test_bitstream.py
# ---------------------------------------------------------------------------

import random

import pytest


def test_single_byte_roundtrip():
    from text_compressor.utils.bitstream import BitReader, BitWriter

    bw = BitWriter()
    pattern = [1, 0, 1, 1, 0, 0, 0, 1]
    for bit in pattern:
        bw.write_bit(bit)
    bw.pad_to_byte()
    data = bw.get_bytes()
    assert data == b"\xb1"

    br = BitReader(data, bw.nbits)
    assert [br.read_bit() for _ in range(8)] == pattern
    assert br.bits_left() == 0


def test_write_bits_various_widths():
    from text_compressor.utils.bitstream import BitReader, BitWriter

    bw = BitWriter()
    bw.write_bits(0b101, 3)
    bw.write_bits(0b11110000, 8)
    bw.pad_to_byte()
    br = BitReader(bw.get_bytes(), bw.nbits)
    assert br.read_bits(3) == 0b101
    assert br.read_bits(8) == 0b11110000
    assert br.bits_left() == 0


def test_random_roundtrip():
    from text_compressor.utils.bitstream import BitReader, BitWriter

    for _ in range(100):
        bits = [random.randint(0, 1) for _ in range(random.randint(1, 256))]
        bw = BitWriter()
        for b in bits:
            bw.write_bit(b)
        br = BitReader(bw.get_bytes(), bw.nbits)
        out = [br.read_bit() for _ in range(len(bits))]
        assert out == bits
        assert br.bits_left() == 0


def test_reader_eof():
    from text_compressor.utils.bitstream import BitReader, BitWriter

    bw = BitWriter()
    bw.write_bits(0, 3)
    br = BitReader(bw.get_bytes(), bw.nbits)
    br.read_bits(3)
    with pytest.raises(EOFError):
        br.read_bit()
