#!/usr/bin/env python3
"""Read-only, exact-ID Solana ProgramData screen for the Immunefi catalog.

Usage: python3 solana_programdata_screen_20261010.py CATALOG_JSON CHAINLINK_ANCHOR_TOML OUTPUT_JSON
The two inputs are official Immunefi catalog and first-party Chainlink Anchor.toml
snapshots. The only network calls here are finalized getMultipleAccounts reads.
"""

import base64
import hashlib
import json
import re
import sys
import tomllib
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

RPC = "https://api.mainnet-beta.solana.com"
LOADER = "BPFLoaderUpgradeab1e11111111111111111111111"
ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def b58(data: bytes) -> str:
    n = int.from_bytes(data, "big")
    chars = ""
    while n:
        n, rem = divmod(n, 58)
        chars = ALPHABET[rem] + chars
    return "1" * (len(data) - len(data.lstrip(b"\0"))) + chars


def read_accounts(keys: list[str]) -> dict:
    request = urllib.request.Request(
        RPC,
        data=json.dumps({
            "jsonrpc": "2.0", "id": 1, "method": "getMultipleAccounts",
            "params": [keys, {
                "encoding": "base64", "commitment": "finalized",
                "dataSlice": {"offset": 0, "length": 45},
            }],
        }).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.load(response)
    if "error" in payload:
        raise RuntimeError(payload["error"])
    return payload["result"]


def add(rows: dict, group: str, name: str, key: str, source: str) -> None:
    row = rows.setdefault(key, {"program_id": key, "groups": [], "sources": []})
    row["groups"].append(f"{group}: {name}")
    row["sources"].append(source)


def main() -> None:
    catalog_path, anchor_path, output_path = map(Path, sys.argv[1:4])
    catalog_bytes = catalog_path.read_bytes()
    anchor_bytes = anchor_path.read_bytes()
    catalog = json.loads(catalog_bytes)
    rows: dict[str, dict] = {}

    for program in catalog:
        if program["isPaused"] or program["endDate"]:
            continue
        for asset in program["assets"]:
            if asset["type"] != "smart_contract":
                continue
            url = asset.get("url") or ""
            description = asset.get("description") or ""
            match = re.search(
                r"(?:solscan\.io/(?:account|token)/|explorer\.solana\.com/address/)"
                r"([1-9A-HJ-NP-Za-km-z]{32,44})", url,
            )
            if match and "devnet" not in url:
                add(rows, program["slug"], description or "exact-address asset", match[1], url)
            if program["slug"] == "lombard-finance":
                match = re.search(r"Solana program ([1-9A-HJ-NP-Za-km-z]{32,44})", description)
                if match:
                    add(rows, program["slug"], description.split(" (")[0], match[1], url)

    # Source-scoped identities from current first-party files and existing target pins.
    anchor = tomllib.loads(anchor_bytes.decode())["programs"]["localnet"]
    for name in (
        "ccip_offramp", "ccip_router", "burnmint_token_pool",
        "lockrelease_token_pool", "fee_quoter", "rmn_remote",
        "mcm", "timelock", "cctp_token_pool",
    ):
        add(rows, "chainlink", name, anchor[name],
            "https://github.com/smartcontractkit/chainlink-ccip/blob/main/chains/solana/contracts/Anchor.toml")
    for group, name, key, source in (
        ("pythnetwork", "Core receiver", "rec5EKMGg6MxZYaMdyBfgwp4d5rB9T1VQH5pJv5LtFJ",
         "https://docs.pyth.network/price-feeds/core/contract-addresses/solana"),
        ("pythnetwork", "Pro receiver", "rec2HHDDnjLfj4kE7VyEtFA1HPGQLK33259532cRyHp",
         "https://github.com/pyth-network/pyth-crosschain/tree/main/target_chains/solana"),
        ("1inch-SmartContracts", "fusion_swap", "HNarfxC3kYMMhFkxUFeYb8wHVdPzY5t9pupqW5fL2meM",
         "https://github.com/1inch/solana-fusion/blob/84ecfdd18266188f5d77fb0cd4c00d97abb70a34/Anchor.toml"),
        ("1inch-SmartContracts", "whitelist", "5jzZhrzqkbdwp5d3J1XbmaXMRnqeXimM1mDMoGHyvR7S",
         "https://github.com/1inch/solana-fusion/blob/84ecfdd18266188f5d77fb0cd4c00d97abb70a34/Anchor.toml"),
        ("1inch-SmartContracts", "cross-chain escrow", "2g4JDRMD7G3dK1PHmCnDAycKzd6e5sdhxqGBbs264zwz",
         "https://github.com/1inch/solana-crosschain-protocol"),
        ("wormhole", "Accountant", "wormDTUJ6AWPNvk59vGQbDvGJmqbDTdgWgAqcLBCgUb",
         "https://github.com/wormhole-foundation/wormhole/tree/main/solana"),
        ("marinade", "liquid staking", "MarBmsSgKXdrN1egZf5sqe1TMai9K1rChYNDJgjq7aD",
         "https://github.com/marinade-finance/liquid-staking-program"),
    ):
        add(rows, group, name, key, source)

    keys = list(rows)
    programs = read_accounts(keys)
    programdata_keys = []
    for key, account in zip(keys, programs["value"]):
        row = rows[key]
        if account is None:
            row["account_status"] = "missing"
            continue
        data = base64.b64decode(account["data"][0])
        row.update({
            "account_owner": account["owner"],
            "executable": account["executable"],
            "account_space": account["space"],
            "loader_variant": int.from_bytes(data[:4], "little") if len(data) >= 4 else None,
        })
        if account["owner"] == LOADER and account["executable"] and data[:4] == (2).to_bytes(4, "little"):
            row["programdata"] = b58(data[4:36])
            programdata_keys.append(row["programdata"])
        else:
            row["account_status"] = "not_upgradeable_program"

    deployment = read_accounts(programdata_keys)
    by_pd = {pd: account for pd, account in zip(programdata_keys, deployment["value"])}
    for row in rows.values():
        if "programdata" not in row:
            continue
        account = by_pd[row["programdata"]]
        if account is None:
            row["programdata_status"] = "missing"
            continue
        data = base64.b64decode(account["data"][0])
        row.update({
            "programdata_owner": account["owner"],
            "programdata_variant": int.from_bytes(data[:4], "little"),
            "last_deploy_slot": int.from_bytes(data[4:12], "little"),
            "upgrade_authority_option": data[12],
        })

    receipt = {
        "observed_at_utc": datetime.now(timezone.utc).isoformat(),
        "rpc": RPC,
        "commitment": "finalized",
        "program_read_context_slot": programs["context"]["slot"],
        "programdata_read_context_slot": deployment["context"]["slot"],
        "catalog_sha256": hashlib.sha256(catalog_bytes).hexdigest(),
        "catalog_program_count": len(catalog),
        "chainlink_anchor_sha256": hashlib.sha256(anchor_bytes).hexdigest(),
        "rows": sorted(rows.values(), key=lambda row: (row["groups"][0], row["program_id"])),
    }
    output_path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({
        "output": str(output_path),
        "programs": len(rows),
        "upgradeable_programs": len(programdata_keys),
        "latest_deploy_slot": max(row.get("last_deploy_slot", 0) for row in rows.values()),
        "context_slot": deployment["context"]["slot"],
    }))


if __name__ == "__main__":
    main()
