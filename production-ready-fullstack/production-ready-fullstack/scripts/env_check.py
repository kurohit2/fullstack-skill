#!/usr/bin/env python3
"""
env_check.py — checks env var hygiene for a project.

Usage:
    python env_check.py <path-to-repo>

Checks (per directory containing an .env or .env.example, searched
recursively — handles monorepos with frontend/ and backend/ subfolders):
  1. .env.example exists if .env exists
  2. .gitignore excludes .env* but NOT .env.example
  3. Every key in .env has a corresponding key in .env.example (and vice versa)
  4. .env.example doesn't contain suspiciously real-looking values
     (heuristic reuse of secret_scan.py patterns would be circular — kept
     simple here: flags values that aren't obviously placeholders)
"""
import sys
import os
import re

SKIP_DIRS = {".git", "node_modules", "venv", ".venv", "__pycache__", "dist", "build", ".next"}

PLACEHOLDER_HINTS = (
    "your_", "xxx", "changeme", "example", "placeholder", "<", "insert_",
    "replace_", "todo", "here", "sk_test_dummy", "dummy",
)


def parse_env_file(filepath):
    keys = {}
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, _, value = line.partition("=")
                    keys[key.strip()] = value.strip().strip('"').strip("'")
    except (IOError, OSError):
        pass
    return keys


def check_gitignore(dirpath):
    gitignore_path = os.path.join(dirpath, ".gitignore")
    if not os.path.exists(gitignore_path):
        # might be at repo root instead of this subdir; caller handles that
        return None
    with open(gitignore_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    ignores_env = bool(re.search(r"^\.env(\*|\.local)?$", content, re.MULTILINE)) or ".env" in content
    example_accidentally_ignored = bool(re.search(r"^\.env\.example$", content, re.MULTILINE))
    return {"ignores_env": ignores_env, "example_ignored": example_accidentally_ignored}


def looks_like_placeholder(value):
    if not value:
        return True
    lower = value.lower()
    return any(hint in lower for hint in PLACEHOLDER_HINTS) or len(value) < 8


def main():
    if len(sys.argv) != 2:
        print("Usage: python env_check.py <path-to-repo>")
        sys.exit(1)

    root = sys.argv[1]
    if not os.path.isdir(root):
        print(f"Not a directory: {root}")
        sys.exit(1)

    issues = []
    checked_any = False

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        has_env = ".env" in filenames
        has_example = ".env.example" in filenames

        if not has_env and not has_example:
            continue

        checked_any = True
        rel = os.path.relpath(dirpath, root)
        print(f"\n--- {rel if rel != '.' else '(root)'} ---")

        if has_env and not has_example:
            issues.append(f"{rel}: .env exists but no .env.example — other contributors (or future you) won't know what vars are required.")
            print("  ✗ .env exists, .env.example missing")
        elif has_example:
            print("  ✓ .env.example present")

        # gitignore check — look in this dir, then walk up to root if not found
        check_dir = dirpath
        gi_result = None
        while True:
            gi_result = check_gitignore(check_dir)
            if gi_result is not None or os.path.abspath(check_dir) == os.path.abspath(root):
                break
            check_dir = os.path.dirname(check_dir)
        if gi_result is None:
            issues.append(f"{rel}: no .gitignore found covering this directory — .env may not be excluded from git.")
            print("  ✗ no .gitignore found in this dir or above")
        else:
            if has_env and not gi_result["ignores_env"]:
                issues.append(f"{rel}: .env exists but .gitignore doesn't appear to exclude it — HIGH RISK of committing secrets.")
                print("  ✗ .gitignore does NOT appear to exclude .env")
            elif has_env:
                print("  ✓ .env appears gitignored")
            if gi_result["example_ignored"]:
                issues.append(f"{rel}: .gitignore excludes .env.example — this file SHOULD be committed so others know what vars are needed.")
                print("  ✗ .env.example is gitignored (it shouldn't be)")

        # key comparison
        if has_env and has_example:
            env_keys = set(parse_env_file(os.path.join(dirpath, ".env")).keys())
            example_keys = set(parse_env_file(os.path.join(dirpath, ".env.example")).keys())
            missing_from_example = env_keys - example_keys
            missing_from_env = example_keys - env_keys
            if missing_from_example:
                issues.append(f"{rel}: keys in .env but not documented in .env.example: {', '.join(sorted(missing_from_example))}")
                print(f"  ✗ in .env but not .env.example: {', '.join(sorted(missing_from_example))}")
            if missing_from_env:
                print(f"  ℹ in .env.example but not in local .env (may be optional or just not set locally): {', '.join(sorted(missing_from_env))}")
            if not missing_from_example:
                print("  ✓ .env keys all documented in .env.example")

        # real-looking values in .env.example
        if has_example:
            example_kv = parse_env_file(os.path.join(dirpath, ".env.example"))
            suspicious = [k for k, v in example_kv.items() if not looks_like_placeholder(v)]
            if suspicious:
                issues.append(f"{rel}: .env.example has values that don't look like placeholders (verify these aren't real secrets): {', '.join(suspicious)}")
                print(f"  ✗ possibly real values in .env.example: {', '.join(suspicious)}")

    if not checked_any:
        print("No .env or .env.example files found anywhere in this path.")
        sys.exit(0)

    print("\n=== Summary ===")
    if not issues:
        print("No env hygiene issues found.")
    else:
        for issue in issues:
            print(f"- {issue}")


if __name__ == "__main__":
    main()
