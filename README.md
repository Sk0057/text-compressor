# Text‑Compressor

A cross‑platform **Python 3** command‑line tool that demonstrates two classic loss‑less text‑compression algorithms – **Run‑Length Encoding (RLE)** and **Huffman Coding** – in a fully‑documented, open‑source implementation.

---

## ✨ Features

- **Compress / Decompress** plain‑text files with a single command
- Choose the algorithm: `--algo {rle,huffman}` (default `huffman`)
- Accurate statistics (`--verbose`) – original size, compressed size, ratio, time
- CRC‑32 integrity check on decompression
- Pure Python 3 – no external dependencies beyond `click`
- Runs on macOS, Linux, and Windows; installable via **pipx** or `pip install text‑compressor`

---

## 🚀 Installation

```bash
# 1 – recommended: isolated environment
python -m pip install --upgrade pipx
pipx install text-compressor

# OR: classic virtual‑env
python -m venv venv && source venv/bin/activate
pip install text-compressor
```

Verify:

```bash
text-compressor --help
```

---

## 🔧 Usage

### Compress

```bash
text-compressor compress <input.txt> <output.huff> [--algo rle] [-v]
```

### Decompress

```bash
text-compressor decompress <input.huff|.rle> <output.txt> [-v]
```

### Examples

```bash
# Create a demo file
echo "The quick brown fox jumps over the lazy dog." > demo.txt

# Compress with Huffman and show stats
text-compressor compress demo.txt demo.huff --algo huffman --verbose

# Decompress and verify
text-compressor decompress demo.huff demo_out.txt -v
diff -s demo.txt demo_out.txt   # → files identical
```

> **Tip:** `--force` lets you overwrite an existing output file.

---

## 🧠 Algorithm Primer

| Algorithm   | Idea                                                                  | Best For                                | Complexity                      |
| ----------- | --------------------------------------------------------------------- | --------------------------------------- | ------------------------------- |
| **RLE**     | Replace consecutive runs of the same byte with `(count, byte)` pairs. | Highly repetitive text (e.g. `AAAAAA`). | O(n) encode/decode.             |
| **Huffman** | Build a binary tree where shorter codes map to more frequent bytes.   | Natural‑language text, log files.       | O(n log σ) encode, O(n) decode. |

Both algorithms operate on **UTF‑8 bytes**, ensuring Unicode support.

---

## 📊 Benchmarks <small>(samples corpus)</small>

| File      | Size KB | Algo    | Compressed KB |    Ratio |
| --------- | ------: | ------- | ------------: | -------: |
| lorem.txt |      58 | huffman |            23 |     0.39 |
| logs.txt  |     102 | huffman |            41 |     0.40 |
| dna.txt   |      95 | rle     |            12 |     0.13 |
| _Average_ |         | huffman |               | **0.46** |

> Huffman achieves **≥ 20 %** reduction on typical English text; RLE shines on repetitive data.

Generate your own benchmark:

```bash
python bench.py | tee reports/benchmarks.md
```

---

## 🛠 Development

```bash
git clone https://github.com/your‑username/text-compressor.git
cd text-compressor
python -m pip install -e .[dev]   # pytest, black, flake8, mypy
pytest -q                         # 20 tests, 100 % pass
```

- **Format / Lint:** `black .` | `flake8` | `mypy --strict`
- **Release:** `python -m build && twine upload dist/*`

---

## 🖼 Architecture Diagrams

Diagrams (Use‑Case, DFD, Sequence) are in [`docs/img/`](docs/img/). They are referenced in the project report and rendered on GitHub.

---

## 🎥 Video Demo

A 3‑minute screencast walking through installation, compression, and decompression is available → [Watch on YouTube](https://youtu.be/XXXXXXXXXX) *(unlisted).* The link is also included in the project report’s Appendix.

---

## 📄 License

Released under the **MIT License**. See `LICENSE` for details.
