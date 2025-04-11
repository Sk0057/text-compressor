############################################
# tests/test_cli.py
############################################
"""Integration tests invoking CLI as a subprocess."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CLI = [sys.executable, "-m", "text_compressor.cli"]


def _run(args: list[str]):
    return subprocess.run(CLI + args, capture_output=True, text=True, check=True)


@pytest.fixture(scope="module")
def sample(tmp_path_factory: pytest.TempPathFactory) -> Path:
    p = tmp_path_factory.mktemp("data") / "sample.txt"
    p.write_text("Hello Huffman!" * 10)
    return p


def test_cli_roundtrip(sample, tmp_path):
    comp = tmp_path / "out.huff"
    decomp = tmp_path / "back.txt"

    _run(["compress", str(sample), str(comp), "--algo", "huffman"])
    _run(["decompress", str(comp), str(decomp)])

    assert decomp.read_text() == sample.read_text()
