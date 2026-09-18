from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any


class InputError(ValueError):
    """Raised when an inventory or policy file is invalid."""


@dataclass(frozen=True)
class Host:
    name: str
    environment: str
    owner: str
    os_family: str
    patch_age_days: int
    monitoring_enabled: bool
    backup_verified: bool
    encryption_enabled: bool
    dependencies: tuple[str, ...]
    approved_for_decommission: bool


@dataclass(frozen=True)
class Policy:
    max_patch_age_days: int
    supported_os_families: tuple[str, ...]


def _load_json(path: str | Path) -> Any:
    source = Path(path)
    try:
        return json.loads(source.read_text(encoding="utf-8"))
    except OSError as exc:
        raise InputError(f"Unable to read {source}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise InputError(
            f"Invalid JSON in {source} at line {exc.lineno}, column {exc.colno}."
        ) from exc


def _required(record: dict[str, Any], key: str, expected: type, context: str) -> Any:
    if key not in record:
        raise InputError(f"{context} is missing required field '{key}'.")
    value = record[key]
    if expected is int and isinstance(value, bool):
        raise InputError(f"{context}.{key} must be an integer.")
    if not isinstance(value, expected):
        raise InputError(f"{context}.{key} must be {expected.__name__}.")
    return value


def load_inventory(path: str | Path) -> list[Host]:
    document = _load_json(path)
    if not isinstance(document, dict) or not isinstance(document.get("hosts"), list):
        raise InputError("Inventory must be an object containing a 'hosts' list.")

    hosts: list[Host] = []
    names: set[str] = set()
    allowed_environments = {"production", "staging", "development", "test"}

    for index, record in enumerate(document["hosts"]):
        context = f"hosts[{index}]"
        if not isinstance(record, dict):
            raise InputError(f"{context} must be an object.")

        name = _required(record, "name", str, context).strip()
        environment = _required(record, "environment", str, context).strip().lower()
        owner = _required(record, "owner", str, context).strip()
        os_family = _required(record, "os_family", str, context).strip().lower()
        patch_age_days = _required(record, "patch_age_days", int, context)
        monitoring = _required(record, "monitoring_enabled", bool, context)
        backup = _required(record, "backup_verified", bool, context)
        encryption = _required(record, "encryption_enabled", bool, context)
        approved = _required(record, "approved_for_decommission", bool, context)
        dependencies = _required(record, "dependencies", list, context)

        if not name:
            raise InputError(f"{context}.name cannot be empty.")
        if name in names:
            raise InputError(f"Duplicate host name '{name}'.")
        if environment not in allowed_environments:
            raise InputError(
                f"{context}.environment must be one of "
                f"{', '.join(sorted(allowed_environments))}."
            )
        if not owner:
            raise InputError(f"{context}.owner cannot be empty.")
        if not os_family:
            raise InputError(f"{context}.os_family cannot be empty.")
        if patch_age_days < 0:
            raise InputError(f"{context}.patch_age_days cannot be negative.")
        if not all(isinstance(item, str) and item.strip() for item in dependencies):
            raise InputError(f"{context}.dependencies must contain non-empty strings.")

        names.add(name)
        hosts.append(
            Host(
                name=name,
                environment=environment,
                owner=owner,
                os_family=os_family,
                patch_age_days=patch_age_days,
                monitoring_enabled=monitoring,
                backup_verified=backup,
                encryption_enabled=encryption,
                dependencies=tuple(item.strip() for item in dependencies),
                approved_for_decommission=approved,
            )
        )

    return hosts


def load_policy(path: str | Path) -> Policy:
    document = _load_json(path)
    if not isinstance(document, dict):
        raise InputError("Policy must be a JSON object.")

    max_patch_age = _required(document, "max_patch_age_days", int, "policy")
    supported = _required(document, "supported_os_families", list, "policy")

    if max_patch_age < 1:
        raise InputError("policy.max_patch_age_days must be at least 1.")
    if not supported or not all(
        isinstance(item, str) and item.strip() for item in supported
    ):
        raise InputError(
            "policy.supported_os_families must contain non-empty strings."
        )

    return Policy(
        max_patch_age_days=max_patch_age,
        supported_os_families=tuple(item.strip().lower() for item in supported),
    )

