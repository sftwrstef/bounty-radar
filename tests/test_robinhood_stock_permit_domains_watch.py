#!/usr/bin/env python3

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch


MODULE_PATH = Path(__file__).resolve().parents[1] / "monitors/robinhood_stock_permit_domains.py"
SPEC = importlib.util.spec_from_file_location("domain_monitor", MODULE_PATH)
assert SPEC and SPEC.loader
MONITOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MONITOR)


class DomainMonitorUnitTest(unittest.TestCase):
    def test_single_aggregate3_call_matches_cast_encoding(self) -> None:
        encoded = MONITOR.encode_aggregate3(
            [
                (
                    "0x322F0929c4625eD5bAd873c95208D54E1c003b2d",
                    MONITOR.DOMAIN_SELECTOR,
                )
            ]
        )
        self.assertEqual(
            encoded,
            "0x82ad56cb"
            "0000000000000000000000000000000000000000000000000000000000000020"
            "0000000000000000000000000000000000000000000000000000000000000001"
            "0000000000000000000000000000000000000000000000000000000000000020"
            "000000000000000000000000322f0929c4625ed5bad873c95208d54e1c003b2d"
            "0000000000000000000000000000000000000000000000000000000000000001"
            "0000000000000000000000000000000000000000000000000000000000000060"
            "0000000000000000000000000000000000000000000000000000000000000004"
            "3644e51500000000000000000000000000000000000000000000000000000000",
        )

    def test_live_tsla_domain_fixture_decodes(self) -> None:
        encoded = (
            "0x0f00000000000000000000000000000000000000000000000000000000000000"
            "00000000000000000000000000000000000000000000000000000000000000e0"
            "0000000000000000000000000000000000000000000000000000000000000120"
            "0000000000000000000000000000000000000000000000000000000000001237"
            "000000000000000000000000322f0929c4625ed5bad873c95208d54e1c003b2d"
            "0000000000000000000000000000000000000000000000000000000000000000"
            "0000000000000000000000000000000000000000000000000000000000000160"
            "0000000000000000000000000000000000000000000000000000000000000019"
            "5465736c6120e280a220526f62696e686f6f6420546f6b656e00000000000000"
            "0000000000000000000000000000000000000000000000000000000000000001"
            "3100000000000000000000000000000000000000000000000000000000000000"
            "0000000000000000000000000000000000000000000000000000000000000000"
        )
        domain = MONITOR.decode_eip712_domain(encoded)
        self.assertEqual(domain["fields"], "0x0f")
        self.assertEqual(domain["name"], "Tesla • Robinhood Token")
        self.assertEqual(domain["version"], "1")
        self.assertEqual(domain["chain_id"], 4663)
        self.assertEqual(
            domain["verifying_contract"], "0x322f0929c4625ed5bad873c95208d54e1c003b2d"
        )
        self.assertEqual(domain["extensions"], [])

    def test_known_tsla_separator_matches(self) -> None:
        separator = MONITOR.CastKeccak().domain_separator(
            "Tesla • Robinhood Token",
            "1",
            4663,
            "0x322F0929c4625eD5bAd873c95208D54E1c003b2d",
        )
        self.assertEqual(
            separator,
            "0xaed03ce8fb70819d92adddf9b9dd4fbb2f32f0e37b6d5937b441c17549d83ed8",
        )

    def test_reuse_requires_an_intervening_distinct_separator(self) -> None:
        proxy = {
            "history": [
                {
                    "separator": "0x" + "11" * 32,
                    "name": "A",
                }
            ],
            "current_separator": "0x" + "11" * 32,
            "current_name": "A",
        }
        same = {"separator": "0x" + "11" * 32, "name": "A"}
        distinct = {"separator": "0x" + "22" * 32, "name": "B"}
        restored = {"separator": "0x" + "11" * 32, "name": "A"}
        self.assertFalse(MONITOR.append_history(proxy, same))
        self.assertFalse(MONITOR.append_history(proxy, distinct))
        self.assertTrue(MONITOR.append_history(proxy, restored))

    def test_only_factory_paired_initialized_one_is_expected(self) -> None:
        proxy = "0x" + "22" * 20
        transaction_hash = "0x" + "33" * 32
        initializer_log = {
            "address": proxy,
            "transactionHash": transaction_hash,
        }
        details = {"type": "unexpected_initialized", "version": 1}
        deployment_logs = [
            {
                "address": MONITOR.FACTORY,
                "transactionHash": transaction_hash,
                "data": "fixture",
            }
        ]
        with patch.object(
            MONITOR, "decode_factory_data", return_value=(proxy, "Name", "SYM")
        ):
            self.assertTrue(
                MONITOR.is_expected_new_proxy_initializer(
                    initializer_log, details, [proxy], deployment_logs
                )
            )
            self.assertFalse(
                MONITOR.is_expected_new_proxy_initializer(
                    initializer_log,
                    {**details, "version": 2},
                    [proxy],
                    deployment_logs,
                )
            )
            self.assertFalse(
                MONITOR.is_expected_new_proxy_initializer(
                    initializer_log,
                    details,
                    [proxy],
                    [{**deployment_logs[0], "transactionHash": "0x" + "44" * 32}],
                )
            )
        with patch.object(
            MONITOR,
            "decode_factory_data",
            return_value=("0x" + "55" * 20, "Name", "SYM"),
        ):
            self.assertFalse(
                MONITOR.is_expected_new_proxy_initializer(
                    initializer_log, details, [proxy], deployment_logs
                )
            )

    def test_check_requires_explicit_bootstrap(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            state_path = Path(directory) / "missing.json"
            rpc = Mock()
            with self.assertRaisesRegex(MONITOR.MonitorError, "run bootstrap explicitly"):
                MONITOR.execute_check(
                    rpc,
                    state_path,
                    Path(directory) / "alerts.jsonl",
                    confirmations=128,
                    max_log_span=1_000,
                )
            self.assertEqual(rpc.mock_calls, [])
            self.assertFalse(state_path.exists())

    def test_domain_sweep_rejects_silent_omission(self) -> None:
        expected = ["0x" + "11" * 20, "0x" + "22" * 20]
        domains = {expected[0]: {"separator": "0x" + "33" * 32}}
        with self.assertRaisesRegex(MONITOR.MonitorError, "1 missing"):
            MONITOR.require_complete_domain_sweep(
                domains,
                errors=[],
                expected_addresses=expected,
                block_number=123,
            )

    def test_alert_is_persisted_before_cursor_advance(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            state_path = Path(directory) / "state.json"
            state_path.write_text("{}", encoding="utf-8")
            rpc = Mock()
            rpc.block_number.return_value = 1_000
            call_order: list[str] = []
            with (
                patch.object(MONITOR, "load_state", return_value={"state": "old"}),
                patch.object(MONITOR, "CastKeccak", return_value=Mock()),
                patch.object(
                    MONITOR,
                    "check_state",
                    return_value=({"state": "new"}, {"alerts": [{"type": "signal"}]}),
                ),
                patch.object(
                    MONITOR,
                    "append_alert_log",
                    side_effect=lambda *_args: call_order.append("alert"),
                ),
                patch.object(
                    MONITOR,
                    "atomic_write_json",
                    side_effect=lambda *_args: call_order.append("state"),
                ),
            ):
                MONITOR.execute_check(
                    rpc,
                    state_path,
                    Path(directory) / "alerts.jsonl",
                    confirmations=128,
                    max_log_span=1_000,
                )
            self.assertEqual(call_order, ["alert", "state"])

    def test_alert_log_failure_prevents_cursor_advance(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            state_path = Path(directory) / "state.json"
            state_path.write_text("{}", encoding="utf-8")
            rpc = Mock()
            rpc.block_number.return_value = 1_000
            with (
                patch.object(MONITOR, "load_state", return_value={"state": "old"}),
                patch.object(MONITOR, "CastKeccak", return_value=Mock()),
                patch.object(
                    MONITOR,
                    "check_state",
                    return_value=({"state": "new"}, {"alerts": [{"type": "signal"}]}),
                ),
                patch.object(MONITOR, "append_alert_log", side_effect=OSError("disk full")),
                patch.object(MONITOR, "atomic_write_json") as write_state,
            ):
                with self.assertRaisesRegex(OSError, "disk full"):
                    MONITOR.execute_check(
                        rpc,
                        state_path,
                        Path(directory) / "alerts.jsonl",
                        confirmations=128,
                        max_log_span=1_000,
                    )
            write_state.assert_not_called()

    def test_incomplete_sweep_does_not_persist_or_advance_cursor(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            state_path = Path(directory) / "state.json"
            proxy = "0x" + "11" * 20
            genesis_hash = "0x" + "22" * 32
            cursor_hash = "0x" + "33" * 32
            safe_hash = "0x" + "44" * 32
            state = {
                "schema_version": 1,
                "network": {
                    "chain_id": MONITOR.EXPECTED_CHAIN_ID,
                    "genesis_hash": genesis_hash,
                    "factory": MONITOR.FACTORY,
                    "registry": MONITOR.REGISTRY,
                    "confirmations": 128,
                },
                "last_scanned": {"block_number": 800, "block_hash": cursor_hash},
                "anchors": {},
                "domain_formula_trusted": True,
                "proxies": {
                    proxy: {
                        "uid": "0x" + "55" * 32,
                        "current_name": "Stock",
                        "current_symbol": "STK",
                        "current_separator": "0x" + "66" * 32,
                        "history": [{"separator": "0x" + "66" * 32}],
                    }
                },
                "counts": {
                    "factory_deployments": 1,
                    "metadata_transitions": 0,
                    "domain_states": 1,
                },
            }
            original = json.dumps(state)
            state_path.write_text(original, encoding="utf-8")
            rpc = Mock()
            rpc.block_number.return_value = 1_000
            rpc.chain_id.return_value = MONITOR.EXPECTED_CHAIN_ID
            rpc.block_hash.side_effect = lambda number: {
                0: genesis_hash,
                800: cursor_hash,
                872: safe_hash,
            }[number]
            rpc.get_logs.return_value = []
            with (
                patch.object(MONITOR, "CastKeccak", return_value=Mock()),
                patch.object(MONITOR, "anchor_snapshot", return_value={}),
                patch.object(MONITOR, "query_domains", return_value=({}, [])),
                patch.object(MONITOR, "append_alert_log") as append_alert,
                patch.object(MONITOR, "atomic_write_json") as write_state,
            ):
                with self.assertRaisesRegex(MONITOR.MonitorError, "1 missing"):
                    MONITOR.execute_check(
                        rpc,
                        state_path,
                        Path(directory) / "alerts.jsonl",
                        confirmations=128,
                        max_log_span=1_000,
                    )
            append_alert.assert_not_called()
            write_state.assert_not_called()
            self.assertEqual(state_path.read_text(encoding="utf-8"), original)

    def test_state_write_failure_leaves_alert_durable_and_old_state(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            state_path = Path(directory) / "state.json"
            alert_path = Path(directory) / "alerts.jsonl"
            original = '{"schema_version": 1, "cursor": "old"}'
            state_path.write_text(original, encoding="utf-8")
            rpc = Mock()
            rpc.block_number.return_value = 1_000
            result = {"coverage_ok": True, "status": "alert", "alerts": [{"type": "signal"}]}
            with (
                patch.object(MONITOR, "CastKeccak", return_value=Mock()),
                patch.object(MONITOR, "check_state", return_value=({"cursor": "new"}, result)),
                patch.object(MONITOR, "atomic_write_json", side_effect=OSError("rename failed")),
            ):
                with self.assertRaisesRegex(OSError, "rename failed"):
                    MONITOR.execute_check(
                        rpc,
                        state_path,
                        alert_path,
                        confirmations=128,
                        max_log_span=1_000,
                    )
            self.assertEqual(state_path.read_text(encoding="utf-8"), original)
            persisted = alert_path.read_text(encoding="utf-8")
            self.assertIn('"type": "signal"', persisted)


if __name__ == "__main__":
    unittest.main()
