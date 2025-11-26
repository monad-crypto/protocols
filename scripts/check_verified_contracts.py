"""
Verifies that protocol addresses are validated contracts using the BlockVision API.

This script processes JSON/JSONC protocol files and checks if the addresses they contain
are verified smart contracts on the Monad blockchain.

Usage:
    python check_verified_contracts.py                    # Verify all protocols
    python check_verified_contracts.py file1.json         # Verify specific file
    python check_verified_contracts.py --verbose          # Show detailed results
"""

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import glob
import json
from jsoncomment import JsonComment
import os
from pathlib import Path
import requests
import sys
import time
from typing import Dict, List, Tuple

BLOCKVISION_API_BASE_URL = "https://api.blockvision.org/v2/monad/contract/source/code"
REQUEST_DELAY = 0.2  # Delay between API requests (seconds)
DEFAULT_WORKERS = 5  # Default number of parallel workers

JSONC_PARSER = JsonComment(json)


def parse_jsonc(file_path: str) -> dict:
    """
    Parse a JSON or JSONC file with comment support.

    Args:
        file_path: Path to the JSON/JSONC file

    Returns:
        Parsed JSON data as a dictionary
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        return JSONC_PARSER.loads(content)


def get_all_protocol_files() -> List[str]:
    """
    Find all protocol files in the mainnet directory.

    Returns:
        Sorted list of file paths to protocol JSON/JSONC files
    """
    files = []
    base_dir = Path(__file__).parent.parent

    for folder in ["mainnet"]:
        folder_path = base_dir / folder
        if folder_path.exists():
            files.extend(glob.glob(str(folder_path / "*.json")))
            files.extend(glob.glob(str(folder_path / "*.jsonc")))

    return sorted(files)


def verify_contract_on_blockvision(address: str, api_key: str) -> Tuple[bool, str]:
    """
    Verify if an address is a validated contract using BlockVision API.

    Args:
        address: Smart contract address to verify
        api_key: BlockVision API authentication key

    Returns:
        Tuple of (is_valid, status_message):
            - is_valid: True if contract is verified, False otherwise
            - status_message: Human-readable status description
    """
    headers = {"accept": "application/json", "x-api-key": api_key}
    params = {"address": address}

    try:
        response = requests.get(
            BLOCKVISION_API_BASE_URL, headers=headers, params=params, timeout=10
        )

        # Handle HTTP response codes
        if response.status_code == 401:
            return False, "Authentication failed"
        elif response.status_code == 429:
            return False, "Rate limit exceeded"
        elif response.status_code != 200:
            return False, f"HTTP {response.status_code}"

        data = response.json()
        if not isinstance(data, dict):
            return False, "Invalid response format"

        code = data.get("code")
        result = data.get("result")

        if code == 0:
            if result is not None:
                return True, "Verified"
            else:
                return False, "Not verified"
        else:
            return False, f"API error (code: {code})"
    except requests.exceptions.Timeout:
        return False, "Request timeout"
    except requests.exceptions.RequestException as e:
        return False, f"Request failed: {str(e)}"
    except json.JSONDecodeError:
        return False, "Invalid JSON response"


def process_file(file_path: str, blockvision_api_key: str) -> Dict:
    """
    Process a single protocol file and verify all its contract addresses.

    Args:
        file_path: Path to the protocol JSON/JSONC file
        blockvision_api_key: BlockVision API key for verification

    Returns:
        Dictionary containing verification results with structure:
            - file: File path
            - protocol: Protocol name
            - status: "success", "skipped", or "error"
            - all_valid: Whether all addresses are verified (if applicable)
            - results: Dict of address verification results
            - message: Error message (if applicable)
    """
    try:
        data = parse_jsonc(file_path)
        protocol_name = data.get("name", Path(file_path).stem)
        addresses = data.get("addresses", {})

        if not addresses:
            return {
                "file": file_path,
                "protocol": protocol_name,
                "status": "skipped",
                "message": "No addresses found",
                "results": {},
            }

        results = {}
        for label, address in addresses.items():
            is_valid, message = verify_contract_on_blockvision(
                address, blockvision_api_key
            )
            results[label] = {"address": address, "valid": is_valid, "message": message}
            time.sleep(REQUEST_DELAY)

        all_valid = all(r["valid"] for r in results.values())

        return {
            "file": file_path,
            "protocol": protocol_name,
            "status": "success",
            "all_valid": all_valid,
            "results": results,
        }
    except json.JSONDecodeError as e:
        return {
            "file": file_path,
            "status": "error",
            "message": f"JSON parsing error: {str(e)}",
            "results": {},
        }
    except Exception as e:
        return {
            "file": file_path,
            "status": "error",
            "message": f"Error: {str(e)}",
            "results": {},
        }


def print_results(results: List[Dict], verbose: bool = False):
    """
    Print formatted verification results to console.

    Args:
        results: List of verification result dictionaries
        verbose: If True, show all addresses including valid ones
    """
    total_files = len(results)
    total_addresses = sum(len(r.get("results", {})) for r in results)
    valid_addresses = sum(
        sum(1 for addr in r.get("results", {}).values() if addr.get("valid", False))
        for r in results
    )
    invalid_addresses = total_addresses - valid_addresses

    print("\n" + "=" * 80)
    print("CONTRACT VERIFICATION RESULTS".center(80))
    print("=" * 80)

    for result in results:
        file_name = Path(result["file"]).name
        protocol = result.get("protocol", "Unknown")

        if result["status"] == "error":
            print(f"\n✗ {protocol} ({file_name})")
            print(f"  └─ Error: {result.get('message', 'Unknown error')}")
            continue

        if result["status"] == "skipped":
            print(f"\n⊘ {protocol} ({file_name})")
            print(f"  └─ {result.get('message', 'Skipped')}")
            continue

        address_results = result.get("results", {})
        all_valid = result.get("all_valid", False)

        if all_valid:
            print(f"\n✓ {protocol} ({file_name})")
            if verbose:
                for label, addr_info in address_results.items():
                    print(f"  └─ ✓ {label}: {addr_info['address']}")
        else:
            print(f"\n✗ {protocol} ({file_name})")
            for label, addr_info in address_results.items():
                symbol = "✓" if addr_info["valid"] else "✗"
                status = addr_info["message"]
                print(f"  └─ {symbol} {label}: {addr_info['address']} [{status}]")

    print("\n" + "=" * 80)
    print("SUMMARY".center(80))
    print("=" * 80)
    print(f"  Files Processed:     {total_files}")
    print(f"  Addresses Checked:   {total_addresses}")
    print(f"  ✓ Verified:          {valid_addresses}")
    print(f"  ✗ Not Verified:      {invalid_addresses}")

    if invalid_addresses == 0 and total_addresses > 0:
        print("\n  All contracts verified successfully!")

    print("=" * 80 + "\n")


def main():
    """Main entry point for the contract verification tool."""

    parser = argparse.ArgumentParser(
        description="Verify that protocol addresses are validated smart contracts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "files",
        nargs="*",
        help="specific JSON/JSONC files to verify (default: all protocols)",
    )
    parser.add_argument(
        "--blockvision-api-key",
        default=None,
        help="BlockVision API key (default: BLOCKVISION_API_KEY environment variable)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="show all addresses including verified ones",
    )
    parser.add_argument(
        "--parallel",
        type=int,
        default=DEFAULT_WORKERS,
        help=f"number of parallel workers (default: {DEFAULT_WORKERS})",
    )

    args = parser.parse_args()

    blockvision_api_key = args.blockvision_api_key or os.environ.get(
        "BLOCKVISION_API_KEY"
    )
    if not blockvision_api_key:
        print("✗ Error: BlockVision API key required")
        print(
            "  Set the BLOCKVISION_API_KEY environment variable or use --blockvision-api-key"
        )
        sys.exit(1)

    if args.files:
        files = args.files
        for file_path in files:
            if not os.path.exists(file_path):
                print(f"✗ Error: File not found: {file_path}")
                sys.exit(1)
    else:
        files = get_all_protocol_files()
        if not files:
            print("✗ Error: No protocol files found in the mainnet directory")
            sys.exit(1)

    print(f"\nVerifying {len(files)} protocol file(s)...\n")

    # Process files in parallel
    results = []
    with ThreadPoolExecutor(max_workers=args.parallel) as executor:
        future_to_file = {
            executor.submit(process_file, file_path, blockvision_api_key): file_path
            for file_path in files
        }

        for future in as_completed(future_to_file):
            result = future.result()
            results.append(result)

            protocol = result.get("protocol", Path(result["file"]).name)
            if result["status"] == "success":
                addr_count = len(result.get("results", {}))
                print(f"  ✓ {protocol} ({addr_count} addresses)")
            else:
                print(f"  ✗ {protocol} - {result.get('message', 'Error')}")

    results.sort(key=lambda x: x["file"])

    print_results(results, verbose=args.verbose)


if __name__ == "__main__":
    main()
