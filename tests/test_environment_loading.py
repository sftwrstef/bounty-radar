from __future__ import annotations

import unittest
from unittest.mock import call, patch

from bounty_radar import config


class EnvironmentLoadingTests(unittest.TestCase):
    def test_default_paths_follow_the_restored_project_location(self) -> None:
        self.assertEqual(config.DEFAULT_ENV_FILES[0], str(config.PROJECT_ROOT / ".env"))
        self.assertEqual(
            config.DEFAULT_ENV_FILES[1],
            str(config.VESPER_ROOT / ".env.audit-notify"),
        )
        self.assertEqual(
            config.DEFAULT_ENV_FILES[4],
            str(config.USER_HOME / "Code" / "Polymarket" / ".env"),
        )

    def test_default_chain_skips_unreadable_optional_env_files(self) -> None:
        with patch.object(
            config,
            "DEFAULT_ENV_FILES",
            ("first.env", "offloaded.env", "telegram.env"),
        ), patch.object(
            config,
            "load_dotenv",
            side_effect=[None, TimeoutError("offloaded"), None],
        ) as load:
            config.load_environment()

        self.assertEqual(
            load.call_args_list,
            [
                call("first.env", override=False),
                call("offloaded.env", override=False),
                call("telegram.env", override=False),
            ],
        )

    def test_explicit_env_file_still_fails_loudly(self) -> None:
        with patch.object(
            config,
            "load_dotenv",
            side_effect=TimeoutError("offloaded"),
        ):
            with self.assertRaises(TimeoutError):
                config.load_environment("explicit.env")


if __name__ == "__main__":
    unittest.main()
