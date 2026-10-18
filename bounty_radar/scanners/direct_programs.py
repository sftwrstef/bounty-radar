from __future__ import annotations

import re
from typing import Any

from bounty_radar.github_api import GitHubAPIError, GitHubClient
from bounty_radar.models import Signal


# These deliberately require both payment language and a direct private route.
# A generic responsible-disclosure policy is useful context, but is not a paid
# hunt and must not page the operator as one.
DIRECT_POLICY_QUERIES = (
    '"bug bounty" "security@" filename:SECURITY.md',
    '"bug bounty" "security@" filename:security.txt',
    '"security reward" "mailto:" filename:SECURITY.md',
)
PAYMENT_TERMS = (
    "bug bounty",
    "security reward",
    "bounty reward",
    "reward for valid",
    "cash reward",
    "payout",
)
PAYMENT_EVIDENCE_TERMS = (
    "$",
    "pay ",
    "payout",
    "reward tier",
    "reward amount",
    "maximum reward",
    "up to ",
)
REPORTING_TERMS = (
    "mailto:",
    "security@",
    "report to",
    "report via email",
    "contact security",
)
WEB3_TERMS = (
    "blockchain",
    "crypto",
    "defi",
    "ethereum",
    "evm",
    "solana",
    "smart contract",
    "solidity",
    "web3",
)
PLATFORM_ROUTE_TERMS = (
    "bugcrowd",
    "hackerone",
    "immunefi",
    "hackenproof",
    "cantina",
    "sherlock",
)
EMAIL_RE = re.compile(r"[a-z0-9._%+\-]+@[a-z0-9.\-]+\.[a-z]{2,}", re.IGNORECASE)
DIRECT_POLICY_FILENAMES = {
    "security.md",
    "security.txt",
    "security-policy.md",
    "security-policy.txt",
    "vulnerability-disclosure.md",
    "bug-bounty.md",
}


def is_direct_bounty_policy(text: str, *, path: str = "") -> bool:
    """Return True only for a policy that promises a reward and direct reporting."""
    lowered = text.lower()
    has_payment = any(term in lowered for term in PAYMENT_TERMS) and any(
        term in lowered for term in PAYMENT_EVIDENCE_TERMS
    )
    has_reporting_route = any(term in lowered for term in REPORTING_TERMS) or bool(
        EMAIL_RE.search(text)
    )
    policy_filename = path.rsplit("/", 1)[-1].lower()
    is_policy_file = policy_filename in DIRECT_POLICY_FILENAMES
    is_web3 = any(term in lowered for term in WEB3_TERMS)
    uses_platform_route = any(term in lowered for term in PLATFORM_ROUTE_TERMS)
    return has_payment and has_reporting_route and is_policy_file and is_web3 and not uses_platform_route


def is_web3_repository(repo: dict[str, Any]) -> bool:
    """Avoid treating a generic security-template mention of crypto as a Web3 bounty."""
    metadata = " ".join(
        [
            str(repo.get("description") or ""),
            str(repo.get("homepage") or ""),
            " ".join(str(topic) for topic in repo.get("topics") or []),
        ]
    ).lower()
    return any(term in metadata for term in WEB3_TERMS)


def scan_direct_programs(
    api: GitHubClient,
    *,
    max_results: int,
) -> tuple[list[Signal], list[str]]:
    """Discover first-party GitHub policies advertising a directly reportable reward."""
    signals: list[Signal] = []
    errors: list[str] = []
    seen_files: set[tuple[str, str]] = set()

    for query in DIRECT_POLICY_QUERIES:
        try:
            result = api.search_code_query(query, max_results=max_results)
        except GitHubAPIError as exc:
            errors.append(f"github-direct-programs: code search failed for {query}: {exc}")
            break

        for item in result.get("items", []):
            repo = item.get("repository") or {}
            full_name = str(repo.get("full_name") or "")
            path = str(item.get("path") or "")
            if not full_name or not path or (full_name, path) in seen_files:
                continue
            seen_files.add((full_name, path))
            try:
                repo_info = api.get_repo(full_name)
                if not is_web3_repository(repo_info):
                    continue
                policy = api.get_content_file(full_name, path)
            except GitHubAPIError as exc:
                errors.append(f"github-direct-programs: could not read {full_name}/{path}: {exc}")
                continue
            if not policy or not is_direct_bounty_policy(policy.get("text", ""), path=path):
                continue

            sha = str(policy.get("sha") or "unknown")
            signals.append(
                Signal(
                    signal_type="direct_program_discovered",
                    key=f"{full_name}: {path}",
                    title="Direct bounty program discovered",
                    severity=5,
                    details=(
                        f"{full_name}/{path} contains explicit reward language and a direct "
                        "private reporting route. Verify scope and payout terms before hunting."
                    ),
                    fingerprint=f"direct-program:{full_name}:{path}:{sha}",
                    url=policy.get("html_url") or item.get("html_url"),
                    metadata={
                        "repository": full_name,
                        "path": path,
                        "query": query,
                        "validated": ["reward_language", "direct_reporting_route"],
                    },
                )
            )

    return signals, errors
