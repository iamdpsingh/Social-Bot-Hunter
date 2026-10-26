import unittest
from datetime import UTC, datetime

from sbh.contracts.adapter import AccessOutcome, NotConfiguredAdapter
from sbh.contracts.capabilities import (
    Capability,
    CapabilityRegistry,
    CapabilityStatus,
    CollectionMode,
    Operation,
    default_registry,
)
from sbh.contracts.platforms import Platform
from sbh.schemas.records import ListKind


def cap(**kw):
    base = dict(platform=Platform.X, operation=Operation.LIST_FOLLOWERS, status=CapabilityStatus.NOT_CONFIGURED,
                mode=CollectionMode.OFFICIAL_API)
    base.update(kw)
    return Capability(**base)


class CapabilityRules(unittest.TestCase):
    def test_verified_requires_real_evidence(self):
        with self.assertRaises(ValueError):
            cap(status=CapabilityStatus.VERIFIED, supported=True, endpoint="e", api_version="v1")
        with self.assertRaises(ValueError):
            cap(status=CapabilityStatus.VERIFIED, supported=True, endpoint="e", api_version="v1",
                last_verified_at=datetime(2026, 1, 1, tzinfo=UTC))  # no evidence reference
        ok = cap(status=CapabilityStatus.VERIFIED, supported=True, endpoint="e", api_version="v1",
                 last_verified_at=datetime(2026, 1, 1, tzinfo=UTC), verification_evidence="integration run #1")
        self.assertEqual(ok.status, CapabilityStatus.VERIFIED)

    def test_implemented_api_operation_must_name_endpoint_and_version(self):
        with self.assertRaises(ValueError):
            cap(status=CapabilityStatus.IMPLEMENTED, supported=True)

    def test_unsupported_contradiction_rejected(self):
        with self.assertRaises(ValueError):
            cap(status=CapabilityStatus.UNSUPPORTED, supported=True)

    def test_duplicate_registration_rejected(self):
        with self.assertRaises(ValueError):
            CapabilityRegistry([cap(), cap()])


class DefaultRegistry(unittest.TestCase):
    def setUp(self):
        self.reg = default_registry()

    def test_every_platform_has_all_operations(self):
        self.assertEqual(len(self.reg.all()), len(Platform) * len(Operation))

    def test_nothing_live_is_claimed_verified_or_implemented(self):
        for c in self.reg.all():
            if c.mode is CollectionMode.OFFICIAL_API:
                self.assertEqual(c.status, CapabilityStatus.NOT_CONFIGURED, c)
                self.assertIsNone(c.supported)  # unknown, not "yes"
                self.assertIsNone(c.endpoint)   # no invented endpoints
                self.assertIsNone(c.last_verified_at)
            self.assertNotEqual(c.status, CapabilityStatus.VERIFIED)

    def test_dataset_import_is_available_for_every_platform(self):
        for p in Platform:
            ok, _ = self.reg.can_collect(p, Operation.DATASET_IMPORT)
            self.assertTrue(ok)

    def test_live_collection_is_refused_with_a_reason(self):
        ok, why = self.reg.can_collect(Platform.INSTAGRAM, Operation.LIST_FOLLOWERS)
        self.assertFalse(ok)
        self.assertIn("not_configured", why)


class AdapterContract(unittest.TestCase):
    def test_unconfigured_adapter_reports_unavailable_never_empty_success(self):
        a = NotConfiguredAdapter(Platform.TIKTOK)
        pages = [a.lookup_account("1"), a.list_relationships("1", ListKind.FOLLOWERS), a.list_content("1")]
        for page in pages:
            self.assertEqual(page.outcome, AccessOutcome.NOT_CONFIGURED)
            self.assertEqual(len(page.items), 0)
            self.assertIn("tiktok", page.limitation)
        self.assertTrue(all(c.status is CapabilityStatus.NOT_CONFIGURED for c in a.capabilities()))


if __name__ == "__main__":
    unittest.main()
