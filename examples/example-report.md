# Example Fleet Readiness Report

Command:

```bash
fleet-readiness audit examples/inventory.json --policy examples/policy.json
```

Output:

```text
Scanned 3 host(s); found 6 issue(s).

[HIGH] FLT001 legacy-test-03
  Patch age is 95 days; policy maximum is 30 days.
  Remediation: Schedule and validate an approved patch window.

[HIGH] FLT004 legacy-test-03
  Storage encryption is disabled.
  Remediation: Migrate data to encrypted storage using an approved plan.

[HIGH] FLT001 web-prod-01
  Patch age is 58 days; policy maximum is 30 days.
  Remediation: Schedule and validate an approved patch window.

[HIGH] FLT002 web-prod-01
  Production host has no verified backup.
  Remediation: Complete and test a backup before operational changes.

[MEDIUM] FLT003 legacy-test-03
  Monitoring is disabled.
  Remediation: Enroll the host in the standard monitoring baseline.

[MEDIUM] FLT005 legacy-test-03
  OS family 'legacy-linux' is outside policy support.
  Remediation: Upgrade, migrate, or approve a documented exception.
```

All hosts, owners, dependencies, and policy values are synthetic.

