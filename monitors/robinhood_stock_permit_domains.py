#!/usr/bin/env python3
"""Read-only Robinhood Stock EIP-712 domain reuse monitor.

The monitor reconstructs the canonical Stock fleet from Factory events, stores
every proxy-local permit domain separator, and checks confirmation-buffered
near-head blocks for:

* a separator returning after an intervening distinct separator;
* metadata or deployment changes;
* Registry/Factory upgrades and role-topology changes;
* unexpected initializer/EIP-5267 domain-change events; and
* silent drift in the pinned control contracts or implementation pointers.

It never signs or sends a transaction.  ``check`` exits non-zero only when the
monitor itself fails; security alerts are returned as JSON with ``status`` set
to ``alert`` so a scheduler can report them without treating them as crashes.
"""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Sequence


DEFAULT_RPC_URL = "https://rpc.mainnet.chain.robinhood.com"
EXPECTED_CHAIN_ID = 4663
FACTORY = "0x4783c67b63de2b358ac5951a7d41f47a38f3c046"
REGISTRY = "0xe10b6f6b275de231345c20d14ab812db62151b00"
TSLA_PROXY = "0x322f0929c4625ed5bad873c95208d54e1c003b2d"
MULTICALL3 = "0xca11bde05977b3631167028862be2a173976ca11"

SENSITIVE_PRINCIPALS = {
    "default_admin": "0xd6f8378f8e440c65f8382f5f2728c78dfd55b66d",
    "token_deployer": "0x5516b3451d4d6c9f63353fe7bc9537477ecce000",
    "beacon_upgrader": "0xcd8c6182e7c6ca3b5156d6a90a67719d7e2be094",
    "factory_upgrader": "0x697e774d60c1a3769f2ed0b919aacf17be0ae553",
    "metadata_updater": "0xcba16c2b9048af033c5b34e43dd1d47d1358524a",
}

MIN_BASELINE_DEPLOYMENTS = 203
MIN_BASELINE_METADATA_TRANSITIONS = 6
DEFAULT_MAX_CURSOR_GAP = 4_500
PINNED_ANCHORS = {
    "registry_code_sha256": "e42be4f7355845c67bb554c14cd9f23e9d3dcaad79f88dc1cd3e725c7b7597b5",
    "registry_implementation": "0xb35490d6f9163de4f80d88dc75c3516eb64c5ae2",
    "stock_implementation_code_sha256": "0ac99e9cc7a3738645af72f6d9e8fb8242660b63134d8fb0c44ba6fac39deec2",
    "stock_proxy_code_sha256": "399ec4bc5b43db03486ceae11f9a6fc5c126427f8f8e10c90fed0c773f4325c6",
    "factory_proxy_code_sha256": "e88f26fb0397fdcd0e4f0ad283dbbe81d478c28889542a2a73a557da8262210c",
    "factory_beacon": REGISTRY,
    "factory_implementation": "0xee351e53bce6aaf106428358838197c91e36ee0e",
    "factory_implementation_code_sha256": "7abe106afcd525985cec5d5f04d3652503f217c9e2bac23bf303d627ad191a3d",
}

DEPLOYED_TOPIC = "0xd9b0c6a1c0de228715ad0fa09f3259686ee84f8cc675e03ef7e47a9cdafa76d6"
METADATA_TOPIC = "0x0030cda629fbac2efa8c01c1732f1dd9cbec41aae6ceae83906fe6c003b3a03c"
UPGRADED_TOPIC = "0xbc7cd75a20ee27fd9adebab32041f755214dbc6bffa90cc0225b39da2e5c2d3b"
ROLE_GRANTED_TOPIC = "0x2f8788117e7eff1d82e926ec794901d17c78024a50270940304540a733656f0d"
ROLE_REVOKED_TOPIC = "0xf6391f5c32d9c69d2a47ea670b442974b53935d1edc7fd64eb21e047a839171b"
ROLE_ADMIN_CHANGED_TOPIC = "0xbd79b86ffe0ab8e8776151514217cd7cacd52c909f66475c3af44e129f0b00ff"
INITIALIZED_TOPIC = "0xc7f505b2f371ae2175ee4913f4499e1f2633a7b5936321eed1cdaeb6115181d2"
EIP712_DOMAIN_CHANGED_TOPIC = "0x0a6387c9ea3628b88a633bb4f3b151770f70085117a15f9bf3787cda53f13d31"

DOMAIN_SELECTOR = "0x3644e515"
EIP712_DOMAIN_SELECTOR = "0x84b0196e"
IMPLEMENTATION_SELECTOR = "0x5c60da1b"
BEACON_SELECTOR = "0x59659e90"
TOKEN_ADDRESS_SELECTOR = "0x97bb3ce9"
UID_SELECTOR = "0xf514ce36"
ACCESS_CONTROLLED_REGISTRY_SELECTOR = "0x50c09be3"
AGGREGATE3_SELECTOR = "0x82ad56cb"

DOMAIN_TYPEHASH = "0x8b73c3c69bb8fe3d512ecc4cf759cc79239f7b179b0ffacaa9a75d522b39400f"
VERSION_ONE_HASH = "0xc89efdaa54c0f20c7adf612882df0950f5a951637e0307cdcb4c672f298b8bc6"
EIP1967_IMPLEMENTATION_SLOT = "0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc"
EIP1967_BEACON_SLOT = "0xa3f0ad74e5423aebfd80d3ef4346578335a9a72aeaee59ff6cb3582b35133d50"

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STATE_FILE = REPO_ROOT / "data" / "robinhood_stock_permit_domains_watch.json"
DEFAULT_ALERT_LOG = REPO_ROOT / "data" / "robinhood_stock_permit_domain_alerts.jsonl"


class MonitorError(RuntimeError):
    """A monitor or RPC invariant failed."""


class RpcError(MonitorError):
    """A JSON-RPC request failed."""


def is_log_range_error(error: RpcError) -> bool:
    message = str(error).lower()
    return any(
        marker in message
        for marker in (
            "block range",
            "range is too wide",
            "too many results",
            "query returned more than",
            "response size",
            "limit exceeded",
            "-32005",
        )
    )


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_hex(value: str, expected_bytes: int | None = None) -> str:
    if not isinstance(value, str) or not value.startswith("0x"):
        raise MonitorError(f"expected 0x-prefixed hex, got {value!r}")
    raw = value[2:].lower()
    if len(raw) % 2:
        raw = "0" + raw
    try:
        bytes.fromhex(raw)
    except ValueError as exc:
        raise MonitorError(f"invalid hex value {value!r}") from exc
    if expected_bytes is not None and len(raw) != expected_bytes * 2:
        raise MonitorError(f"expected {expected_bytes} bytes, got {len(raw) // 2}")
    return "0x" + raw


def normalize_address(value: str) -> str:
    value = normalize_hex(value)
    raw = value[2:]
    if len(raw) > 40:
        raw = raw[-40:]
    if len(raw) != 40:
        raise MonitorError(f"invalid address length: {value}")
    return "0x" + raw


def hex_int(value: str) -> int:
    return int(normalize_hex(value), 16)


