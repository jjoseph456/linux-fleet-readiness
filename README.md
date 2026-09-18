# Linux Fleet Readiness

[![Test](https://github.com/jjoseph456/linux-fleet-readiness/actions/workflows/test.yml/badge.svg)](https://github.com/jjoseph456/linux-fleet-readiness/actions/workflows/test.yml)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A dependency-free Python CLI that reviews synthetic Linux server inventory for
operational risk and produces guarded decommission plans. It demonstrates how
I turn infrastructure operations experience into repeatable, testable tooling.

> This is a clean-room personal project. It contains no employer source code,
> hostnames, credentials, customer information, internal procedures, ticket
> data, or proprietary configuration. Every server, policy, and workflow in
> this repository is fictional.

## Why This Project

Infrastructure teams need consistent answers to two recurring questions:

1. Which hosts need attention before they become operational or security risk?
2. Is a host actually ready to be decommissioned without disrupting a service?

`fleet-readiness` converts those questions into explicit validation, audit
rules, machine-readable output, and safety gates. It plans actions but never
connects to or changes a server.

## Capabilities

- Validates a JSON server inventory and policy file
- Flags overdue patching, missing monitoring, unverified backups, missing
  encryption, and unsupported operating-system families
- Sorts findings by severity and supports CI-friendly failure thresholds
- Blocks decommission plans when approvals, backups, or dependencies are
  unresolved
- Produces human-readable and JSON output
- Uses only the Python standard library
- Includes synthetic examples and unit tests

## Quick Start

Requires Python 3.10 or later.

```bash
python -m pip install -e .
fleet-readiness audit examples/inventory.json --policy examples/policy.json
fleet-readiness decommission examples/inventory.json --host batch-dev-02
python -m unittest discover -s tests -v
```

You can also run the package without installing it:

```bash
python -m fleet_readiness audit examples/inventory.json \
  --policy examples/policy.json
```

## Audit Rules

| Rule | Severity | Condition |
| --- | --- | --- |
| `FLT001` | High | Patch age exceeds the configured maximum |
| `FLT002` | High | Production host has no verified backup |
| `FLT003` | Medium | Monitoring is disabled |
| `FLT004` | High | Storage encryption is disabled |
| `FLT005` | Medium | OS family is outside the supported policy |

Audit with JSON output and fail when a high-severity finding exists:

```bash
fleet-readiness audit examples/inventory.json \
  --policy examples/policy.json \
  --format json \
  --fail-on high
```

Exit codes:

| Code | Meaning |
| --- | --- |
| `0` | Command completed and no configured failure condition was met |
| `1` | Input or validation error |
| `2` | Audit threshold met or decommission plan blocked |

## Decommission Safety Gates

A host is blocked from decommissioning when:

- Business or technical owner approval is missing
- Service dependencies remain
- The final backup has not been verified
- The host is classified as production

For a ready synthetic host:

```bash
fleet-readiness decommission examples/inventory.json \
  --host batch-dev-02
```

The generated plan covers evidence capture, traffic removal, monitoring,
credential revocation, shutdown observation, resource deletion, and inventory
closure. It remains a plan; this project deliberately performs no destructive
operations.

## Example Audit Output

```text
Scanned 3 host(s); found 6 issue(s).

[HIGH] FLT001 web-prod-01
  Patch age is 58 days; policy maximum is 30 days.
  Remediation: Schedule and validate an approved patch window.

[MEDIUM] FLT003 legacy-test-03
  Monitoring is disabled.
  Remediation: Enroll the host in the standard monitoring baseline.
```

See the [complete example report](examples/example-report.md).

## Engineering Decisions

- **Read-only by design:** portfolio software should not make destructive
  infrastructure changes.
- **Explicit schema validation:** malformed or ambiguous inventory fails
  visibly instead of producing a success-shaped report.
- **Synthetic examples:** the repository demonstrates method and judgment
  without exposing operational details from past employers.
- **No runtime dependencies:** reviewers can run the CLI and tests with a
  standard Python installation.
- **Separate evidence and action:** audit findings explain observed state;
  decommission plans express gates and proposed steps.

## Repository Structure

```text
.
|-- docs/
|   |-- career-context.md
|   `-- sanitization.md
|-- examples/
|   |-- example-report.md
|   |-- inventory.json
|   `-- policy.json
|-- fleet_readiness/
|   |-- __init__.py
|   |-- __main__.py
|   |-- audit.py
|   |-- cli.py
|   |-- decommission.py
|   `-- models.py
|-- tests/
|   `-- test_fleet_readiness.py
|-- LICENSE
|-- README.md
`-- pyproject.toml
```

## Limitations

- Inventory is file-based; the tool does not query cloud, hypervisor, CMDB, or
  configuration-management APIs.
- Rules are readiness signals, not proof of compliance.
- Production decommissioning is intentionally blocked.
- Real workflows require organization-specific approvals, retention rules,
  recovery testing, and change-management controls.
