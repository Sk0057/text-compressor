############################################
# text_compressor/cli.py  (overwrites previous stub)
############################################
"""Command‑line interface for Text‑Compressor."""
from __future__ import annotations

import sys
from pathlib import Path

import click

from text_compressor.compressors import CompressorFactory


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def cli() -> None:
    """Lossless text compression using RLE or Huffman coding."""


@cli.command()
@click.argument("input", type=click.Path(exists=True, path_type=Path))
@click.argument("output", type=click.Path(path_type=Path))
@click.option(
    "--algo",
    "-a",
    default="huffman",
    show_default=True,
    type=click.Choice(["rle", "huffman"], case_sensitive=False),
    help="Compression algorithm to use.",
)
@click.option("--force", "-f", is_flag=True, help="Overwrite OUTPUT if it exists.")
@click.option(
    "--verbose", "-v", is_flag=True, help="Print statistics after completion."
)
def compress(input: Path, output: Path, algo: str, force: bool, verbose: bool):
    """Compress INPUT file and write to OUTPUT."""
    if output.exists() and not force:
        click.echo("Error: OUTPUT exists – use --force to overwrite.", err=True)
        sys.exit(1)

    comp = CompressorFactory.get(algo)
    comp.compress(input, output)

    if verbose:
        ratio = (
            output.stat().st_size / input.stat().st_size if input.stat().st_size else 0
        )
        click.echo(
            f"Done. {input.stat().st_size} → {output.stat().st_size} bytes (ratio {ratio:.2f})."
        )


@cli.command()
@click.argument("input", type=click.Path(exists=True, path_type=Path))
@click.argument("output", type=click.Path(path_type=Path))
@click.option("--force", "-f", is_flag=True, help="Overwrite OUTPUT if it exists.")
@click.option(
    "--verbose", "-v", is_flag=True, help="Print statistics after completion."
)
def decompress(input: Path, output: Path, force: bool, verbose: bool):
    """Decompress INPUT archive to OUTPUT text file."""
    if output.exists() and not force:
        click.echo("Error: OUTPUT exists – use --force to overwrite.", err=True)
        sys.exit(1)

    # Detect algo from header
    with input.open("rb") as f:
        magic = f.read(4)
    algo = "rle" if magic == b"RLE1" else "huffman" if magic == b"HUF1" else None
    if algo is None:
        click.echo("Error: Unsupported or corrupted archive.", err=True)
        sys.exit(2)

    comp = CompressorFactory.get(algo)
    comp.decompress(input, output)

    if verbose:
        click.echo(f"Restored {output.stat().st_size} bytes.")


if __name__ == "__main__":
    cli()
