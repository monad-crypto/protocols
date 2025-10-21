#!/usr/bin/env python3
"""
validate_protocol.py

Validate protocol metadata JSON files in the `testnet/` folder.

Checks for required fields: `name`, `description`, `links`, and `categories`.
"""

import json
import os
import sys

REQUIRED_FIELDS = ["name", "description", "links", "categories"]

def validate_file(filepath: str) -> bool:
    """Validate one JSON metadata file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Error reading {filepath}: {e}")
        return False

    missing = [field for field in REQUIRED_FIELDS if field not in data]
    if missing:
        print(f"⚠️ {filepath} missing: {', '.join(missing)}")
        return False

    print(f"✅ {filepath} is valid.")
    return True

def main():
    base_dir = os.path.join(os.path.dirname(__file__), "..", "testnet")
    if not os.path.isdir(base_dir):
        print("❌ testnet/ directory not found.")
        sys.exit(1)

    json_files = [f for f in os.listdir(base_dir) if f.endswith(".json")]
    if not json_files:
        print("⚠️ No JSON files found in testnet/")
        sys.exit(0)

    print(f"🔍 Validating {len(json_files)} files...\n")
    valid = all(validate_file(os.path.join(base_dir, f)) for f in json_files)

    if not valid:
        sys.exit(1)

if __name__ == "__main__":
    main()
￼Enter