def bytes_from_hex(value: str) -> bytes:
    return bytes.fromhex(normalize_hex(value)[2:])


def abi_word(raw: bytes, index: int) -> bytes:
    start = index * 32
    end = start + 32
    if end > len(raw):
        raise MonitorError(f"ABI word {index} is outside {len(raw)} bytes")
    return raw[start:end]


def abi_dynamic_bytes(raw: bytes, offset_word_index: int) -> bytes:
    offset = int.from_bytes(abi_word(raw, offset_word_index), "big")
    if offset + 32 > len(raw):
        raise MonitorError(f"ABI dynamic offset {offset} is outside {len(raw)} bytes")
    length = int.from_bytes(raw[offset : offset + 32], "big")
    start = offset + 32
    end = start + length
    if end > len(raw):
        raise MonitorError(f"ABI dynamic value length {length} is outside payload")
    return raw[start:end]


def abi_string(raw: bytes, offset_word_index: int) -> str:
    try:
        return abi_dynamic_bytes(raw, offset_word_index).decode("utf-8")
    except UnicodeDecodeError as exc:
        raise MonitorError("domain metadata is not valid UTF-8") from exc


def decode_factory_data(data: str) -> tuple[str, str, str]:
    raw = bytes_from_hex(data)
    address = normalize_address("0x" + abi_word(raw, 0)[12:].hex())
    return address, abi_string(raw, 1), abi_string(raw, 2)


def decode_metadata_data(data: str) -> tuple[str, str]:
    raw = bytes_from_hex(data)
    return abi_string(raw, 0), abi_string(raw, 1)


def decode_address_word(data: str) -> str:
    raw = bytes_from_hex(data)
    if len(raw) < 32:
        raise MonitorError("address return value is shorter than one ABI word")
    return normalize_address("0x" + raw[-20:].hex())


def decode_topic_address(topic: str) -> str:
    raw = bytes_from_hex(topic)
    if len(raw) != 32:
        raise MonitorError("indexed address topic is not 32 bytes")
    return normalize_address("0x" + raw[-20:].hex())


def decode_eip712_domain(data: str) -> dict[str, Any]:
    raw = bytes_from_hex(data)
    if len(raw) < 7 * 32:
        raise MonitorError("eip712Domain return is too short")
    extensions_offset = int.from_bytes(abi_word(raw, 6), "big")
    if extensions_offset + 32 > len(raw):
        raise MonitorError("EIP-712 extensions offset is outside payload")
    extension_count = int.from_bytes(raw[extensions_offset : extensions_offset + 32], "big")
    extensions: list[int] = []
    for index in range(extension_count):
        start = extensions_offset + 32 + index * 32
        if start + 32 > len(raw):
            raise MonitorError("EIP-712 extensions array is truncated")
        extensions.append(int.from_bytes(raw[start : start + 32], "big"))
    return {
        "fields": "0x" + abi_word(raw, 0)[:1].hex(),
        "name": abi_string(raw, 1),
        "version": abi_string(raw, 2),
        "chain_id": int.from_bytes(abi_word(raw, 3), "big"),
        "verifying_contract": normalize_address("0x" + abi_word(raw, 4)[12:].hex()),
        "salt": "0x" + abi_word(raw, 5).hex(),
        "extensions": extensions,
    }


def pad_abi(value: bytes) -> bytes:
    return value + bytes((-len(value)) % 32)


def abi_uint(value: int) -> bytes:
    if value < 0:
        raise MonitorError("ABI uint cannot be negative")
    return value.to_bytes(32, "big")


def encode_aggregate3(calls: Sequence[tuple[str, str]]) -> str:
    """Encode Multicall3 aggregate3((address,bool,bytes)[]) with allowFailure=true."""
    elements: list[bytes] = []
    for target, call_data in calls:
        raw_call = bytes_from_hex(call_data)
        elements.append(
            b"".join(
                [
                    bytes(12) + bytes_from_hex(normalize_address(target)),
                    abi_uint(1),
                    abi_uint(96),
                    abi_uint(len(raw_call)),
                    pad_abi(raw_call),
                ]
            )
        )
    offsets: list[bytes] = []
    cursor = 32 * len(elements)
    for element in elements:
        offsets.append(abi_uint(cursor))
        cursor += len(element)
    encoded_array = abi_uint(len(elements)) + b"".join(offsets) + b"".join(elements)
    return AGGREGATE3_SELECTOR + (abi_uint(32) + encoded_array).hex()


def decode_aggregate3_result(data: str) -> list[tuple[bool, str]]:
    raw = bytes_from_hex(data)
    array_start = int.from_bytes(abi_word(raw, 0), "big")
    if array_start + 32 > len(raw):
        raise MonitorError("Multicall result array offset is outside payload")
    count = int.from_bytes(raw[array_start : array_start + 32], "big")
    offsets_base = array_start + 32
    output: list[tuple[bool, str]] = []
    for index in range(count):
        offset_pos = offsets_base + index * 32
        if offset_pos + 32 > len(raw):
            raise MonitorError("Multicall result offsets are truncated")
        relative = int.from_bytes(raw[offset_pos : offset_pos + 32], "big")
        tuple_start = offsets_base + relative
        if tuple_start + 64 > len(raw):
            raise MonitorError("Multicall result tuple is truncated")
        success = bool(int.from_bytes(raw[tuple_start : tuple_start + 32], "big"))
        bytes_offset = int.from_bytes(raw[tuple_start + 32 : tuple_start + 64], "big")
        bytes_start = tuple_start + bytes_offset
        if bytes_start + 32 > len(raw):
            raise MonitorError("Multicall return-data offset is outside payload")
        length = int.from_bytes(raw[bytes_start : bytes_start + 32], "big")
        value_start = bytes_start + 32
        value_end = value_start + length
        if value_end > len(raw):
            raise MonitorError("Multicall return data is truncated")
        output.append((success, "0x" + raw[value_start:value_end].hex()))
    return output


def log_position(log: dict[str, Any]) -> tuple[int, int, int]:
    return (
        hex_int(log["blockNumber"]),
        hex_int(log.get("transactionIndex", "0x0")),
        hex_int(log.get("logIndex", "0x0")),
    )


def log_evidence(log: dict[str, Any]) -> dict[str, Any]:
    return {
        "block_number": hex_int(log["blockNumber"]),
        "transaction_hash": normalize_hex(log["transactionHash"], 32),
        "log_index": hex_int(log.get("logIndex", "0x0")),
    }


