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

## 🔐 Google Drive Setup (BYOC)

This application uses **Bring Your Own Credentials (BYOC)** for Google Drive integration. This means you must set up your own Google Cloud OAuth credentials—there are no hardcoded app credentials from the developer.

### Why BYOC?

* **Security**: No shared credentials means no security audits needed for the application itself
* **Privacy**: Your data access is under your control
* **Flexibility**: Works with any Google account

### Setup Steps

1. **Create a Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Click "Select a Project" and then "New Project"
   - Enter a project name (e.g., "pdfkitx") and click Create

2. **Enable the Google Drive API**
   - In the Cloud Console, go to APIs & Services > Library
   - Search for "Google Drive API"
   - Click on it and press "Enable"

3. **Create OAuth 2.0 Credentials**
   - Go to APIs & Services > Credentials
   - Click "Create Credentials" > "OAuth client ID"
   - If prompted, first create an OAuth consent screen (External type is fine for personal use)
   - Choose "Desktop application" as the application type
   - Click Create

4. **Download Your Credentials**
   - In the Credentials page, find your newly created OAuth client
   - Click the download icon (⬇️) next to it
   - Save the downloaded JSON file as `credentials.json` in the project root directory

5. **Verify the Setup**
   - Copy the template if needed:
     ```powershell
     cp credentials.json.example credentials.json
     ```
   - Replace the placeholder values with those from your downloaded credentials file
   - The file should contain your actual `client_id` and `client_secret`

### First Use

When you first run a Drive command:

```powershell
pdfkitx drive list
```

Your browser will open, asking you to sign in and grant access. After you authorize, an OAuth token (`token.pickle`) is created and stored locally for future use.

### Security Notes

* **Never commit `credentials.json`** — It's in `.gitignore` for a reason
* **Keep your `client_secret` private** — Treat it like a password
* **`token.pickle` is local** — OAuth tokens are stored only on your machine

---

## 🤖 LLM Setup (BYOC)

This application supports **AI-powered command generation** using Gemini (or other LLMs). Like Google Drive, it uses **Bring Your Own Credentials (BYOC)** — you provide your own API key, not embedded from the developer.

### Why BYOC?

* **No dependencies on developer credentials** — You maintain full control
* **Privacy** — Your API usage is under your account
* **Cost control** — You see your own API charges

### Setup Steps

1. **Get a Gemini API Key**
   - Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
   - Click "Create API Key"
   - Copy your API key

2. **Create `llm_key.json`**
   - Copy from template:
     ```powershell
     cp llm_key.json.example llm_key.json
     ```
   - Edit `llm_key.json` and replace `YOUR_GEMINI_API_KEY_HERE` with your actual key
   - File should look like:
     ```json
     {
       "provider": "google",
       "api_key": "sk-proj-xxxxx..."
     }
     ```

3. **Verify Setup**
   - Start the REPL: `pdfkitx`
   - Try: `llm ask "split report.pdf into 2 halves"`
   - You should see generated commands to approve

### Usage: `llm ask`

**`llm ask` is only available in interactive REPL mode.**

The workflow:
1. Enter your request in natural language
2. The LLM generates command(s) based on the command schema
3. You review the generated commands and choose to:
   - **Approve (y)** — Execute all commands
   - **Reject (n)** — Cancel and try again
   - **Modify (m)** — Edit a specific command
   - **Regenerate (r)** — Ask the LLM to try again (all or a specific command)

**Example session:**

```
:>> llm ask upload my files to google drive in a folder called "backup"
Generating commands...
Generated commands:
  1. drive upload . backup

Execute commands? (y)es / (n)o / (m)odify command / (r)egenerate: y
Executing commands...
  > drive upload . backup
... (command runs)
```

### Security Notes

* **Never commit `llm_key.json`** — It's in `.gitignore` for a reason
* **Keep your API key private** — Treat it like a password
* **Generated commands are validated** — Basic syntax checks before execution
* **User approval required** — LLM-generated commands require explicit approval before running

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

### LLM (AI-Powered)

```powershell
llm ask <natural language request>  # REPL only, requires llm_key.json setup
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

* **Google Drive requires BYOC setup** — See "Google Drive Setup (BYOC)" section above
* PDF and ZIP functionality work normally without Drive credentials
* OAuth tokens (`token.pickle`) are created and stored locally on first authentication
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


