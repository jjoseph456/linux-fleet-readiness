from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from fleet_readiness.audit import audit_hosts, meets_threshold
from fleet_readiness.decommission import create_plan
from fleet_readiness.models import Host, InputError, Policy, load_inventory


def host(**overrides: object) -> Host:
    values: dict[str, object] = {
        "name": "test-host-01",
        "environment": "test",
        "owner": "platform-team",
        "os_family": "rhel",
        "patch_age_days": 10,
        "monitoring_enabled": True,
        "backup_verified": True,
        "encryption_enabled": True,
        "dependencies": (),
        "approved_for_decommission": True,
    }
    values.update(overrides)
    return Host(**values)


class AuditTests(unittest.TestCase):
    def setUp(self) -> None:
        self.policy = Policy(
            max_patch_age_days=30,
            supported_os_families=("rhel", "ubuntu", "suse"),
        )

    def test_compliant_host_has_no_findings(self) -> None:
        self.assertEqual(audit_hosts([host()], self.policy), [])

    def test_risky_host_reports_expected_rules(self) -> None:
        risky = host(
            environment="production",
            patch_age_days=45,
            monitoring_enabled=False,
            backup_verified=False,
            encryption_enabled=False,
            os_family="legacy-linux",
        )
        rules = {item.rule_id for item in audit_hosts([risky], self.policy)}
        self.assertEqual(rules, {"FLT001", "FLT002", "FLT003", "FLT004", "FLT005"})

    def test_failure_threshold_uses_severity_order(self) -> None:
        findings = audit_hosts([host(monitoring_enabled=False)], self.policy)
        self.assertTrue(meets_threshold(findings, "medium"))
        self.assertFalse(meets_threshold(findings, "high"))
        self.assertFalse(meets_threshold(findings, "none"))


class DecommissionTests(unittest.TestCase):
    def test_ready_host_produces_plan(self) -> None:
        plan = create_plan(host())
        self.assertTrue(plan.ready)
        self.assertEqual(plan.blockers, ())
        self.assertGreaterEqual(len(plan.steps), 6)

    def test_dependencies_and_missing_approval_block_plan(self) -> None:
        plan = create_plan(
            host(
                dependencies=("reporting-service",),
                approved_for_decommission=False,
            )
        )
        self.assertFalse(plan.ready)
        self.assertEqual(len(plan.blockers), 2)

    def test_production_is_always_blocked(self) -> None:
        plan = create_plan(host(environment="production"))
        self.assertFalse(plan.ready)
        self.assertIn("Production hosts", plan.blockers[0])


class ValidationTests(unittest.TestCase):
    def test_duplicate_host_names_fail_validation(self) -> None:
        record = {
            "name": "duplicate-01",
            "environment": "test",
            "owner": "platform-team",
            "os_family": "rhel",
            "patch_age_days": 1,
            "monitoring_enabled": True,
            "backup_verified": True,
            "encryption_enabled": True,
            "dependencies": [],
            "approved_for_decommission": False,
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "inventory.json"
            path.write_text(
                json.dumps({"hosts": [record, record]}),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(InputError, "Duplicate host name"):
                load_inventory(path)


if __name__ == "__main__":
    unittest.main()