class JsonRpc:
    def __init__(
        self,
        url: str,
        timeout: float = 30.0,
        retries: int = 4,
        batch_size: int = 20,
        min_request_interval: float = 0.1,
    ) -> None:
        self.url = url
        self.timeout = timeout
        self.retries = retries
        self.batch_size = batch_size
        self.min_request_interval = min_request_interval
        self.last_request_at = 0.0

    def _post(self, payload: Any) -> Any:
        encoded = json.dumps(payload, separators=(",", ":")).encode()
        request = urllib.request.Request(
            self.url,
            data=encoded,
            headers={"Content-Type": "application/json", "User-Agent": "vesper-domain-monitor/1"},
            method="POST",
        )
        last_error: Exception | None = None
        for attempt in range(self.retries):
            elapsed = time.monotonic() - self.last_request_at
            if elapsed < self.min_request_interval:
                time.sleep(self.min_request_interval - elapsed)
            self.last_request_at = time.monotonic()
            try:
                with urllib.request.urlopen(request, timeout=self.timeout) as response:
                    return json.loads(response.read())
            except urllib.error.HTTPError as exc:
                try:
                    body = exc.read(256).decode("utf-8", errors="replace").strip()
                except OSError:
                    body = ""
                last_error = RpcError(
                    f"HTTP {exc.code}{f': {body}' if body else ''}"
                )
                retry_after = exc.headers.get("Retry-After") if exc.headers else None
                if attempt + 1 < self.retries:
                    try:
                        delay = max(0.5 * (2**attempt), float(retry_after or 0))
                    except ValueError:
                        delay = 0.5 * (2**attempt)
                    time.sleep(min(delay, 30.0))
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
                last_error = exc
                if attempt + 1 < self.retries:
                    time.sleep(0.5 * (2**attempt))
        raise RpcError(
            f"JSON-RPC transport failed after {self.retries} attempts: {last_error}"
        )

    def call(self, method: str, params: Sequence[Any]) -> Any:
        response = self._post({"jsonrpc": "2.0", "id": 1, "method": method, "params": list(params)})
        if not isinstance(response, dict):
            raise RpcError(f"unexpected JSON-RPC response for {method}")
        if response.get("error"):
            error = response["error"]
            raise RpcError(f"{method} failed: {error.get('code')} {error.get('message')}")
        if "result" not in response:
            raise RpcError(f"{method} response has no result")
        return response["result"]

    def batch(self, calls: Sequence[tuple[str, Sequence[Any]]]) -> list[Any | RpcError]:
        output: list[Any | RpcError] = []
        for base in range(0, len(calls), self.batch_size):
            chunk = calls[base : base + self.batch_size]
            payload = [
                {"jsonrpc": "2.0", "id": index, "method": method, "params": list(params)}
                for index, (method, params) in enumerate(chunk)
            ]
            try:
                response = self._post(payload)
                if not isinstance(response, list):
                    raise RpcError("batch request returned a non-list response")
                by_id = {item.get("id"): item for item in response if isinstance(item, dict)}
                for index, (method, _params) in enumerate(chunk):
                    item = by_id.get(index)
                    if item is None:
                        output.append(RpcError(f"missing batch result for {method}"))
                    elif item.get("error"):
                        error = item["error"]
                        output.append(RpcError(f"{method} failed: {error.get('code')} {error.get('message')}"))
                    else:
                        output.append(item.get("result"))
            except RpcError:
                for method, params in chunk:
                    try:
                        output.append(self.call(method, params))
                    except RpcError as exc:
                        output.append(exc)
        return output

    def block_number(self) -> int:
        return hex_int(self.call("eth_blockNumber", []))

    def chain_id(self) -> int:
        return hex_int(self.call("eth_chainId", []))

    def block_hash(self, number: int) -> str:
        block = self.call("eth_getBlockByNumber", [hex(number), False])
        if not block or not block.get("hash"):
            raise RpcError(f"block {number} is unavailable")
        return normalize_hex(block["hash"], 32)

    def get_logs(
        self,
        from_block: int,
        to_block: int,
        *,
        addresses: str | Sequence[str],
        topics: str | Sequence[str],
        max_span: int,
    ) -> list[dict[str, Any]]:
        if from_block > to_block:
            return []
        address_filter: str | list[str]
        if isinstance(addresses, str):
            address_filter = normalize_address(addresses)
        else:
            address_filter = [normalize_address(address) for address in addresses]
        topic_filter: list[Any]
        if isinstance(topics, str):
            topic_filter = [normalize_hex(topics, 32)]
        else:
            topic_filter = [[normalize_hex(topic, 32) for topic in topics]]

        def fetch(start: int, end: int) -> list[dict[str, Any]]:
            query = {
                "fromBlock": hex(start),
                "toBlock": hex(end),
                "address": address_filter,
                "topics": topic_filter,
            }
            try:
                result = self.call("eth_getLogs", [query])
            except RpcError as exc:
                if start >= end or not is_log_range_error(exc):
                    raise
                midpoint = (start + end) // 2
                return fetch(start, midpoint) + fetch(midpoint + 1, end)
            return [log for log in result if not log.get("removed", False)]

        logs: list[dict[str, Any]] = []
        cursor = from_block
        while cursor <= to_block:
            end = min(to_block, cursor + max_span - 1)
            logs.extend(fetch(cursor, end))
            cursor = end + 1
        unique: dict[tuple[str, int], dict[str, Any]] = {}
        for log in logs:
            key = (normalize_hex(log["transactionHash"], 32), hex_int(log.get("logIndex", "0x0")))
            unique[key] = log
        return sorted(unique.values(), key=log_position)


class CastKeccak:
    def __init__(self) -> None:
        self.cast = shutil.which("cast")
        if not self.cast:
            raise MonitorError("Foundry cast is required but was not found in PATH")
        self.cache: dict[bytes, str] = {}

    def digest(self, value: bytes) -> str:
        cached = self.cache.get(value)
        if cached:
            return cached
        try:
            result = subprocess.run(
                [self.cast, "keccak", "0x" + value.hex()],
                check=True,
                capture_output=True,
                text=True,
                timeout=15,
            )
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
            raise MonitorError("cast keccak failed") from exc
        digest = normalize_hex(result.stdout.strip(), 32)
        self.cache[value] = digest
        return digest

    def domain_separator(self, name: str, version: str, chain_id: int, verifying_contract: str) -> str:
        name_hash = bytes_from_hex(self.digest(name.encode("utf-8")))
        if version == "1":
            version_hash = bytes_from_hex(VERSION_ONE_HASH)
        else:
            version_hash = bytes_from_hex(self.digest(version.encode("utf-8")))
        payload = b"".join(
            [
                bytes_from_hex(DOMAIN_TYPEHASH),
                name_hash,
                version_hash,
                chain_id.to_bytes(32, "big"),
                bytes(12) + bytes_from_hex(normalize_address(verifying_contract)),
            ]
        )
        return self.digest(payload)


def rpc_eth_call(rpc: JsonRpc, address: str, selector: str, block_tag: Any = "latest") -> str:
    return rpc.call("eth_call", [{"to": normalize_address(address), "data": selector}, block_tag])


