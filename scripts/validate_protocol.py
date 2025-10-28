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
# --- NEW IMPORTS ---
import requests
from requests.exceptions import RequestException
# -------------------

REQUIRED_FIELDS = ["name", "description", "links", "categories"]
CATEGORIES = json5.load(open("categories.json", "r", encoding="utf-8"))
CATEGORIES = CATEGORIES["categories"]

def is_valid_address(address: str) -> bool:
    """Check if an address is a valid Ethereum address."""
    return address.startswith("0x") and len(address) == 42 and \
        all(c in "0123456789ABCDEFabcdef" for c in address[2:])

# --- NEW FUNCTION FOR LINK CHECKING ---
def check_url(url, protocol_name):
    """Checks if a URL is live. Returns an error message if not."""
    if not url:
        return None
    try:
        # Use a HEAD request to be faster and use less bandwidth
        response = requests.head(url, allow_redirects=True, timeout=10)
        
        # Check for client (4xx) or server (5xx) errors
        if 400 <= response.status_code < 600:
            return f"  - {protocol_name}: Link '{url}' returned status {response.status_code}"
    except RequestException as e:
        # Catch timeouts, connection errors, etc.
        return f"  - {protocol_name}: Link '{url}' failed to connect (e.g., timeout or DNS error)"
    return None
# --------------------------------------

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

def main():
    parser = argparse.ArgumentParser('')
    parser.add_argument('-n', '--network', dest='network', choices=['testnet', 'mainnet'],
        default='mainnet')
    parser.add_argument('-p', '--protocol', dest='protocol', required=False)
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
        
        # --- NEW: Check links for a single protocol ---
        errors = []
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json5.load(f)
            protocol_name = data.get("name", filepath)
            if "links" in data and isinstance(data["links"], dict):
                for link_name, link_url in data["links"].items():
                    if isinstance(link_url, str):
                        error_msg = check_url(link_url, protocol_name)
                        if error_msg:
                            errors.append(f"[Link Check] {error_msg}")
                    else:
                        errors.append(f"[Schema Error] - {protocol_name}: Link '{link_name}' is not a valid URL string.")
        except Exception:
            # If there's a load error, it was already reported by is_valid_file
            pass 
        
        if errors:
            is_valid = False
            print("\nValidation failed with the following errors:")
            print("\n".join(errors))
        # ---------------------------------------------
        
        if is_valid:
            print(f"✅ {filepath} is valid.")
        else:
            print(f"❌ {filepath} is invalid.")

    # check all protocols
    else:
        json_files = [f for f in sorted(os.listdir(base_dir)) if f.endswith(".json") or f.endswith(".jsonc")]
        if not json_files:
            print("⚠️ No JSON files found in testnet/")
            sys.exit(0)

        print(f"Validating {len(json_files)} files...\n")
        
        # List to collect all link errors from all files
        all_link_errors = [] 
        all_files_valid = True

        for filename in json_files:
            filepath = os.path.join(base_dir, filename)
            
            # Run existing structural and address checks (prints structural errors directly)
            structural_valid = is_valid_file(filepath)
            
            # --- NEW: Check links for all protocols ---
            file_link_errors = []
            try:
                # Need to load data again to check links, as is_valid_file only returns a bool
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json5.load(f)
                protocol_name = data.get("name", filename)
                if "links" in data and isinstance(data["links"], dict):
                    for link_name, link_url in data["links"].items():
                        if isinstance(link_url, str):
                            error_msg = check_url(link_url, protocol_name)
                            if error_msg:
                                file_link_errors.append(f"[Link Check] {error_msg}")
                        else:
                            file_link_errors.append(f"[Schema Error] - {protocol_name}: Link '{link_name}' is not a valid URL string.")
            except Exception:
                # If there's an error here, it was already caught in is_valid_file, just skip link check
                pass 
            
            if file_link_errors:
                all_link_errors.extend(file_link_errors)
            
            # Determine overall validity
            is_valid = structural_valid and not file_link_errors

            if is_valid:
                print(f"✅ {filename} is valid.")
            else:
                all_files_valid = False
                print(f"❌ {filename} is invalid (see summary below for link errors).")
        
        # --- NEW: Final Error Report ---
        if all_link_errors:
            print("\nValidation failed with the following errors:")
            print("\n".join(all_link_errors))
            sys.exit(1)
            
        if not all_files_valid:
            # Exits if any structural or link check failed
            sys.exit(1)
        # --------------------------------

        print("All protocols are valid")
        sys.exit(0)

if __name__ == "__main__":
    main()
