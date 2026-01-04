# pdfkitx — PDF, ZIP & Google Drive CLI Toolkit 📄🔧

**pdfkitx** is a unified command-line toolkit for managing **PDF files**, **ZIP archives**, and **Google Drive**.
It supports **interactive**, **one-shot**, and **scripted workflows** using a **single shared command grammar**, ensuring consistent behavior across all modes.

Designed to be used as a standalone executable (`pdfkitx`) or via Python (`main.py`) for development.

---

## 🚀 Features

* **Interactive CLI** — Type commands in the REPL (`pdf`, `zip`, `drive`, `help`, `clear`, `exit`)
* **Google Drive integration** — Authenticate, list, upload, download, and share files
* **ZIP archive handling** — Add, extract, remove files and maintain a small index
* **PDF manipulation** — Split, extract, merge, delete pages
* **Scripting support** — Run plain-text scripts with batch commands
* **Cross-mode consistency** — Same grammar for REPL, CLI, and scripts
* **Python backend modules** — `pdf_manager/`, `zip_manager/`, `drive_manager/`
* **Utility helpers** — Path resolution and small helpers in `helper.py`

---

## 📥 Installation

### Requirements

* Python **3.10+**
* Optional: `credentials.json` for Google Drive

### Using the included virtual environment (recommended)

```powershell
.\pymupdf-venv\Scripts\Activate.ps1
```

### Or install dependencies manually

```powershell
pip install -r requirements.txt
```

---

## ⚡ Usage

### Interactive REPL

```powershell
pdfkitx
```

Example:

```
pdf split "report.pdf" "1-3,5"
exit
```

Exit with `exit`, `quit`, or `end`.

---

### One-shot CLI

```powershell
pdfkitx pdf merge a.pdf b.pdf --out merged.pdf
pdfkitx drive share myfile.pdf user@example.com
```

The program exits immediately after executing the command.

---

### Scripted Workflows

Script files are plain text:

* One command per line
* Blank lines ignored
* `#` starts a comment

**Example: `workflow.txt`**

```text
# split and upload a report
pdf split report.pdf 1-3 --delete
drive upload report_split/ reports
drive share reports reports@example.com
```

Run it:

```powershell
pdfkitx run workflow.txt
```

> Each line is parsed using the same `argparse` grammar as the REPL and one-shot commands.

---

## 🧾 Commands & Examples

### PDF

```powershell
pdf split <file> <ranges>        # e.g. "1-3,5"
pdf extract <file> <pages> <out>
pdf merge <in1> <in2> ... --out merged.pdf
```

### ZIP

```powershell
zip add <path> <archive>
zip extract <archive> [dest] [members ...]
zip remove <archive> <member>
```

### Google Drive

```powershell
drive init [username]
drive list
drive upload <path> [remote_folder]
drive share <target> [email]
```

Use `pdfkitx help` in the REPL or CLI for full command documentation.

---

## 🏗️ Design & Architecture

* **Single entrypoint** — `pdfkitx` or `main.py` decides mode and delegates parsing
* **One grammar, one dispatcher** — `commands.py` builds the complete `argparse` tree
* **Shared parsing** — REPL, CLI, and scripts use the same parser
* **Separation of concerns**:

  * `pdf_manager/` — PDF logic
  * `zip_manager/` — ZIP operations
  * `drive_manager/` — Google Drive API integration

---

## 🧪 Development & Tests

* Tests use **pytest** in the `tests/` directory
* Run tests:

```powershell
pip install -r requirements.txt
pytest -q
```

### Contributor Notes

* CLI grammar: `commands.py`
* Backend logic: appropriate manager module
* Mock external services (Drive API) in tests

---

## 📁 Files of Interest

* `main.py` — Program entrypoint
* `commands.py` — CLI grammar and dispatcher
* `repl.py` — Interactive REPL loop
* `help_docs.py` — Help text and examples
* `helper.py` — Path utilities
* `pdf_manager/` — PDF operations
* `zip_manager/` — ZIP operations
* `drive_manager/` — Google Drive integration

---

## ⚠️ Notes & Limitations

* Google Drive requires a valid `credentials.json` in the project root
* OAuth tokens (`token.pickle`) are created on first authentication
* Some subcommands may evolve; consult `help_docs.py` and tests for current behavior
* Error handling is conservative; missing paths may raise immediately

---

## 🤝 Contributing

Bug reports, feature requests, and pull requests are welcome.
Include tests and documentation updates for any new features.

---

## ✨ Recommended Improvements / TODO

* Complete CLI argument parsing for all PDF and ZIP subcommands
* Add verbose / dry-run modes for destructive operations
* Improve Drive listing, filtering, and name disambiguation
* Expand automated tests for all modules

---


