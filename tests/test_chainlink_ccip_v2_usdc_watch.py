from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock


MODULE_PATH = Path(__file__).resolve().parents[1] / "monitors/chainlink_ccip_v2_usdc.py"
SPEC = importlib.util.spec_from_file_location("chainlink_ccip_v2_usdc", MODULE_PATH)
assert SPEC and SPEC.loader
watch = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(watch)


def token_config(pool: str, version: str = watch.PROXY_VERSION) -> dict:
    return {"poolAddress": pool, "typeAndVersion": version}


def lane(
    *,
    version: str = "2.0.0",
    usdc: bool = True,
    enabled: bool = True,
    on_ramp: str = "0x01",
    off_ramp: str = "0x02",
) -> dict:
    supported = {}
    if usdc:
        supported["USDC"] = {
            "rateLimiterConfig": {
                "in": {"isEnabled": enabled, "capacity": "100000000" if enabled else "0", "rate": "1"}
            }
        }
    return {
        "onRamp": {"address": on_ramp, "version": version},
        "offRamp": {"address": off_ramp, "version": version},
        "supportedTokens": supported,
    }


def route_lanes(
    *,
    version: str = "2.0.0",
    usdc: bool = True,
    enabled: bool = True,
    on_ramp: str = "0x01",
    source_side_off_ramp: str = "0x02",
    destination_off_ramp: str = "0x04",
    destination_off_ramp_version: str = "2.0.0",
) -> dict:
    reverse = lane(
        usdc=False,
        on_ramp="0x03",
        off_ramp=destination_off_ramp,
    )
    reverse["offRamp"]["version"] = destination_off_ramp_version
    return {
        "source": {
            "dest": lane(
                version=version,
                usdc=usdc,
                enabled=enabled,
                on_ramp=on_ramp,
                off_ramp=source_side_off_ramp,
            )
        },
        "dest": {"source": reverse},
    }


