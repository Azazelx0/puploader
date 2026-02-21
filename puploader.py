#!/usr/bin/env python3
"""puploader: simple no-code terminal uploader using Python standard library."""

from __future__ import annotations

import argparse
import mimetypes
import sys
import uuid
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen


def prompt_non_empty(message: str) -> str:
    while True:
        value = input(message).strip()
        if value:
            return value
        print("Input cannot be empty. Please try again.")


def prompt_existing_file(message: str) -> Path:
    while True:
        raw_path = input(message).strip()
        if not raw_path:
            print("File path cannot be empty. Please try again.")
            continue

        file_path = Path(raw_path).expanduser()
        if not file_path.exists():
            print(f"File does not exist: {file_path}")
            continue
        if not file_path.is_file():
            print(f"Path is not a file: {file_path}")
            continue
        return file_path


def validate_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def build_multipart_body(field_name: str, file_path: Path) -> tuple[bytes, str]:
    boundary = f"----puploader-{uuid.uuid4().hex}"
    mime_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
    file_bytes = file_path.read_bytes()

    safe_filename = file_path.name.replace('"', "")
    encoded_filename = quote(file_path.name)

    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="{field_name}"; filename="{safe_filename}"; filename*=UTF-8\'\'{encoded_filename}\r\n'
        f"Content-Type: {mime_type}\r\n\r\n"
    ).encode("utf-8") + file_bytes + f"\r\n--{boundary}--\r\n".encode("utf-8")

    content_type = f"multipart/form-data; boundary={boundary}"
    return body, content_type


def upload_file(url: str, file_path: Path, field_name: str, timeout: int = 30) -> tuple[int, str]:
    body, content_type = build_multipart_body(field_name, file_path)

    request = Request(
        url=url,
        data=body,
        method="POST",
        headers={
            "Content-Type": content_type,
            "Content-Length": str(len(body)),
            "User-Agent": "puploader/1.1",
        },
    )

    with urlopen(request, timeout=timeout) as response:
        response_text = response.read().decode("utf-8", errors="replace")
        return response.status, response_text


def perform_upload(url: str, file_path: Path, field_name: str, timeout: int) -> int:
    print("\nUploading...")
    try:
        status_code, response_text = upload_file(url, file_path, field_name, timeout=timeout)
        print(f"\nUpload finished with HTTP {status_code}.")
        if response_text:
            print("Server response (first 1000 chars):")
            print(response_text[:1000])
        return 0
    except HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
        print(f"\nUpload failed with HTTP {exc.code}: {exc.reason}")
        if error_body:
            print("Server response (first 1000 chars):")
            print(error_body[:1000])
        return 1
    except URLError as exc:
        print(f"\nUpload failed: Could not reach server ({exc.reason}).")
        return 1
    except OSError as exc:
        print(f"\nUpload failed: {exc}")
        return 1


def run_tui(default_field_name: str, default_timeout: int) -> int:
    print("╭────────────────────────────────────────────────────────────╮")
    print("│                       📤 PUPLOADER                         │")
    print("│         (Simple Standard Library File Uploader)            │")
    print("╰────────────────────────────────────────────────────────────╯")
    print(" This tool uploads one file to an HTTP endpoint.\n")

    while True:
        url = prompt_non_empty("Upload URL: ")
        if not validate_url(url):
            print("URL must start with http:// or https:// and include a host.")
            print()
            continue

        file_path = prompt_existing_file("Path to file: ")
        perform_upload(url, file_path, default_field_name, default_timeout)

        again = input("\nUpload another file? (y/N): ").strip().lower()
        if again not in {"y", "yes"}:
            print("Goodbye!")
            return 0
        print()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Simple file uploader. Run with no arguments for interactive mode, "
            "or provide --url and --file for one-shot mode."
        )
    )
    parser.add_argument("--url", help="Upload URL, e.g. http://127.0.0.1:8000/upload")
    parser.add_argument("--file", dest="file_path", help="Path to file to upload")
    parser.add_argument("--field", default="files", help="Multipart form field name (default: files)")
    parser.add_argument("--timeout", type=int, default=30, help="HTTP timeout in seconds (default: 30)")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.timeout <= 0:
        print("Timeout must be greater than zero.", file=sys.stderr)
        return 2

    if args.url or args.file_path:
        if not args.url or not args.file_path:
            print("In one-shot mode, both --url and --file are required.", file=sys.stderr)
            return 2
        if not validate_url(args.url):
            print("URL must start with http:// or https:// and include a host.", file=sys.stderr)
            return 2

        file_path = Path(args.file_path).expanduser()
        if not file_path.exists() or not file_path.is_file():
            print(f"File does not exist or is not a file: {file_path}", file=sys.stderr)
            return 2

        return perform_upload(args.url, file_path, args.field, args.timeout)

    if not sys.stdin.isatty():
        print(
            "No arguments provided and no interactive terminal detected. "
            "Use --url and --file for non-interactive usage.",
            file=sys.stderr,
        )
        return 1

    try:
        return run_tui(default_field_name=args.field, default_timeout=args.timeout)
    except KeyboardInterrupt:
        print("\nCancelled by user.")
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
