"""Fail on common public-release hazards without opening proprietary inputs."""

from __future__ import annotations

import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
BLOCKED_NAMES = {".git", ".env", "token.txt", "credentials.json"}
BLOCKED_SUFFIXES = {".parquet", ".feather", ".pkl", ".pem", ".key", ".pyc"}
TEXT_SUFFIXES = {
    ".cff", ".csv", ".gitignore", ".json", ".md", ".py", ".toml", ".txt",
    ".yaml", ".yml",
}
CONTENT_PATTERNS = {
    "absolute local Windows path": re.compile(
        r"[A-Za-z]:\\\\(?:Users|Documents|Desktop)\\\\", re.IGNORECASE
    ),
    "AWS access key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "assigned password": re.compile(
        r"(?i)password\\s*=\\s*['\\\"][^'\\\"]+['\\\"]"
    ),
    "assigned secret/token": re.compile(
        r"(?i)(?:api[_-]?key|secret|token)\\s*=\\s*['\\\"][^'\\\"]+['\\\"]"
    ),
}


def main() -> None:
    findings: list[str] = []
    for path in ROOT.rglob("*"):
        relative = path.relative_to(ROOT)
        if any(part in BLOCKED_NAMES for part in relative.parts):
            findings.append(f"blocked name: {relative}")
            continue
        if not path.is_file():
            continue
        if path.suffix.lower() in BLOCKED_SUFFIXES:
            findings.append(f"blocked file type: {relative}")
            continue
        if path.suffix.lower() == ".ipynb":
            notebook = json.loads(path.read_text(encoding="utf-8"))
            for index, cell in enumerate(notebook.get("cells", [])):
                if cell.get("cell_type") == "code" and (
                    cell.get("outputs") or cell.get("execution_count") is not None
                ):
                    findings.append(f"notebook output: {relative} cell {index}")
                source = "".join(cell.get("source", []))
                for label, pattern in CONTENT_PATTERNS.items():
                    if pattern.search(source):
                        findings.append(f"{label}: {relative} cell {index}")
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name != ".gitignore":
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for label, pattern in CONTENT_PATTERNS.items():
            if pattern.search(text):
                findings.append(f"{label}: {relative}")

    if findings:
        raise SystemExit(
            "Public-release scan failed:\\n" + "\\n".join(sorted(set(findings)))
        )
    print(
        "Public-release scan passed: no blocked files, embedded notebook "
        "outputs, absolute local paths, or credential patterns found."
    )


if __name__ == "__main__":
    main()
