#!/usr/bin/env python3
"""
validate_protocol.py

Validate protocol metadata JSON files in the `testnet/` folder.

Checks for required fields: `name`, `description`, `links`, and `categories`.
"""
import argparse
import json5
import os
import sys
from urllib.request import Request, urlopen
from collections import defaultdict

REQUIRED_FIELDS = ["name", "description", "links", "categories"]
CATEGORIES = json5.load(open("categories.json", "r", encoding="utf-8"))
CATEGORIES = CATEGORIES["categories"]

def is_valid_address(address: str) -> bool:
    """Check if an address is a valid Ethereum address."""
    return address.startswith("0x") and len(address) == 42 and \
        all(c in "0123456789ABCDEFabcdef" for c in address[2:])

def is_valid_file(filepath: str) -> bool:
    """Validate one JSON metadata file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json5.load(f)
    except Exception as e:
        print(f"❌ Error reading {filepath}: {e}")
        return False

    filename = os.path.split(filepath)[-1]

    # all required fields must be present
    missing = [field for field in REQUIRED_FIELDS if field not in data]
    if missing:
        print(f"❌ {filename} missing: {', '.join(missing)}")
        return False

    # categories must be a subset of the allowed categories
    categories = data.get("categories", [])
    if not categories:
        print(f"❌ {filename} missing: 'categories'")
        return False

    invalid_categories = [category for category in categories if category not in CATEGORIES]
    if invalid_categories:
        print(f"❌ {filename} contains invalid categories: {', '.join(invalid_categories)}")
        return False

    # empty address map is a warning
    address_map = data.get("addresses", {})
    if not address_map:
        print(f"⚠️ {filename} has empty address map")

    # but any addresses supplied must be valid
    all_valid = True
    for contract_name, address in address_map.items():
        if not is_valid_address(address):
            print(f"❌ {filename} contains invalid address: {contract_name} -> {address}")
            all_valid = False
    if not all_valid:
        return False

    return True

def check_duplicated_address_labels(base_dir: str, json_files: list[str]) -> bool:
    address_labels = defaultdict(lambda: [])
    for json_file in json_files:
        with open(os.path.join(base_dir, json_file), "r", encoding="utf-8") as f:
            data = json5.load(f)
        for address_label, address in data['addresses'].items():
            address_labels[address.lower()].append((json_file, address_label))
    
    multiple_address_labels = [(address, labels) for address, labels in address_labels.items() if len(labels) > 1]
    has_duplicated_address_labels = False
    for address, labels in multiple_address_labels:
        distinct_labels = {address_label for json_file, address_label in labels}
        if len(distinct_labels) >= 2:
            labels_str = "\n" + "\n".join([f"{json_file}: {x}" for json_file, x in labels])
            print(f'❌ Address {address} has multiple distinct labels:{labels_str}')
            has_duplicated_address_labels = True
    
    return has_duplicated_address_labels

def check_included_canonical_contracts(base_dir: str, json_files: list[str]) -> bool:
    canonical_contract_data = json5.load(open(os.path.join(base_dir, "CANONICAL.jsonc"), "r", encoding="utf-8"))
    canonical_contract_addresses = {x.lower() for x in canonical_contract_data['addresses'].values()}
    has_included_canonical_contracts = False
    for f in os.listdir(base_dir):
        if f in {'CANONICAL.jsonc', 'README.md'}:
            continue

        with open(os.path.join(base_dir, f), 'r') as protocol_file:
            protocol_data = json5.load(protocol_file)
            for label, x in protocol_data['addresses'].items():
                if x.lower() in canonical_contract_addresses:
                    print(f'❌ {f} includes a canonical contract "{label}": "{x}" - please remove this entry.')
                    has_included_canonical_contracts = True

    return has_included_canonical_contracts

def check_invalid_links(base_dir: str, json_files: list[str]) -> bool:
    # 20251117: for now this should be run manually as there may be legitimate reasons for some invalid links
    has_invalid_links = False
    for f in json_files:
        with open(os.path.join(base_dir, f), 'r') as protocol_file:
            protocol_data = json5.load(protocol_file)
            for link_label, link in protocol_data['links'].items():
                if link == "":
                    continue
                if not link.startswith('https://') and not link.startswith('http://'):
                    print(f'⚠️ {f} contains an invalid link: "{link}"')
                    has_invalid_links = True
                    continue
                
                try:
                    req = Request(link, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36'})
                    status_code = urlopen(req).status
                except Exception as e:
                    print(f'⚠️ {f} contains a bad link. Attempt to access "{link}" returned an error: {e}')
                    has_invalid_links = True

                if status_code != 200:
                    print(f'⚠️ {f} contains a bad link. Attempt to access "{link}" returned: {status_code}')
                    has_invalid_links = True
            
    return has_invalid_links

def main():
    parser = argparse.ArgumentParser('')
    parser.add_argument('-n', '--network', dest='network', choices=['testnet', 'mainnet'],
        default='mainnet')
    parser.add_argument('-p', '--protocol', dest='protocol', required=False)
    parser.add_argument('-l', '--link', dest='link', action='store_true')
    args, unknown_args = parser.parse_known_args()

    network = args.network
    base_dir = os.path.join(os.path.dirname(__file__), "..", network)
    if not os.path.isdir(base_dir):
        print(f"❌ {network} directory not found.")
        sys.exit(1)

    # check one protocol
    if args.protocol:
        json_files = [f for f in sorted(os.listdir(base_dir)) if f.endswith(".json") or f.endswith(".jsonc")]
        json_files = [f for f in json_files if os.path.splitext(f)[0].lower() == args.protocol.lower()]

        if not json_files:
            print(f"❌ {args.protocol} not found.")
            sys.exit(1)
        filepath = os.path.join(base_dir, json_files[0])
        is_valid = is_valid_file(filepath)
        if is_valid:
            print(f"✅ {filepath} is valid.")
        else:
            print(f"❌ {filepath} is invalid.")

    # check all protocols
    else:
        invalid = []
        json_files = [f for f in sorted(os.listdir(base_dir)) if f.endswith(".json") or f.endswith(".jsonc")]
        if not json_files:
            print("⚠️ No JSON files found in testnet/")
            sys.exit(0)

        print(f"Validating {len(json_files)} files...\n")
        for filename in json_files:
            filepath = os.path.join(base_dir, filename)
            is_valid = is_valid_file(filepath)
            if is_valid:
                print(f"✅ {filename} is valid.")
            else:
                print(f"❌ {filename} is invalid.")
                invalid.append(filename)

        if len(invalid) > 0:
            raise Exception("invalid jsons: " + ",".join(invalid))

    has_included_canonical_contracts = check_included_canonical_contracts(base_dir, json_files)
    has_duplicated_address_labels = check_duplicated_address_labels(base_dir, json_files)
    if args.link:
        check_invalid_links(base_dir, json_files)

    if has_included_canonical_contracts:
        raise Exception("Found included canonical contracts in repo")

    if has_duplicated_address_labels:
        raise Exception("Found duplicated address labels in repo")

if __name__ == "__main__":
    main()
