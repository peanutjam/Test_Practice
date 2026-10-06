"""Resolve Microsoft Learn study URLs for AZ-900 question bank."""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from functools import lru_cache
from pathlib import Path

CATALOG_CACHE = Path(__file__).resolve().parent / ".learn-catalog.json"
CATALOG_URL = "https://learn.microsoft.com/api/learn/catalog?locale=en-us"
LEARN_PREFIX = "https://learn.microsoft.com/en-us/training/modules/"

# Retired module slugs -> current AZ-900 module slugs (same unit slug when possible).
MODULE_ALIASES: dict[str, str] = {
    "describe-monitoring-tools": "describe-monitoring-tools-azure",
    "describe-basic-security-features": "describe-azure-identity-access-security",
    "describe-cost-management": "describe-cost-management-azure",
    "describe-security-privacy-compliance-trust": "describe-azure-identity-access-security",
    "describe-azure-database-analytics-services": "explore-provision-deploy-relational-database-offerings-azure",
}

# Old unit slug (no numeric prefix) -> unit slug in the resolved module.
UNIT_ALIASES: dict[str, str] = {
    "describe-azure-portal": "describe-interacting-azure",
    "describe-azure-policy": "describe-purpose-of-azure-policy",
    "describe-azure-cloud-shell": "describe-interacting-azure",
    "describe-tags": "describe-purpose-of-tags",
    "describe-azure-cli": "describe-interacting-azure",
    "describe-azure-powershell": "describe-interacting-azure",
    "describe-resource-locks": "describe-purpose-of-resource-locks",
    "describe-cost-management": "describe-azure-tool",
    "describe-total-cost-ownership-calculator": "compare-pricing-total-cost-of-ownership-calculators",
    "describe-azure-active-directory": "directory-services",
    "describe-role-based-access-control": "role-based-access-control",
    "describe-multi-factor-authentication": "authentication-methods",
    "describe-defense-depth": "describe-defense-depth",
    "describe-azure-ddos-protection": "describe-azure-ddos-protection",
    "describe-azure-key-vault": "describe-encryption-key-management",
    "describe-azure-firewall": "describe-what-is-azure-firewall",
    "describe-compliance-offerings": "describe-purpose-of-service-trust-portal",
    "describe-azure-bastion": "describe-what-is-azure-bastion",
    "describe-azure-sql-database": "introduction",
    "describe-azure-cosmos-db": "introduction",
    "describe-azure-synapse-analytics": "introduction",
    "describe-storage-tiers": "describe-azure-storage-services",
    "describe-azure-table-storage": "describe-azure-storage-services",
    "describe-azure-queue-storage": "describe-azure-storage-services",
    "describe-azure-blob-storage": "describe-azure-storage-services",
    "describe-azure-files": "identify-azure-file-movement-options",
    "describe-azure-virtual-networks": "virtual-network",
    "describe-azure-dns": "domain-name-system",
    "describe-azure-expressroute": "expressroute",
    "describe-azure-content-delivery-network": "introduction",
    "describe-azure-load-balancer": "describe-application-hosting-options",
    "describe-azure-virtual-machines": "virtual-machines",
    "describe-azure-functions": "functions",
    "describe-azure-app-service": "describe-application-hosting-options",
    "describe-azure-kubernetes-service": "containers",
    "describe-availability-zones": "describe-azure-physical-infrastructure",
    "describe-regions": "describe-azure-physical-infrastructure",
    "describe-service-level-agreements": "describe-azure-physical-infrastructure",
    "describe-subscriptions": "describe-azure-management-infrastructure",
    "describe-azure-resource-manager": "describe-azure-resource-manager-azure-arm-templates",
    "describe-azure-advisor": "describe-purpose-of-azure-advisor",
    "describe-azure-monitor": "describe-azure-monitor",
    "describe-azure-service-health": "describe-azure-service-health",
    "describe-azure-well-architected-framework": "introduction",
    "describe-azure-arc": "describe-purpose-of-azure-arc",
    "describe-purpose-microsoft-purview": "describe-purpose-microsoft-purview",
}

