#!/usr/bin/env python3
"""
Protocols to CSV Converter

This script collects all Protocol files in a directory and generates a CSV file
for upload to a DB, plus a JSON file keyed by protocol filename.
"""

import argparse
import csv
import json
import json5
import os

from pathlib import Path
from typing import Any, List, Dict, Tuple


# Define a function to parse JSON protocol files
def parse_protocol_file(file_path: str) -> Tuple[List[Dict[str, str]], Dict[str, Any]]:
    """
    Parse a single JSON file and extract the required fields.

    Returns a tuple of (csv_rows, raw_data). raw_data is the full parsed
    document so callers can also emit a JSON-keyed-by-filename output.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json5.load(f)

        # Extract common fields
        name = data.get("name", "")

        # Get first category or empty string if no categories
        categories = data.get("categories", [])
        if not categories:
            print(f"⚠️  {name}: missing category – skipped")
            return [], {}
        first_category = categories[0]
        parts = first_category.split("::")
        if len(parts) != 2:
            print(f"⚠️  {name}: invalid category format '{first_category}' – skipped")
            return [], {}

        type, subtype = parts[0], parts[1]

        # Join all categories for the new column
        all_categories = ";".join(categories)

        # Get addresses
        addresses = data.get("addresses", {})

        # Create rows - one for each address
        rows = []
        for contract_name, address in sorted(addresses.items()):
            row = {
                "name": name,
                "ctype": type,
                "csubtype": subtype,
                "contract": contract_name,
                "address": address.lower(),
                "all_categories": all_categories,
            }
            rows.append(row)

        return rows, data

    except (json5.JSONDecodeError, FileNotFoundError, KeyError) as e:
        print(f"Error processing {file_path}: {e}")
        return [], {}


# Define a function to collect protocol files in a given directory
def collect_protocol_files(directory: str) -> List[str]:
    """
    Collect all protocol files in the specified directory.
    """
    directory_path = Path(directory)
    if not directory_path.exists():
        raise FileNotFoundError(f"Directory '{directory}' does not exist")
    if not directory_path.is_dir():
        raise NotADirectoryError(f"'{directory}' is not a directory")

    json_files = [
        str(f)
        for f in sorted(os.listdir(directory_path))
        if f.endswith(".json") or f.endswith(".jsonc")
    ]
    json_files = [os.path.join(directory_path, f) for f in json_files]
    return json_files


# Define a function to write data to a CSV file
def write_csv(rows: List[Dict[str, str]], output_file: str) -> None:
    """
    Write the extracted data to a CSV file.
    """
    if not rows:
        print("No data to write to CSV")
        return

    fieldnames = ["name", "ctype", "csubtype", "contract", "address", "all_categories"]
    rows = sorted(
        rows, key=lambda x: (x["ctype"], x["csubtype"], x["name"], x["contract"])
    )

    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Successfully wrote {len(rows)} rows to {output_file}")


def write_json(protocols: Dict[str, Any], output_file: str) -> None:
    """
    Write the parsed protocol documents keyed by filename to a JSON file.
    """
    if not protocols:
        print("No data to write to JSON")
        return

    ordered = {k: protocols[k] for k in sorted(protocols)}
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(ordered, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Successfully wrote {len(ordered)} protocols to {output_file}")


# Define a function to collect protocol files in a given directory and then parse the JSON
# protocol files, and write data to a CSV file
def main():
    """Main function to parse arguments and process files."""
    parser = argparse.ArgumentParser(
        description="Convert protocol files to a CSV for DB upload"
    )
    parser.add_argument(
        "-n",
        "--network",
        default="mainnet",
        choices=["testnet", "mainnet"],
        help="Directory containing protocol files to process",
    )
    parser.add_argument(
        "-o",
        "--out",
        default="./protocols.csv",
        help="Output CSV file name (default: output.csv)",
    )

    args = parser.parse_args()

    network = args.network
    if network == "testnet":
        csv_name = "protocols-testnet.csv"
        json_name = "protocols-testnet.json"
    elif network == "mainnet":
        csv_name = "protocols-mainnet.csv"
        json_name = "protocols-mainnet.json"
    else:
        print(f"Invalid network: {network}")
        return

    csv_out = os.path.expanduser(csv_name)
    json_out = os.path.expanduser(json_name)

    protocol_files = collect_protocol_files(network)
    print(f"Found {len(protocol_files)} protocol files")

    # Process all JSON files
    all_rows = []
    protocols: Dict[str, Any] = {}
    for file in protocol_files:
        print(f"Processing {file}...")
        try:
            rows, data = parse_protocol_file(file)
            all_rows.extend(rows)
            if data:
                key = Path(file).stem
                protocols[key] = data
        except (FileNotFoundError, NotADirectoryError) as e:
            print(f"Error: {e}")
            return 1
        except Exception as e:
            print(f"Unexpected error: {e}")
            return 1

    # Write CSV and JSON
    write_csv(all_rows, csv_out)
    write_json(protocols, json_out)


if __name__ == "__main__":
    main()
