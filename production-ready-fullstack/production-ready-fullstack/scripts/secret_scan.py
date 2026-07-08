#!/usr/bin/env python3
"""
secret_scan.py — scan a repo for likely hardcoded secrets/credentials.

Usage:
    python secret_scan.py <path-to-repo>

Not a substitute for a real secret-scanning tool (gitleaks, trufflehog) on
a project handling real money/PII — this is a fast, dependency-free first
pass to catch obvious cases. Skips common dirs (node_modules, .git, venv,
dist/build, etc.) and binary files.
"""
import re
import sys
import os

SKIP_DIRS = {
    ".git", "node_modules", "venv", ".venv", "__pycache__", "dist",
    "build", ".next", ".vercel", "env", ".env_cache", "site-packages",
    ".mypy_cache", ".pytest_cache",
}

SKIP_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".woff", ".woff2",
    ".ttf", ".eot", ".pdf", ".zip", ".gz", ".lock", ".map",
}

# (label, regex) — intentionally conservative to keep false positives down,
# but err toward flagging when unsure; a false positive costs a glance,
# a missed real secret costs a breach.
PATTERNS = [
    ("AWS Access Key", r"AKIA[0-9A-Z]{16}"),
    ("Generic API Key assignment", r"(?i)(api[_-]?key|apikey)\s*[:=]\s*['\"][A-Za-z0-9_\-]{16,}['\"]"),
    ("Generic Secret assignment", r"(?i)(secret|token)\s*[:=]\s*['\"][A-Za-z0-9_\-]{16,}['\"]"),
    ("Razorpay Key", r"rzp_(live|test)_[A-Za-z0-9]{10,}"),
    ("Stripe Key", r"sk_(live|test)_[A-Za-z0-9]{16,}"),
    ("Supabase/JWT-style token", r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"),
    ("Private Key block", r"-----BEGIN (RSA |EC )?PRIVATE KEY-----"),
    ("Hardcoded DB URL with credentials", r"(postgres|postgresql|mysql|mongodb)(\+[a-z]+)?://[^:\s]+:[^@\s]+@"),
    ("Slack Token", r"xox[baprs]-[A-Za-z0-9-]{10,}"),
    ("Google API Key", r"AIza[0-9A-Za-z_\-]{35}"),
]

COMPILED = [(label, re.compile(pattern)) for label, pattern in PATTERNS]

# Filenames that are *expected* to contain example/placeholder secrets —
# still scan them, but tag findings differently.
EXAMPLE_FILE_HINTS = (".example", ".sample", "template")


def should_skip_dir(dirname: str) -> bool:
    return dirname in SKIP_DIRS or dirname.startswith(".")


def should_skip_file(filename: str) -> bool:
    ext = os.path.splitext(filename)[1].lower()
    return ext in SKIP_EXTENSIONS


def scan_file(filepath: str):
    findings = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for lineno, line in enumerate(f, start=1):
                for label, pattern in COMPILED:
                    if pattern.search(line):
                        findings.append((label, lineno, line.strip()[:120]))
    except (IOError, OSError):
        pass
    return findings


def main():
    if len(sys.argv) != 2:
        print("Usage: python secret_scan.py <path-to-repo>")
        sys.exit(1)

    root = sys.argv[1]
    if not os.path.isdir(root):
        print(f"Not a directory: {root}")
        sys.exit(1)

    total_findings = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not should_skip_dir(d)]
        for filename in filenames:
            if should_skip_file(filename):
                continue
            filepath = os.path.join(dirpath, filename)
            findings = scan_file(filepath)
            if findings:
                is_example = any(hint in filename.lower() for hint in EXAMPLE_FILE_HINTS)
                rel = os.path.relpath(filepath, root)
                for label, lineno, snippet in findings:
                    total_findings += 1
                    tag = "[EXAMPLE FILE — verify it's a real placeholder, not a leaked real key]" if is_example else "[REVIEW]"
                    print(f"{tag} {rel}:{lineno} — {label}")
                    print(f"    {snippet}")

    print()
    if total_findings == 0:
        print("No likely hardcoded secrets found by pattern scan.")
        print("Note: this is a pattern-based first pass, not a guarantee — for anything handling real payments/PII, also run gitleaks or trufflehog, and check git history for secrets removed in later commits (they're still compromised).")
    else:
        print(f"{total_findings} potential finding(s) above. Review each — pattern matches can be false positives, but every real API key/token found should be rotated if it was ever committed, even if removed since.")


if __name__ == "__main__":
    main()