# Units that moved to a different module than MODULE_ALIASES implies.
UNIT_RELOCATIONS: dict[str, tuple[str, str]] = {
    "describe-azure-bastion": (
        "describe-basic-security-capabilities-azure",
        "describe-what-is-azure-bastion",
    ),
    "describe-azure-ddos-protection": (
        "describe-basic-security-capabilities-azure",
        "describe-azure-ddos-protection",
    ),
    "describe-azure-firewall": (
        "describe-basic-security-capabilities-azure",
        "describe-what-is-azure-firewall",
    ),
    "describe-azure-policy": (
        "describe-features-tools-azure-for-governance-compliance",
        "describe-purpose-of-azure-policy",
    ),
    "describe-resource-locks": (
        "describe-features-tools-azure-for-governance-compliance",
        "describe-purpose-of-resource-locks",
    ),
    "describe-compliance-offerings": (
        "describe-features-tools-azure-for-governance-compliance",
        "describe-purpose-of-service-trust-portal",
    ),
    "describe-tags": (
        "describe-cost-management-azure",
        "describe-purpose-of-tags",
    ),
    "describe-azure-resource-manager": (
        "describe-features-tools-manage-deploy-azure-resources",
        "describe-azure-resource-manager-azure-arm-templates",
    ),
    "describe-azure-portal": (
        "describe-features-tools-manage-deploy-azure-resources",
        "describe-interacting-azure",
    ),
    "describe-azure-cloud-shell": (
        "describe-features-tools-manage-deploy-azure-resources",
        "describe-interacting-azure",
    ),
    "describe-azure-cli": (
        "describe-features-tools-manage-deploy-azure-resources",
        "describe-interacting-azure",
    ),
    "describe-azure-powershell": (
        "describe-features-tools-manage-deploy-azure-resources",
        "describe-interacting-azure",
    ),
    "describe-azure-cosmos-db": (
        "explore-non-relational-data-stores-azure",
        "introduction",
    ),
    "describe-azure-virtual-networks": (
        "describe-azure-networking-services",
        "virtual-network",
    ),
    "describe-azure-dns": (
        "describe-azure-networking-services",
        "domain-name-system",
    ),
    "describe-azure-expressroute": (
        "describe-azure-networking-services",
        "expressroute",
    ),
    "describe-azure-content-delivery-network": (
        "describe-azure-networking-services",
        "introduction",
    ),
}

# Full old URLs that should map to a specific module+unit (highest priority).
EXACT_REDIRECTS: dict[str, str] = {
    "https://learn.microsoft.com/en-us/training/modules/describe-azure-database-analytics-services/3-describe-azure-cosmos-db": (
        f"{LEARN_PREFIX}explore-non-relational-data-stores-azure/1-introduction"
    ),
    "https://learn.microsoft.com/en-us/training/paths/az-900-describe-cloud-concepts/": (
        "https://learn.microsoft.com/en-us/training/paths/microsoft-azure-fundamentals-describe-cloud-concepts/"
    ),
}


def _load_catalog() -> dict:
    if not CATALOG_CACHE.exists():
        data = urllib.request.urlopen(CATALOG_URL, timeout=120).read()
        CATALOG_CACHE.write_bytes(data)
    return json.loads(CATALOG_CACHE.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _modules_by_slug() -> dict[str, dict]:
    raw = _load_catalog()
    out: dict[str, dict] = {}
    for module in raw.get("modules", []):
        uid = module.get("uid", "")
        if uid.startswith("learn.wwl."):
            out[uid[len("learn.wwl.") :]] = module
    return out


def _unit_url(module_slug: str, unit_slug: str) -> str | None:
    overrides = _load_overrides()
    key = f"{module_slug}/{unit_slug}"
    if key in overrides:
        return overrides[key]

    module = _modules_by_slug().get(module_slug)
    if not module:
        return None
    for index, uid in enumerate(module.get("units") or [], start=1):
        if uid.endswith("." + unit_slug):
            return f"{LEARN_PREFIX}{module_slug}/{index}-{unit_slug}"
    return None


@lru_cache(maxsize=1)
def _load_overrides() -> dict[str, str]:
    path = Path(__file__).resolve().parent / "learn_url_overrides.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _module_url(module_slug: str) -> str:
    module = _modules_by_slug().get(module_slug)
    if module and module.get("url"):
        return module["url"].split("?")[0].rstrip("/") + "/"
    return f"{LEARN_PREFIX}{module_slug}/"


def resolve_study_url(url: str) -> str:
    normalized = url.split("?")[0].rstrip("/")
    if normalized in EXACT_REDIRECTS:
        return EXACT_REDIRECTS[normalized]

    if "/training/paths/" in normalized:
        return normalized + "/"

    match = re.match(
        r"https://learn\.microsoft\.com/en-us/training/modules/([^/]+)(?:/\d+-(.+))?",
        normalized,
    )
    if not match:
        return url

    module_slug, unit_slug = match.group(1), match.group(2)

    if not unit_slug:
        module_slug = MODULE_ALIASES.get(module_slug, module_slug)
        return _module_url(module_slug)

    bare_slug = unit_slug
    if bare_slug in UNIT_RELOCATIONS:
        module_slug, target_slug = UNIT_RELOCATIONS[bare_slug]
    else:
        module_slug = MODULE_ALIASES.get(module_slug, module_slug)
        target_slug = UNIT_ALIASES.get(bare_slug, bare_slug)

    resolved = _unit_url(module_slug, target_slug)
    if resolved:
        return resolved

    return _module_url(module_slug)


def verify_url(url: str) -> bool:
    request = urllib.request.Request(
        url,
        method="HEAD",
        headers={"User-Agent": "az900-prep/1.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.status == 200
    except urllib.error.HTTPError as exc:
        if exc.code in (405, 403):
            return verify_url_get(url)
        return False
    except urllib.error.URLError:
        return False


def verify_url_get(url: str) -> bool:
    request = urllib.request.Request(url, headers={"User-Agent": "az900-prep/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.status == 200
    except Exception:
        return False
