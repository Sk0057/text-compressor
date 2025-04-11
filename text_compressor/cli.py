import click


@click.group()
def cli() -> None:
    """Text‑Compressor CLI."""
    pass


if __name__ == "__main__":
    cli()
