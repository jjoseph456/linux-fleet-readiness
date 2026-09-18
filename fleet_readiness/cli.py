from __future__ import annotations

import argparse
import json
import sys

from .audit import SEVERITY_ORDER, audit_hosts, meets_threshold
from .decommission import create_plan
from .models import InputError, load_inventory, load_policy


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fleet-readiness",
        description="Audit synthetic Linux inventory and plan safe decommissioning.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    audit = subparsers.add_parser("audit", help="Audit inventory against a policy.")
    audit.add_argument("inventory")
    audit.add_argument("--policy", required=True)
    audit.add_argument("--format", choices=("text", "json"), default="text")
    audit.add_argument(
        "--fail-on",
        choices=("none", "low", "medium", "high", "critical"),
        default="none",
    )

    decommission = subparsers.add_parser(
        "decommission", help="Create a guarded decommission plan."
    )
    decommission.add_argument("inventory")
    decommission.add_argument("--host", required=True)
    decommission.add_argument("--format", choices=("text", "json"), default="text")
    return parser


def _print_audit_text(host_count: int, findings: list[object]) -> None:
    print(f"Scanned {host_count} host(s); found {len(findings)} issue(s).")
    for finding in findings:
        print(f"\n[{finding.severity.upper()}] {finding.rule_id} {finding.host}")
        print(f"  {finding.message}")
        print(f"  Remediation: {finding.remediation}")


def _print_plan_text(plan: object) -> None:
    status = "READY" if plan.ready else "BLOCKED"
    print(f"Decommission plan for {plan.host}: {status}")
    if plan.blockers:
        print("\nBlockers:")
        for blocker in plan.blockers:
            print(f"- {blocker}")
    print("\nPlanned steps:")
    for index, step in enumerate(plan.steps, start=1):
        print(f"{index}. {step}")


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)

    try:
        hosts = load_inventory(args.inventory)

        if args.command == "audit":
            policy = load_policy(args.policy)
            findings = audit_hosts(hosts, policy)
            if args.format == "json":
                print(
                    json.dumps(
                        {
                            "host_count": len(hosts),
                            "finding_count": len(findings),
                            "findings": [item.as_dict() for item in findings],
                        },
                        indent=2,
                    )
                )
            else:
                _print_audit_text(len(hosts), findings)
            return 2 if meets_threshold(findings, args.fail_on) else 0

        host = next((item for item in hosts if item.name == args.host), None)
        if host is None:
            raise InputError(f"Host '{args.host}' was not found in the inventory.")
        plan = create_plan(host)
        if args.format == "json":
            print(json.dumps(plan.as_dict(), indent=2))
        else:
            _print_plan_text(plan)
        return 0 if plan.ready else 2

    except InputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

