from __future__ import annotations

from dataclasses import asdict, dataclass

from .models import Host, Policy


SEVERITY_ORDER = {"low": 1, "medium": 2, "high": 3, "critical": 4}


@dataclass(frozen=True)
class Finding:
    rule_id: str
    severity: str
    host: str
    message: str
    remediation: str

    def as_dict(self) -> dict[str, str]:
        return asdict(self)


def audit_hosts(hosts: list[Host], policy: Policy) -> list[Finding]:
    findings: list[Finding] = []

    for host in hosts:
        if host.patch_age_days > policy.max_patch_age_days:
            findings.append(
                Finding(
                    rule_id="FLT001",
                    severity="high",
                    host=host.name,
                    message=(
                        f"Patch age is {host.patch_age_days} days; policy maximum "
                        f"is {policy.max_patch_age_days} days."
                    ),
                    remediation="Schedule and validate an approved patch window.",
                )
            )

        if host.environment == "production" and not host.backup_verified:
            findings.append(
                Finding(
                    rule_id="FLT002",
                    severity="high",
                    host=host.name,
                    message="Production host has no verified backup.",
                    remediation="Complete and test a backup before operational changes.",
                )
            )

        if not host.monitoring_enabled:
            findings.append(
                Finding(
                    rule_id="FLT003",
                    severity="medium",
                    host=host.name,
                    message="Monitoring is disabled.",
                    remediation="Enroll the host in the standard monitoring baseline.",
                )
            )

        if not host.encryption_enabled:
            findings.append(
                Finding(
                    rule_id="FLT004",
                    severity="high",
                    host=host.name,
                    message="Storage encryption is disabled.",
                    remediation="Migrate data to encrypted storage using an approved plan.",
                )
            )

        if host.os_family not in policy.supported_os_families:
            findings.append(
                Finding(
                    rule_id="FLT005",
                    severity="medium",
                    host=host.name,
                    message=f"OS family '{host.os_family}' is outside policy support.",
                    remediation="Upgrade, migrate, or approve a documented exception.",
                )
            )

    return sorted(
        findings,
        key=lambda item: (-SEVERITY_ORDER[item.severity], item.host, item.rule_id),
    )


def meets_threshold(findings: list[Finding], threshold: str) -> bool:
    if threshold == "none":
        return False
    minimum = SEVERITY_ORDER[threshold]
    return any(SEVERITY_ORDER[item.severity] >= minimum for item in findings)