class ChainlinkCCIPV2USDCWatchTests(unittest.TestCase):
    def test_default_alert_environment_follows_monitor_location(self) -> None:
        self.assertEqual(watch.FALLBACK_ENV_FILES[0], MODULE_PATH.parents[2] / ".env.audit-notify")
        self.assertEqual(
            watch.FALLBACK_ENV_FILES[2],
            Path.home() / "Code" / "Vesper" / ".env.audit-notify",
        )

    def test_default_alert_environment_uses_shared_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fallback = root / ".env.audit-notify"
            fallback.write_text(
                "TELEGRAM_BOT_TOKEN=test-token\nTELEGRAM_CHAT_ID=test-chat\n",
                encoding="utf-8",
            )
            with (
                mock.patch.object(watch, "FALLBACK_ENV_FILES", (fallback,)),
                mock.patch.dict(os.environ, {}, clear=True),
            ):
                loaded = watch._load_alert_environment(None, root / "radar")
                self.assertTrue(loaded)
                self.assertEqual(os.environ["TELEGRAM_BOT_TOKEN"], "test-token")
                self.assertEqual(os.environ["TELEGRAM_CHAT_ID"], "test-chat")

    def test_zero_match_ignores_v2_non_usdc_and_v1_usdc(self) -> None:
        lanes = {"source": {"dest-a": lane(usdc=False), "dest-b": lane(version="1.6.0")}}
        tokens = {"USDC": {"source": token_config("0xa"), "dest-b": token_config("0xb")}}
        self.assertEqual(watch.find_v2_usdc_lanes(lanes, tokens), [])

    def test_v2_usdc_lane_is_annotated_as_proxy_candidate(self) -> None:
        lanes = route_lanes()
        tokens = {"USDC": {"source": token_config("0xa"), "dest": token_config("0xb")}}
        matches = watch.find_v2_usdc_lanes(lanes, tokens)
        self.assertEqual(len(matches), 1)
        self.assertTrue(matches[0]["proxy_candidate"])
        self.assertTrue(matches[0]["inbound_rate_limit_enabled"])
        self.assertEqual(matches[0]["inbound_capacity"], "100000000")
        self.assertEqual(matches[0]["id"], "source|dest")
        self.assertEqual(matches[0]["deployment_id"], "source|dest|0x01|0x04")
        self.assertEqual(matches[0]["off_ramp"], "0x04")
        self.assertEqual(matches[0]["source_side_off_ramp"], "0x02")

    def test_route_requires_destination_off_ramp_from_reverse_entry(self) -> None:
        tokens = {"USDC": {"source": token_config("0xa"), "dest": token_config("0xb")}}
        self.assertEqual(
            watch.find_v2_usdc_lanes({"source": {"dest": lane()}}, tokens),
            [],
        )
        self.assertEqual(
            watch.find_v2_usdc_lanes(
                route_lanes(destination_off_ramp_version="1.6.0"), tokens
            ),
            [],
        )

    def test_source_side_reverse_off_ramp_version_does_not_define_route_version(self) -> None:
        lanes = route_lanes()
        lanes["source"]["dest"]["offRamp"]["version"] = "1.6.0"
        tokens = {"USDC": {"source": token_config("0xa"), "dest": token_config("0xb")}}
        matches = watch.find_v2_usdc_lanes(lanes, tokens)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["off_ramp"], "0x04")

    def test_new_route_requests_onchain_check_once(self) -> None:
        current = watch.find_v2_usdc_lanes(
            route_lanes(),
            {"USDC": {"source": token_config("0xa"), "dest": token_config("0xb")}},
        )
        first = watch.diff_matches({}, current)
        self.assertEqual(first[0]["change_reason"], "new_v2_usdc_route")
        self.assertTrue(first[0]["onchain_reopen_check"])
        previous = {"lanes": {item["id"]: item for item in current}}
        self.assertEqual(watch.diff_matches(previous, current), [])

    def test_ramp_rotation_is_confirmation_only(self) -> None:
        tokens = {"USDC": {"source": token_config("0xa"), "dest": token_config("0xb")}}
        before = watch.find_v2_usdc_lanes(route_lanes(), tokens)
        after = watch.find_v2_usdc_lanes(route_lanes(on_ramp="0x05"), tokens)
        previous = {"lanes": {item["id"]: item for item in before}}
        changes = watch.diff_matches(previous, after)
        self.assertEqual(changes[0]["change_reason"], "ramp_changed_confirmation_only")
        self.assertFalse(changes[0]["onchain_reopen_check"])

    def test_legacy_deployment_key_does_not_create_a_new_route(self) -> None:
        tokens = {"USDC": {"source": token_config("0xa"), "dest": token_config("0xb")}}
        current = watch.find_v2_usdc_lanes(route_lanes(), tokens)
        legacy_key = "source|dest|0x01|0x02"
        previous = {"lanes": {legacy_key: current[0]}}
        self.assertEqual(watch.diff_matches(previous, current), [])

    def test_legacy_deployment_key_rotation_is_not_a_new_route(self) -> None:
        tokens = {"USDC": {"source": token_config("0xa"), "dest": token_config("0xb")}}
        before = watch.find_v2_usdc_lanes(route_lanes(), tokens)[0]
        after = watch.find_v2_usdc_lanes(route_lanes(on_ramp="0x05"), tokens)
        previous = {"lanes": {"source|dest|0x01|0x02": before}}
        changes = watch.diff_matches(previous, after)
        self.assertEqual(changes[0]["change_reason"], "ramp_changed_confirmation_only")
        self.assertFalse(changes[0]["onchain_reopen_check"])

    def test_legacy_source_side_off_ramp_state_migrates_without_false_delta(self) -> None:
        tokens = {"USDC": {"source": token_config("0xa"), "dest": token_config("0xb")}}
        current = watch.find_v2_usdc_lanes(route_lanes(), tokens)
        legacy = dict(current[0])
        legacy["off_ramp"] = legacy.pop("source_side_off_ramp")
        legacy["deployment_id"] = "source|dest|0x01|0x02"
        previous = {"lanes": {legacy["deployment_id"]: legacy}}
        self.assertEqual(watch.diff_matches(previous, current), [])

    def test_legacy_pending_check_off_ramp_is_migrated_without_losing_history(self) -> None:
        tokens = {"USDC": {"source": token_config("0xa"), "dest": token_config("0xb")}}
        current = watch.find_v2_usdc_lanes(route_lanes(), tokens)
        previous = {
            "reopen_checks": {
                "source|dest": {
                    "route_id": "source|dest",
                    "status": "pending",
                    "trigger_count": 3,
                    "off_ramp": "0x02",
                }
            }
        }
        checks = watch.update_reopen_checks(
            previous,
            [],
            "2026-09-12T00:00:00+00:00",
            current=current,
        )
        self.assertEqual(checks["source|dest"]["off_ramp"], "0x04")
        self.assertEqual(checks["source|dest"]["source_side_off_ramp"], "0x02")
        self.assertEqual(checks["source|dest"]["trigger_count"], 3)
        self.assertEqual(checks["source|dest"]["status"], "pending")

    def test_destination_off_ramp_rotation_is_confirmation_only(self) -> None:
        tokens = {"USDC": {"source": token_config("0xa"), "dest": token_config("0xb")}}
        before = watch.find_v2_usdc_lanes(route_lanes(), tokens)
        after = watch.find_v2_usdc_lanes(
            route_lanes(destination_off_ramp="0x06"), tokens
        )
        previous = {"lanes": {item["id"]: item for item in before}}
        changes = watch.diff_matches(previous, after)
        self.assertEqual(changes[0]["change_reason"], "ramp_changed_confirmation_only")
        self.assertFalse(changes[0]["onchain_reopen_check"])

    def test_rate_limit_activation_is_a_fresh_actionable_delta(self) -> None:
        tokens = {"USDC": {"source": token_config("0xa"), "dest": token_config("0xb")}}
        disabled = watch.find_v2_usdc_lanes(route_lanes(enabled=False), tokens)
        enabled = watch.find_v2_usdc_lanes(route_lanes(enabled=True), tokens)
        previous = {"lanes": {item["id"]: item for item in disabled}}
        changes = watch.diff_matches(previous, enabled)
        self.assertEqual(changes[0]["change_reason"], "inbound_rate_limit_activated")
        self.assertTrue(changes[0]["onchain_reopen_check"])

    def test_alert_wording_is_evidence_gated(self) -> None:
        current = watch.find_v2_usdc_lanes(
            route_lanes(),
            {"USDC": {"source": token_config("0xa"), "dest": token_config("0xb")}},
        )
        change = {
            **current[0],
            "change_reason": "ramp_changed_confirmation_only",
            "onchain_reopen_check": False,
        }
        alert = watch._format_alert([change])
        self.assertNotIn("Reopen the parked USDC migration rate-limit candidate now", alert)
        self.assertIn("This is a confirmation signal, not an automatic reopen", alert)
        self.assertIn("Onchain reopen check: NO - ramp-only confirmation", alert)
        self.assertIn("a nonzero siloed lock/release child plus a mechanism transition", alert)
        self.assertIn("destination OffRamp acceptance onchain", alert)

    def test_actionable_change_remains_pending_after_route_is_deduplicated(self) -> None:
        current = watch.find_v2_usdc_lanes(
            route_lanes(),
            {"USDC": {"source": token_config("0xa"), "dest": token_config("0xb")}},
        )
        changes = watch.diff_matches({}, current)
        checks = watch.update_reopen_checks({}, changes, "2026-09-11T00:00:00+00:00")
        previous = {"lanes": {item["id"]: item for item in current}, "reopen_checks": checks}

        self.assertEqual(watch.diff_matches(previous, current), [])
        carried = watch.update_reopen_checks(previous, [], "2026-09-12T00:00:00+00:00")
        self.assertEqual(len(watch.pending_reopen_checks(carried)), 1)
        self.assertEqual(carried["source|dest"]["trigger_count"], 1)

    def test_pending_check_requires_explicit_resolution(self) -> None:
        change = {
            **watch.find_v2_usdc_lanes(
                route_lanes(),
                {"USDC": {"source": token_config("0xa"), "dest": token_config("0xb")}},
            )[0],
            "change_reason": "new_v2_usdc_route",
            "onchain_reopen_check": True,
        }
        previous = {
            "reopen_checks": watch.update_reopen_checks(
                {}, [change], "2026-09-11T00:00:00+00:00"
            )
        }
        resolved = watch.resolve_reopen_check(
            previous,
            "source|dest",
            "RE-PARK",
            "CCV only; no siloed child",
            "2026-09-12T00:00:00+00:00",
        )
        self.assertEqual(watch.pending_reopen_checks(resolved), [])
        self.assertEqual(resolved["source|dest"]["resolution"], "RE-PARK")
        self.assertEqual(resolved["source|dest"]["resolution_note"], "CCV only; no siloed child")

    def test_state_round_trip_preserves_reopen_checks(self) -> None:
        current = watch.find_v2_usdc_lanes(
            route_lanes(),
            {"USDC": {"source": token_config("0xa"), "dest": token_config("0xb")}},
        )
        checks = watch.update_reopen_checks(
            {}, watch.diff_matches({}, current), "2026-09-11T00:00:00+00:00"
        )
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory) / "state.json"
            watch._write_state(state, current, "2026-09-11T00:00:00+00:00", checks)
            loaded = watch._load_state(state)
        self.assertEqual(loaded["reopen_checks"], checks)


if __name__ == "__main__":
    unittest.main()