def query_domains(
    rpc: JsonRpc, addresses: Sequence[str], block_tag: Any
) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]]]:
    ordered = [normalize_address(address) for address in addresses]
    results: list[Any | RpcError] = []
    for address_group in groups(ordered, size=80):
        aggregate_calls: list[tuple[str, str]] = []
        for address in address_group:
            aggregate_calls.append((address, EIP712_DOMAIN_SELECTOR))
            aggregate_calls.append((address, DOMAIN_SELECTOR))
        try:
            encoded = encode_aggregate3(aggregate_calls)
            raw_result = rpc.call(
                "eth_call", [{"to": MULTICALL3, "data": encoded}, block_tag]
            )
            decoded = decode_aggregate3_result(raw_result)
            if len(decoded) != len(aggregate_calls):
                raise MonitorError(
                    f"Multicall returned {len(decoded)} rows for {len(aggregate_calls)} calls"
                )
            for success, value in decoded:
                results.append(value if success else RpcError("Multicall subcall failed"))
        except (MonitorError, RpcError):
            fallback = [
                ("eth_call", [{"to": target, "data": call_data}, block_tag])
                for target, call_data in aggregate_calls
            ]
            results.extend(rpc.batch(fallback))
    domains: dict[str, dict[str, Any]] = {}
    errors: list[dict[str, Any]] = []
    if len(results) != len(ordered) * 2:
        raise MonitorError(
            f"domain query returned {len(results)} rows for {len(ordered) * 2} calls"
        )
    for index, address in enumerate(ordered):
        domain_result = results[index * 2]
        separator_result = results[index * 2 + 1]
        if isinstance(domain_result, RpcError) or isinstance(separator_result, RpcError):
            errors.append(
                {
                    "type": "domain_query_failed",
                    "proxy": address,
                    "block": block_tag,
                    "domain_error": str(domain_result) if isinstance(domain_result, RpcError) else None,
                    "separator_error": str(separator_result) if isinstance(separator_result, RpcError) else None,
                }
            )
            continue
        try:
            domain = decode_eip712_domain(str(domain_result))
            domain["separator"] = normalize_hex(str(separator_result), 32)
            domains[address] = domain
        except MonitorError as exc:
            errors.append({"type": "domain_decode_failed", "proxy": address, "error": str(exc)})
    return domains, errors


def require_complete_domain_sweep(
    domains: dict[str, dict[str, Any]],
    errors: Sequence[dict[str, Any]],
    expected_addresses: Sequence[str],
    block_number: int,
) -> None:
    expected = {normalize_address(address) for address in expected_addresses}
    observed = set(domains)
    missing = sorted(expected - observed)
    unexpected = sorted(observed - expected)
    if errors or missing or unexpected:
        raise MonitorError(
            f"incomplete domain sweep at block {block_number}: "
            f"{len(errors)} query/decode failures, {len(missing)} missing, "
            f"{len(unexpected)} unexpected; first errors: {list(errors[:3])}; "
            f"first missing: {missing[:3]}; first unexpected: {unexpected[:3]}"
        )


def code_sha256(rpc: JsonRpc, address: str, block_tag: Any = "latest") -> str:
    code = bytes_from_hex(rpc.call("eth_getCode", [normalize_address(address), block_tag]))
    return hashlib.sha256(code).hexdigest()


def anchor_snapshot(rpc: JsonRpc, block_tag: Any) -> dict[str, Any]:
    registry_implementation = decode_address_word(
        rpc_eth_call(rpc, REGISTRY, IMPLEMENTATION_SELECTOR, block_tag)
    )
    factory_beacon = decode_address_word(rpc_eth_call(rpc, FACTORY, BEACON_SELECTOR, block_tag))
    factory_slot = normalize_hex(
        rpc.call("eth_getStorageAt", [FACTORY, EIP1967_IMPLEMENTATION_SLOT, block_tag]), 32
    )
    factory_implementation = decode_address_word(factory_slot)
    return {
        "registry_code_sha256": code_sha256(rpc, REGISTRY, block_tag),
        "registry_implementation": registry_implementation,
        "stock_implementation_code_sha256": code_sha256(rpc, registry_implementation, block_tag),
        "stock_proxy_code_sha256": code_sha256(rpc, TSLA_PROXY, block_tag),
        "factory_proxy_code_sha256": code_sha256(rpc, FACTORY, block_tag),
        "factory_beacon": factory_beacon,
        "factory_implementation_slot": factory_slot,
        "factory_implementation": factory_implementation,
        "factory_implementation_code_sha256": code_sha256(rpc, factory_implementation, block_tag),
        "sensitive_principal_code_sha256": {
            label: code_sha256(rpc, address, block_tag)
            for label, address in sorted(SENSITIVE_PRINCIPALS.items())
        },
    }


def groups(values: Sequence[str], size: int = 40) -> Iterable[list[str]]:
    for start in range(0, len(values), size):
        yield list(values[start : start + size])


