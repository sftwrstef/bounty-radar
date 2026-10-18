#!/usr/bin/env python3
"""Read-only exact-asset Ethereum EIP-1967 implementation screen.

Usage: python3 immunefi_eth_high_bounty_eip1967_screen_20261010.py CATALOG_JSON OUTPUT_JSON
Only archived eth_getStorageAt, eth_getBlockByNumber, and eth_getLogs are called.
"""

import hashlib
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

RPC = "https://eth.drpc.org"
SLOT = "0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc"
UPGRADED = "0xbc7cd75a20ee27fd9adebab32041f755214dbc6bffa90cc0225b39da2e5c2d3b"
BEFORE_OCT8 = 26143955  # 2026-10-07 23:59:59 UTC
LAST_PRIOR_UPGRADE_SCREEN = 26164624
END_FINALIZED = 26164957  # 2026-10-10 22:14:47 UTC


def rpc(payload):
    request = urllib.request.Request(
        RPC, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "User-Agent": "curl/8.7.1"},
    )
    for attempt in range(5):
        try:
            with urllib.request.urlopen(request, timeout=40) as response:
                return json.load(response)
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError):
            if attempt == 4:
                raise
            time.sleep(0.5 * 2**attempt)


def one(method, params):
    response = rpc({"jsonrpc": "2.0", "id": 1, "method": method, "params": params})
    if "error" in response:
        raise RuntimeError(response["error"])
    return response["result"]


def storage_batch(addresses, block, cache, cache_path):
    words = cache.setdefault(str(block), {})
    missing = [addr for addr in addresses if addr not in words]
    for offset in range(0, len(missing), 3):
        # dRPC's public tier rejects JSON-RPC batches larger than three.
        keys = missing[offset:offset + 3]
        requests = [
            {"jsonrpc": "2.0", "id": i, "method": "eth_getStorageAt",
             "params": [addr, SLOT, hex(block)]}
            for i, addr in enumerate(keys)
        ]
        response = rpc(requests)
        if not isinstance(response, list) or len(response) != len(keys):
            raise RuntimeError(f"batch {offset} returned incomplete response")
        by_id = {item["id"]: item for item in response}
        if set(by_id) != set(range(len(keys))):
            raise RuntimeError(f"batch {offset} returned mismatched response IDs")
        for i, addr in enumerate(keys):
            item = by_id[i]
            if "error" in item or not isinstance(item.get("result"), str):
                raise RuntimeError(f"storage error for {addr} block {block}: {item.get('error')}")
            words[addr] = item["result"].lower()
        cache_path.write_text(json.dumps(cache))
        time.sleep(0.1)
    return words


def main():
    catalog_path, output_path = map(Path, sys.argv[1:3])
    catalog_bytes = catalog_path.read_bytes()
    catalog = json.loads(catalog_bytes)
    assets = {}
    programs = set()
    for program in catalog:
        if (program["isPaused"] or program["inviteOnly"] or program["endDate"]
                or program["maxBounty"] < 1_000_000):
            continue
        for asset in program["assets"]:
            if asset["type"] != "smart_contract":
                continue
            parsed = urllib.parse.urlparse(asset.get("url") or "")
            if parsed.hostname not in ("etherscan.io", "www.etherscan.io", "eth.blockscout.com"):
                continue
            match = re.search(r"/address/(0x[0-9a-fA-F]{40})(?:/|$)", parsed.path)
            if match:
                key = match[1].lower()
                assets.setdefault(key, []).append({
                    "program": program["slug"], "max_bounty": program["maxBounty"],
                    "asset_url": asset["url"], "description": asset.get("description"),
                })
                programs.add(program["slug"])
    addresses = sorted(assets)
    cache_path = Path("/tmp/vesper-immunefi-eth-high-bounty-eip1967-20261010-cache.json")
    cache = json.loads(cache_path.read_text()) if cache_path.exists() else {}
    start = one("eth_getBlockByNumber", [hex(BEFORE_OCT8), False])
    end = one("eth_getBlockByNumber", [hex(END_FINALIZED), False])
    before = storage_batch(addresses, BEFORE_OCT8, cache, cache_path)
    after = storage_batch(addresses, END_FINALIZED, cache, cache_path)
    changes = [
        {"address": addr, "before": before[addr], "after": after[addr],
         "assets": assets[addr]}
        for addr in addresses if before[addr] != after[addr]
    ]
    tail = []
    for lo in range(LAST_PRIOR_UPGRADE_SCREEN + 1, END_FINALIZED + 1, 100):
        hi = min(lo + 99, END_FINALIZED)
        logs = one("eth_getLogs", [{"fromBlock": hex(lo), "toBlock": hex(hi),
                                    "topics": [UPGRADED]}])
        tail.append({"from": lo, "to": hi, "log_count": len(logs),
                     "exact_matches": [
                         {"address": log["address"],
                          "block": int(log["blockNumber"], 16),
                          "tx_hash": log["transactionHash"],
                          "assets": assets[log["address"].lower()]}
                         for log in logs if log["address"].lower() in assets
                     ]})
    receipt = {
        "observed_at_utc": datetime.now(timezone.utc).isoformat(),
        "rpc": RPC, "catalog_sha256": hashlib.sha256(catalog_bytes).hexdigest(),
        "catalog_program_count": len(catalog),
        "filter": "active non-invite programs with maxBounty >= 1000000; exact Etherscan or eth.blockscout.com smart-contract address",
        "selected_program_count": len(programs),
        "selected_asset_rows": sum(map(len, assets.values())),
        "selected_unique_addresses": len(addresses),
        "slot": SLOT,
        "start_block": {"number": BEFORE_OCT8, "hash": start["hash"],
                        "timestamp": int(start["timestamp"], 16)},
        "end_block": {"number": END_FINALIZED, "hash": end["hash"],
                      "timestamp": int(end["timestamp"], 16)},
        "implementation_slot_changes": changes,
        "nonzero_implementation_slots_before": sum(int(word, 16) != 0 for word in before.values()),
        "nonzero_implementation_slots_after": sum(int(word, 16) != 0 for word in after.values()),
        "tail_upgraded_event_windows": tail,
    }
    output_path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({
        "output": str(output_path), "programs": len(programs),
        "asset_rows": receipt["selected_asset_rows"], "addresses": len(addresses),
        "implementation_changes": len(changes),
        "tail_event_exact_matches": sum(len(x["exact_matches"]) for x in tail),
    }))


if __name__ == "__main__":
    main()
