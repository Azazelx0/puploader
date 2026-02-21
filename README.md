<h1 align="center">📤 puploader</h1>

<p align="center">
  <em>A zero-dependency terminal tool for uploading files over HTTP — built entirely on Python's standard library.</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.8%2B-3776AB?logo=python&logoColor=white" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/dependencies-none-success" alt="No Dependencies">
  <img src="https://img.shields.io/badge/license-MIT-blue" alt="MIT License">
</p>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🖥️ **Interactive Mode** | Guided prompts — no flags to remember |
| ⚡ **One-Shot Mode** | Upload in a single command via CLI args |
| 📦 **Zero Dependencies** | Uses only Python's standard library — no `pip install` needed |
| 🔒 **Multipart Upload** | Sends files as `multipart/form-data` with proper MIME types |
| 🌐 **Unicode-Safe** | Correctly handles filenames with special characters |

---

## 🚀 Quick Start

### Interactive Mode

```bash
python3 puploader.py
```

or use the wrapper script:

```bash
./puploader
```

You'll be prompted for the upload URL and file path — that's it!

### One-Shot Mode

```bash
python3 puploader.py \
  --url "http://127.0.0.1:8000/upload" \
  --file "/path/to/file.txt"
```

### Optional Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--field` | `files` | Multipart form field name |
| `--timeout` | `30` | HTTP timeout in seconds |

---

## 📋 Requirements

- **Python 3.8** or newer
- No external packages required ✅

---

## 💡 Example

```
$ python3 puploader.py
========================================================
                 puploader (No coding needed)
========================================================
This tool uploads one file to an HTTP endpoint.

Upload URL: http://localhost:8000/upload
Path to file: ./report.pdf

Uploading...

Upload finished with HTTP 200.
Server response (first 1000 chars):
{"status": "ok", "filename": "report.pdf"}

Upload another file? (y/N): n
Goodbye!
```

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to open an issue or submit a pull request.

## 📄 License

This project is open source. See the [LICENSE](LICENSE) file for details.
