from __future__ import annotations

from dataclasses import asdict, dataclass

from .models import Host


@dataclass(frozen=True)
class DecommissionPlan:
    host: str
    ready: bool
    blockers: tuple[str, ...]
    steps: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def create_plan(host: Host) -> DecommissionPlan:
    blockers: list[str] = []

    if host.environment == "production":
        blockers.append("Production hosts require a separate reviewed change process.")
    if not host.approved_for_decommission:
        blockers.append("Business or technical owner approval is missing.")
    if host.dependencies:
        blockers.append(
            "Unresolved dependencies: " + ", ".join(sorted(host.dependencies)) + "."
        )
    if not host.backup_verified:
        blockers.append("Final backup or recovery evidence has not been verified.")

    steps = (
        "Capture the final inventory, owner approval, and change reference.",
        "Verify recovery evidence and required data-retention handling.",
        "Remove the host from traffic, scheduling, and service discovery.",
        "Silence monitoring only after traffic removal is confirmed.",
        "Revoke machine credentials, certificates, keys, and privileged access.",
        "Shut down the host for an observation window and validate service health.",
        "Delete compute, storage, DNS, backup, and monitoring resources as approved.",
        "Update inventory records and close the change with supporting evidence.",
    )

    return DecommissionPlan(
        host=host.name,
        ready=not blockers,
        blockers=tuple(blockers),
        steps=steps,
    )