def history_entry(
    *,
    source: str,
    name: str,
    symbol: str | None,
    separator: str,
    chain_id: int,
    proxy: str,
    evidence: dict[str, Any],
    version: str = "1",
    domain_details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    entry = {
        "source": source,
        "name": name,
        "version": version,
        "chain_id": chain_id,
        "verifying_contract": normalize_address(proxy),
        "separator": normalize_hex(separator, 32),
        **evidence,
    }
    if symbol is not None:
        entry["symbol"] = symbol
    if domain_details is not None:
        entry.update(
            {
                "fields": domain_details.get("fields"),
                "salt": domain_details.get("salt"),
                "extensions": domain_details.get("extensions"),
            }
        )
    return entry


def current_domain_details(name: str, proxy: str, separator: str) -> dict[str, Any]:
    return {
        "fields": "0x0f",
        "name": name,
        "version": "1",
        "chain_id": EXPECTED_CHAIN_ID,
        "verifying_contract": normalize_address(proxy),
        "salt": "0x" + "00" * 32,
        "extensions": [],
        "separator": normalize_hex(separator, 32),
    }


def append_history(proxy_state: dict[str, Any], entry: dict[str, Any]) -> bool:
    previous = proxy_state["history"][-1]["separator"] if proxy_state["history"] else None
    seen_before = any(item["separator"] == entry["separator"] for item in proxy_state["history"])
    proxy_state["history"].append(entry)
    proxy_state["current_separator"] = entry["separator"]
    proxy_state["current_name"] = entry["name"]
    if "symbol" in entry:
        proxy_state["current_symbol"] = entry["symbol"]
    return bool(previous and previous != entry["separator"] and seen_before)


def build_bootstrap_state(
    rpc: JsonRpc,
    hasher: CastKeccak,
    safe_head: int,
    max_log_span: int,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    chain_id = rpc.chain_id()
    if chain_id != EXPECTED_CHAIN_ID:
        raise MonitorError(f"wrong chain id: expected {EXPECTED_CHAIN_ID}, got {chain_id}")

    deployments = rpc.get_logs(
        0,
        safe_head,
        addresses=FACTORY,
        topics=DEPLOYED_TOPIC,
        max_span=max_log_span,
    )
    if not deployments:
        raise MonitorError("canonical Factory returned zero deployments")
    if len(deployments) < MIN_BASELINE_DEPLOYMENTS:
        raise MonitorError(
            f"incomplete Factory history: expected at least {MIN_BASELINE_DEPLOYMENTS}, "
            f"received {len(deployments)}"
        )

    proxies: dict[str, dict[str, Any]] = {}
    seen_uids: set[str] = set()
    for log in deployments:
        address, name, symbol = decode_factory_data(log["data"])
        uid = normalize_hex(log["topics"][1], 32)
        if address in proxies:
            raise MonitorError(f"duplicate Factory deployment address {address}")
        if uid in seen_uids:
            raise MonitorError(f"duplicate Factory UID {uid}")
        seen_uids.add(uid)
        separator = hasher.domain_separator(name, "1", chain_id, address)
        entry = history_entry(
            source="Factory.Deployed",
            name=name,
            symbol=symbol,
            separator=separator,
            chain_id=chain_id,
            proxy=address,
            evidence=log_evidence(log),
            domain_details=current_domain_details(name, address, separator),
        )
        proxies[address] = {
            "uid": uid,
            "current_name": name,
            "current_symbol": symbol,
            "current_separator": separator,
            "history": [entry],
        }

    metadata_logs: list[dict[str, Any]] = []
    proxy_addresses = sorted(proxies)
    for address_group in groups(proxy_addresses):
        metadata_logs.extend(
            rpc.get_logs(
                0,
                safe_head,
                addresses=address_group,
                topics=METADATA_TOPIC,
                max_span=max_log_span,
            )
        )
    metadata_logs.sort(key=log_position)
    if len(metadata_logs) < MIN_BASELINE_METADATA_TRANSITIONS:
        raise MonitorError(
            f"incomplete metadata history: expected at least {MIN_BASELINE_METADATA_TRANSITIONS}, "
            f"received {len(metadata_logs)}"
        )

    alerts: list[dict[str, Any]] = []
    for log in metadata_logs:
        address = normalize_address(log["address"])
        if address not in proxies:
            raise MonitorError(f"metadata event came from non-Factory proxy {address}")
        name, symbol = decode_metadata_data(log["data"])
        separator = hasher.domain_separator(name, "1", chain_id, address)
        entry = history_entry(
            source="Stock.MetaDataUpdated",
            name=name,
            symbol=symbol,
            separator=separator,
            chain_id=chain_id,
            proxy=address,
            evidence=log_evidence(log),
            domain_details=current_domain_details(name, address, separator),
        )
        if append_history(proxies[address], entry):
            alerts.append(
                {
                    "type": "historical_domain_reuse",
                    "priority": "urgent",
                    "disposition": "reopen_candidate",
                    "proxy": address,
                    "separator": separator,
                    **log_evidence(log),
                }
            )

    safe_hash = rpc.block_hash(safe_head)
    block_ref = {"blockHash": safe_hash, "requireCanonical": True}

    # Validate the reconstruction at one canonical near-head state. Incomplete
    # coverage is a hard monitor failure and must never advance the cursor.
    domains, domain_errors = query_domains(rpc, proxy_addresses, block_ref)
    if domain_errors:
        sample = domain_errors[:3]
        raise MonitorError(f"domain validation failed for {len(domain_errors)} proxies: {sample}")

    for address, proxy_state in proxies.items():
        domain = domains.get(address)
        if not domain:
            raise MonitorError(f"no domain result for {address}")
        expected = proxy_state["current_separator"]
        if domain["verifying_contract"] != address:
            raise MonitorError(f"{address} reports different verifying contract {domain['verifying_contract']}")
        if domain["chain_id"] != chain_id:
            raise MonitorError(f"{address} reports wrong domain chain {domain['chain_id']}")
        recomputed = hasher.domain_separator(
            domain["name"], domain["version"], domain["chain_id"], domain["verifying_contract"]
        )
        if recomputed != domain["separator"]:
            raise MonitorError(f"{address} EIP-5267 tuple does not match DOMAIN_SEPARATOR")
        if domain["separator"] != expected:
            raise MonitorError(
                f"{address} event-derived separator {expected} does not match live {domain['separator']}"
            )
        proxy_state["domain"] = domain

    # Every extant Stock is expected to remain a BeaconProxy bound to the Registry.
    beacon_calls = [
        ("eth_getStorageAt", [address, EIP1967_BEACON_SLOT, block_ref])
        for address in proxy_addresses
    ]
    beacon_results = rpc.batch(beacon_calls)
    if len(beacon_results) != len(proxy_addresses):
        raise MonitorError(
            f"beacon validation returned {len(beacon_results)} rows for "
            f"{len(proxy_addresses)} proxies"
        )
    for address, result in zip(proxy_addresses, beacon_results):
        if isinstance(result, RpcError):
            raise MonitorError(f"failed to read beacon slot for {address}: {result}")
        beacon = decode_address_word(str(result))
        if beacon != REGISTRY:
            raise MonitorError(f"{address} beacon slot points to {beacon}, expected {REGISTRY}")

    now = utc_now()
    anchors = anchor_snapshot(rpc, block_ref)
    for key, expected in PINNED_ANCHORS.items():
        if anchors.get(key) != expected:
            raise MonitorError(
                f"bootstrap control anchor {key} changed: expected {expected}, got {anchors.get(key)}"
            )

    state = {
        "schema_version": 1,
        "created_at": now,
        "updated_at": now,
        "network": {
            "name": "Robinhood Chain mainnet",
            "chain_id": chain_id,
            "genesis_hash": rpc.block_hash(0),
            "factory": FACTORY,
            "registry": REGISTRY,
            "confirmations": None,
        },
        "last_scanned": {"block_number": safe_head, "block_hash": safe_hash},
        "anchors": anchors,
        "domain_formula_trusted": True,
        "proxies": dict(sorted(proxies.items())),
        "counts": {
            "factory_deployments": len(deployments),
            "metadata_transitions": len(metadata_logs),
            "domain_states": sum(len(proxy["history"]) for proxy in proxies.values()),
        },
    }
    return state, alerts


def event_details(log: dict[str, Any]) -> dict[str, Any]:
    topic0 = normalize_hex(log["topics"][0], 32)
    details: dict[str, Any] = {"contract": normalize_address(log["address"]), **log_evidence(log)}
    if topic0 == UPGRADED_TOPIC and len(log["topics"]) > 1:
        details.update({"type": "upgrade", "implementation": decode_topic_address(log["topics"][1])})
    elif topic0 in (ROLE_GRANTED_TOPIC, ROLE_REVOKED_TOPIC):
        details.update(
            {
                "type": "role_granted" if topic0 == ROLE_GRANTED_TOPIC else "role_revoked",
                "role": normalize_hex(log["topics"][1], 32),
                "account": decode_topic_address(log["topics"][2]),
                "sender": decode_topic_address(log["topics"][3]),
            }
        )
    elif topic0 == ROLE_ADMIN_CHANGED_TOPIC:
        details.update(
            {
                "type": "role_admin_changed",
                "role": normalize_hex(log["topics"][1], 32),
                "previous_admin": normalize_hex(log["topics"][2], 32),
                "new_admin": normalize_hex(log["topics"][3], 32),
            }
        )
    elif topic0 == INITIALIZED_TOPIC:
        raw = bytes_from_hex(log.get("data", "0x"))
        details.update({"type": "unexpected_initialized", "version": int.from_bytes(raw, "big")})
    elif topic0 == EIP712_DOMAIN_CHANGED_TOPIC:
        details.update({"type": "eip712_domain_changed"})
    else:
        details.update({"type": "unknown_signal", "topic0": topic0})
    return details


def is_expected_new_proxy_initializer(
    log: dict[str, Any],
    details: dict[str, Any],
    new_addresses: Sequence[str],
    deployment_logs: Sequence[dict[str, Any]],
) -> bool:
    """Return true only for Initialized(1) emitted in its Factory deployment tx."""
    if details.get("type") != "unexpected_initialized" or details.get("version") != 1:
        return False
    initializer_address = normalize_address(log["address"])
    if initializer_address not in set(new_addresses):
        return False
    transaction_hash = normalize_hex(log["transactionHash"], 32)
    return any(
        normalize_address(deployment["address"]) == FACTORY
        and normalize_hex(deployment["transactionHash"], 32) == transaction_hash
        and decode_factory_data(deployment["data"])[0] == initializer_address
        for deployment in deployment_logs
    )


def append_observed_domain(
    proxy_state: dict[str, Any], domain: dict[str, Any], block_number: int, source: str
) -> bool:
    entry = history_entry(
        source=source,
        name=domain["name"],
        symbol=None,
        separator=domain["separator"],
        chain_id=domain["chain_id"],
        proxy=domain["verifying_contract"],
        evidence={"block_number": block_number, "transaction_hash": None, "log_index": None},
        version=domain["version"],
        domain_details=domain,
    )
    if proxy_state.get("current_separator") == entry["separator"]:
        proxy_state["domain"] = domain
        proxy_state["current_name"] = domain["name"]
        return False
    reused = append_history(proxy_state, entry)
    proxy_state["domain"] = domain
    return reused


def compare_anchors(previous: dict[str, Any], current: dict[str, Any]) -> list[dict[str, Any]]:
    alerts: list[dict[str, Any]] = []
    for key in sorted(set(previous) | set(current)):
        if previous.get(key) != current.get(key):
            alerts.append(
                {
                    "type": "control_anchor_changed",
                    "priority": "review",
                    "disposition": "control_plane_review",
                    "field": key,
                    "before": previous.get(key),
                    "after": current.get(key),
                }
            )
    return alerts


def check_state(
    rpc: JsonRpc,
    hasher: CastKeccak,
    state: dict[str, Any],
    safe_head: int,
    confirmations: int,
    max_log_span: int,
    max_cursor_gap: int,
) -> tuple[dict[str, Any], dict[str, Any]]:
    network = state.get("network", {})
    if network.get("chain_id") != EXPECTED_CHAIN_ID or rpc.chain_id() != EXPECTED_CHAIN_ID:
        raise MonitorError("state or RPC chain ID does not match Robinhood Chain mainnet")
    if normalize_hex(network.get("genesis_hash", "0x"), 32) != rpc.block_hash(0):
        raise MonitorError("RPC genesis hash does not match the bootstrapped Robinhood network")
    if normalize_address(network.get("factory", "0x")) != FACTORY:
        raise MonitorError("state Factory address does not match the canonical Factory")
    if normalize_address(network.get("registry", "0x")) != REGISTRY:
        raise MonitorError("state Registry address does not match the canonical Registry")

    last_scanned = state["last_scanned"]
    previous_block = int(last_scanned["block_number"])
    previous_hash = normalize_hex(last_scanned["block_hash"], 32)
    if safe_head < previous_block:
        raise MonitorError(
            f"confirmation-buffered head {safe_head} is behind stored cursor {previous_block}"
        )
    cursor_gap = safe_head - previous_block
    if cursor_gap > max_cursor_gap:
        raise MonitorError(
            f"cursor gap {cursor_gap} blocks exceeds the reviewed maximum {max_cursor_gap}; "
            "near-head state continuity cannot be guaranteed on the pruned public RPC"
        )
    if rpc.block_hash(previous_block) != previous_hash:
        raise MonitorError(
            f"confirmation-buffered checkpoint block {previous_block} changed hash; "
            "rebuild state before advancing"
        )

    alerts: list[dict[str, Any]] = []
    changes = {"deployments": 0, "metadata": 0, "upgrades": 0, "roles": 0, "unexpected": 0}
    safe_hash = rpc.block_hash(safe_head)
    block_ref = {"blockHash": safe_hash, "requireCanonical": True}
    current_anchors = anchor_snapshot(rpc, block_ref)
    alerts.extend(compare_anchors(state.get("anchors", {}), current_anchors))

    if safe_head > previous_block:
        start = previous_block + 1
        registry_signals = rpc.get_logs(
            start,
            safe_head,
            addresses=REGISTRY,
            topics=[UPGRADED_TOPIC, ROLE_GRANTED_TOPIC, ROLE_REVOKED_TOPIC, ROLE_ADMIN_CHANGED_TOPIC],
            max_span=max_log_span,
        )
        factory_upgrades = rpc.get_logs(
            start,
            safe_head,
            addresses=FACTORY,
            topics=UPGRADED_TOPIC,
            max_span=max_log_span,
        )
        registry_upgraded = any(
            normalize_hex(log["topics"][0], 32) == UPGRADED_TOPIC for log in registry_signals
        )
        formula_trusted = bool(state.get("domain_formula_trusted", True)) and not registry_upgraded
        deployment_logs = rpc.get_logs(
            start,
            safe_head,
            addresses=FACTORY,
            topics=DEPLOYED_TOPIC,
            max_span=max_log_span,
        )

        proxies: dict[str, dict[str, Any]] = state["proxies"]
        new_addresses: list[str] = []
        for log in deployment_logs:
            address, name, symbol = decode_factory_data(log["data"])
            uid = normalize_hex(log["topics"][1], 32)
            if address in proxies:
                alerts.append(
                    {
                        "type": "duplicate_factory_address",
                        "priority": "urgent",
                        "disposition": "control_plane_review",
                        "proxy": address,
                        **log_evidence(log),
                    }
                )
                continue
            if formula_trusted:
                separator = hasher.domain_separator(name, "1", EXPECTED_CHAIN_ID, address)
                entry = history_entry(
                    source="Factory.Deployed",
                    name=name,
                    symbol=symbol,
                    separator=separator,
                    chain_id=EXPECTED_CHAIN_ID,
                    proxy=address,
                    evidence=log_evidence(log),
                    domain_details=current_domain_details(name, address, separator),
                )
                history = [entry]
            else:
                separator = None
                history = []
                alerts.append(
                    {
                        "type": "deployment_under_unreviewed_stock_implementation",
                        "priority": "review",
                        "disposition": "control_plane_review",
                        "proxy": address,
                        **log_evidence(log),
                    }
                )
            proxies[address] = {
                "uid": uid,
                "current_name": name,
                "current_symbol": symbol,
                "current_separator": separator,
                "history": history,
            }
            new_addresses.append(address)
            changes["deployments"] += 1

        all_addresses = sorted(proxies)
        metadata_logs: list[dict[str, Any]] = []
        for address_group in groups(all_addresses):
            metadata_logs.extend(
                rpc.get_logs(
                    start,
                    safe_head,
                    addresses=address_group,
                    topics=METADATA_TOPIC,
                    max_span=max_log_span,
                )
            )
        metadata_logs.sort(key=log_position)
        affected: set[str] = set(new_addresses)
        for log in metadata_logs:
            address = normalize_address(log["address"])
            if address not in proxies:
                alerts.append(
                    {
                        "type": "metadata_from_unknown_proxy",
                        "priority": "urgent",
                        "disposition": "control_plane_review",
                        "proxy": address,
                        **log_evidence(log),
                    }
                )
                continue
            name, symbol = decode_metadata_data(log["data"])
            if not formula_trusted:
                alerts.append(
                    {
                        "type": "metadata_under_unreviewed_stock_implementation",
                        "priority": "review",
                        "disposition": "control_plane_review",
                        "proxy": address,
                        "name": name,
                        "symbol": symbol,
                        **log_evidence(log),
                    }
                )
                affected.add(address)
                changes["metadata"] += 1
                continue
            separator = hasher.domain_separator(name, "1", EXPECTED_CHAIN_ID, address)
            entry = history_entry(
                source="Stock.MetaDataUpdated",
                name=name,
                symbol=symbol,
                separator=separator,
                chain_id=EXPECTED_CHAIN_ID,
                proxy=address,
                evidence=log_evidence(log),
                domain_details=current_domain_details(name, address, separator),
            )
            if append_history(proxies[address], entry):
                alerts.append(
                    {
                        "type": "domain_separator_reused",
                        "priority": "urgent",
                        "disposition": "reopen_candidate",
                        "proxy": address,
                        "separator": separator,
                        "name": name,
                        **log_evidence(log),
                    }
                )
            affected.add(address)
            changes["metadata"] += 1

        unexpected_logs: list[dict[str, Any]] = []
        for address_group in groups(all_addresses):
            unexpected_logs.extend(
                rpc.get_logs(
                    start,
                    safe_head,
                    addresses=address_group,
                    topics=[INITIALIZED_TOPIC, EIP712_DOMAIN_CHANGED_TOPIC],
                    max_span=max_log_span,
                )
            )

        domain_affecting_control_change = False
        for log in sorted(registry_signals + factory_upgrades + unexpected_logs, key=log_position):
            details = event_details(log)
            if is_expected_new_proxy_initializer(
                log, details, new_addresses, deployment_logs
            ):
                continue
            details["priority"] = "review"
            details["disposition"] = "control_plane_review"
            alerts.append(details)
            if details["type"] == "upgrade":
                changes["upgrades"] += 1
                domain_affecting_control_change = True
            elif details["type"].startswith("role_"):
                changes["roles"] += 1
            else:
                changes["unexpected"] += 1
                domain_affecting_control_change = True

        if domain_affecting_control_change:
            affected = set(all_addresses)

        # The raw separator is the authority consumed by permit. Sweep every
        # canonical proxy every time so future unlogged mutators cannot become
        # a false quiet after an implementation change.
        affected = set(all_addresses)

        if affected:
            domains, errors = query_domains(rpc, sorted(affected), block_ref)
            require_complete_domain_sweep(domains, errors, sorted(affected), safe_head)
            for address, domain in domains.items():
                supported_shape = (
                    domain["fields"] == "0x0f"
                    and domain["salt"] == "0x" + "00" * 32
                    and domain["extensions"] == []
                )
                recomputed = None
                if supported_shape:
                    recomputed = hasher.domain_separator(
                        domain["name"],
                        domain["version"],
                        domain["chain_id"],
                        domain["verifying_contract"],
                    )
                else:
                    alerts.append(
                        {
                            "type": "unsupported_eip712_domain_shape",
                            "priority": "review",
                            "disposition": "control_plane_review",
                            "proxy": address,
                            "domain": domain,
                        }
                    )
                if recomputed is not None and recomputed != domain["separator"]:
                    alerts.append(
                        {
                            "type": "domain_tuple_separator_mismatch",
                            "priority": "urgent",
                            "disposition": "control_plane_review",
                            "proxy": address,
                            "reported_separator": domain["separator"],
                            "recomputed_separator": recomputed,
                        }
                    )
                expected = proxies[address].get("current_separator")
                if expected is None:
                    reused = append_observed_domain(
                        proxies[address], domain, safe_head, "pinned live domain observation"
                    )
                    if reused:
                        alerts.append(
                            {
                                "type": "domain_separator_reused",
                                "priority": "urgent",
                                "disposition": "reopen_candidate",
                                "proxy": address,
                                "separator": domain["separator"],
                            }
                        )
                elif domain["separator"] != expected:
                    reused = append_observed_domain(
                        proxies[address], domain, safe_head, "live observation after control change"
                    )
                    alerts.append(
                        {
                            "type": "unexplained_domain_change",
                            "priority": "urgent",
                            "disposition": "control_plane_review",
                            "proxy": address,
                            "expected_separator": expected,
                            "observed_separator": domain["separator"],
                            "reused_prior_separator": reused,
                        }
                    )
                else:
                    proxies[address]["domain"] = domain

        for address in new_addresses:
            proxy_state = proxies[address]
            beacon_word = rpc.call("eth_getStorageAt", [address, EIP1967_BEACON_SLOT, block_ref])
            beacon = decode_address_word(beacon_word)
            if beacon != REGISTRY:
                alerts.append(
                    {
                        "type": "new_proxy_wrong_beacon",
                        "priority": "urgent",
                        "disposition": "control_plane_review",
                        "proxy": address,
                        "beacon": beacon,
                    }
                )
            proxy_code_hash = code_sha256(rpc, address, block_ref)
            expected_proxy_code_hash = current_anchors["stock_proxy_code_sha256"]
            if proxy_code_hash != expected_proxy_code_hash:
                alerts.append(
                    {
                        "type": "new_proxy_runtime_code_changed",
                        "priority": "urgent",
                        "disposition": "control_plane_review",
                        "proxy": address,
                        "expected_sha256": expected_proxy_code_hash,
                        "observed_sha256": proxy_code_hash,
                    }
                )
            factory_address = decode_address_word(
                rpc_eth_call(
                    rpc,
                    FACTORY,
                    TOKEN_ADDRESS_SELECTOR + proxy_state["uid"][2:],
                    block_ref,
                )
            )
            if factory_address != address:
                alerts.append(
                    {
                        "type": "new_proxy_factory_mapping_mismatch",
                        "priority": "urgent",
                        "disposition": "control_plane_review",
                        "proxy": address,
                        "factory_mapping": factory_address,
                        "uid": proxy_state["uid"],
                    }
                )
            proxy_uid = normalize_hex(
                rpc_eth_call(rpc, address, UID_SELECTOR, block_ref), 32
            )
            if proxy_uid != proxy_state["uid"]:
                alerts.append(
                    {
                        "type": "new_proxy_uid_mismatch",
                        "priority": "urgent",
                        "disposition": "control_plane_review",
                        "proxy": address,
                        "factory_uid": proxy_state["uid"],
                        "proxy_uid": proxy_uid,
                    }
                )
            access_registry = decode_address_word(
                rpc_eth_call(rpc, address, ACCESS_CONTROLLED_REGISTRY_SELECTOR, block_ref)
            )
            if access_registry != REGISTRY:
                alerts.append(
                    {
                        "type": "new_proxy_access_registry_mismatch",
                        "priority": "urgent",
                        "disposition": "control_plane_review",
                        "proxy": address,
                        "access_registry": access_registry,
                    }
                )

        state["counts"] = {
            "factory_deployments": len(proxies),
            "metadata_transitions": state["counts"]["metadata_transitions"] + len(metadata_logs),
            "domain_states": sum(len(proxy["history"]) for proxy in proxies.values()),
        }
        state["last_scanned"] = {
            "block_number": safe_head,
            "block_hash": safe_hash,
        }
        state["domain_formula_trusted"] = formula_trusted

    state["anchors"] = current_anchors
    state["network"]["confirmations"] = confirmations
    state["updated_at"] = utc_now()
    result = {
        "coverage_ok": True,
        "status": "alert" if alerts else "ok",
        "checked_at": state["updated_at"],
        "scanned_from": previous_block + 1 if safe_head > previous_block else None,
        "scanned_through": state["last_scanned"]["block_number"],
        "latest_safe_head": safe_head,
        "cursor_gap": cursor_gap,
        "proxy_count": len(state["proxies"]),
        "domain_state_count": state["counts"]["domain_states"],
        "changes": changes,
        "alerts": alerts,
    }
    return state, result


def atomic_write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def append_alert_log(path: Path, result: dict[str, Any]) -> None:
    if not result.get("alerts"):
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def load_state(path: Path) -> dict[str, Any]:
    try:
        with path.open(encoding="utf-8") as handle:
            state = json.load(handle)
    except FileNotFoundError as exc:
        raise MonitorError(f"state file does not exist: {path}") from exc
    except json.JSONDecodeError as exc:
        raise MonitorError(f"state file is invalid JSON: {path}") from exc
    if state.get("schema_version") != 1:
        raise MonitorError(f"unsupported state schema: {state.get('schema_version')}")
    return state


def state_summary(state: dict[str, Any]) -> dict[str, Any]:
    return {
        "coverage_ok": True,
        "status": "state",
        "updated_at": state.get("updated_at"),
        "last_scanned": state.get("last_scanned"),
        "proxy_count": len(state.get("proxies", {})),
        "counts": state.get("counts", {}),
        "anchors": state.get("anchors", {}),
    }


def bootstrap(
    rpc: JsonRpc,
    state_path: Path,
    alert_log: Path,
    confirmations: int,
    max_log_span: int,
    force: bool,
) -> dict[str, Any]:
    if state_path.exists() and not force:
        raise MonitorError(f"state already exists at {state_path}; use check or bootstrap --force")
    latest = rpc.block_number()
    if latest <= confirmations:
        raise MonitorError(f"latest block {latest} is below confirmation depth {confirmations}")
    safe_head = latest - confirmations
    state, alerts = build_bootstrap_state(rpc, CastKeccak(), safe_head, max_log_span)
    state["network"]["confirmations"] = confirmations
    result = {
        "coverage_ok": True,
        "status": "alert" if alerts else "bootstrapped",
        "checked_at": state["updated_at"],
        "scanned_through": safe_head,
        "proxy_count": len(state["proxies"]),
        "domain_state_count": state["counts"]["domain_states"],
        "metadata_transition_count": state["counts"]["metadata_transitions"],
        "alerts": alerts,
    }
    # Persist an alert before advancing the cursor so a log-write failure is
    # replayable on the next run instead of becoming a false quiet.
    append_alert_log(alert_log, result)
    atomic_write_json(state_path, state)
    return result


def execute_check(
    rpc: JsonRpc,
    state_path: Path,
    alert_log: Path,
    confirmations: int,
    max_log_span: int,
    max_cursor_gap: int = DEFAULT_MAX_CURSOR_GAP,
) -> dict[str, Any]:
    if not state_path.exists():
        raise MonitorError(
            f"state file does not exist: {state_path}; run bootstrap explicitly "
            "after reviewing the pinned anchors"
        )
    state = load_state(state_path)
    latest = rpc.block_number()
    if latest <= confirmations:
        raise MonitorError(f"latest block {latest} is below confirmation depth {confirmations}")
    safe_head = latest - confirmations
    updated, result = check_state(
        rpc,
        CastKeccak(),
        state,
        safe_head,
        confirmations,
        max_log_span,
        max_cursor_gap,
    )
    # Alert durability precedes cursor advancement. If this append fails, the
    # unchanged cursor makes the entire range replayable.
    append_alert_log(alert_log, result)
    atomic_write_json(state_path, updated)
    return result


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("bootstrap", "check", "status"))
    parser.add_argument("--rpc-url", default=os.environ.get("ROBINHOOD_RPC_URL", DEFAULT_RPC_URL))
    parser.add_argument("--state-file", type=Path, default=DEFAULT_STATE_FILE)
    parser.add_argument("--alert-log", type=Path, default=DEFAULT_ALERT_LOG)
    parser.add_argument("--confirmations", type=int, default=128)
    parser.add_argument("--max-log-span", type=int, default=10_000_000)
    parser.add_argument("--max-cursor-gap", type=int, default=DEFAULT_MAX_CURSOR_GAP)
    parser.add_argument("--force", action="store_true", help="replace an existing bootstrap state")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    if args.confirmations < 0:
        print(json.dumps({"coverage_ok": False, "status": "error", "error": "confirmations must be non-negative"}))
        return 1
    if args.max_log_span <= 0:
        print(json.dumps({"coverage_ok": False, "status": "error", "error": "max-log-span must be positive"}))
        return 1
    if args.max_cursor_gap <= 0:
        print(json.dumps({"coverage_ok": False, "status": "error", "error": "max-cursor-gap must be positive"}))
        return 1

    state_path = args.state_file.expanduser().resolve()
    alert_log = args.alert_log.expanduser().resolve()
    lock_path = state_path.with_suffix(state_path.suffix + ".lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with lock_path.open("a+") as lock:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            if args.command == "status":
                result = state_summary(load_state(state_path))
            else:
                rpc = JsonRpc(args.rpc_url)
                if args.command == "bootstrap":
                    result = bootstrap(
                        rpc,
                        state_path,
                        alert_log,
                        args.confirmations,
                        args.max_log_span,
                        args.force,
                    )
                else:
                    result = execute_check(
                        rpc,
                        state_path,
                        alert_log,
                        args.confirmations,
                        args.max_log_span,
                        args.max_cursor_gap,
                    )
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0
    except BlockingIOError:
        print(json.dumps({"coverage_ok": False, "status": "error", "error": "another monitor run holds the state lock"}))
        return 1
    except (MonitorError, OSError) as exc:
        print(json.dumps({"coverage_ok": False, "status": "error", "error": str(exc)}, ensure_ascii=False, sort_keys=True))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
