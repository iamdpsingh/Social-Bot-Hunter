"""Tests for SignalManager lifecycle and shutdown triggers."""

from __future__ import annotations

import unittest

from sbh.runtime.signals import SignalManager


class TestSignalManager(unittest.TestCase):
    def setUp(self) -> None:
        self.sm = SignalManager.get_instance()
        self.sm.reset_for_testing()

    def tearDown(self) -> None:
        self.sm.reset_for_testing()

    def test_shutdown_trigger_and_state(self) -> None:
        self.assertFalse(self.sm.is_shutting_down())
        self.sm.trigger_shutdown()
        self.assertTrue(self.sm.is_shutting_down())

    def test_shutdown_hook_execution(self) -> None:
        hook_ran = []

        def hook_one() -> None:
            hook_ran.append(1)

        def hook_two() -> None:
            hook_ran.append(2)

        self.sm.register_shutdown_hook(hook_one)
        self.sm.register_shutdown_hook(hook_two)

        self.sm.trigger_shutdown()
        # Executed in reverse order: hook_two, then hook_one
        self.assertEqual(hook_ran, [2, 1])


if __name__ == "__main__":
    unittest.main()
