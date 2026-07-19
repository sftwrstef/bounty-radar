from __future__ import annotations

from typing import Any
from urllib.parse import quote_plus

from bounty_radar.github_api import GitHubAPIError, GitHubClient
from bounty_radar.models import Signal


SECURITY_PATHS = (
    "SECURITY.md",
    ".github/SECURITY.md",
    "docs/SECURITY.md",
    "security.md",
)

KEYWORD_GROUPS: dict[str, tuple[str, ...]] = {
    "bounty_reference": (
        "bug bounty",
        "immunefi",
        "hackenproof",
        "cantina",
        "sherlock",
        "code4rena",
    ),
    "security_policy_reference": (
        "responsible disclosure",
        "security policy",
    ),
    "audit_reference": (
        "audit",
        "security audit",
        "audited by",
        "formal verification",
    ),
    "bridge_reference": (
        "bridge",
        "relayer",
        "prover",
        "settlement",
        "message handler",
        "proof verification",
        "consensus",
        "async",
    ),
}

SEVERITY_BY_TYPE = {
    "bounty_reference": 5,
    "security_policy_reference": 4,
    "audit_reference": 3,
    "bridge_reference": 2,
}

NOISY_CODE_SEARCH_TERMS = {"async"}


def scan_security_docs(
    api: GitHubClient,
    repo: dict[str, Any],
    state: dict[str, str],
) -> tuple[list[Signal], dict[str, str]]:
    full_name = repo["full_name"]
    default_branch = repo.get("default_branch")
    signals: list[Signal] = []
    state_updates: dict[str, str] = {}

    for path in SECURITY_PATHS:
        found = api.get_content_file(full_name, path, ref=default_branch)
        if not found or not found.get("sha"):
            continue

        state_key = f"security_doc_sha:{path}"
        previous_sha = state.get(state_key)
        current_sha = str(found["sha"])
        state_updates[state_key] = current_sha

        if previous_sha is None:
            signals.append(
                Signal(
                    signal_type="security_doc_new",
                    key=path,
                    title="New security policy document detected",
                    severity=5,
                    details=f"{path} exists on {full_name}. First seen by radar.",
                    fingerprint=f"security-doc-new:{path}:{current_sha}",
                    url=found.get("html_url"),
                    metadata={"path": path, "sha": current_sha},
                )
            )
        elif previous_sha != current_sha:
            signals.append(
                Signal(
                    signal_type="security_doc_changed",
                    key=path,
                    title="Security policy document changed",
                    severity=4,
                    details=f"{path} changed from {previous_sha[:8]} to {current_sha[:8]}.",
                    fingerprint=f"security-doc-changed:{path}:{current_sha}",
                    url=found.get("html_url"),
                    metadata={"path": path, "sha": current_sha, "previous_sha": previous_sha},
                )
            )
        else:
            signals.append(
                Signal(
                    signal_type="security_doc_present",
                    key=path,
                    title="Security policy document present",
                    severity=1,
                    details=f"{path} remains present.",
                    fingerprint=f"security-doc-present:{path}",
                    url=found.get("html_url"),
                    metadata={"path": path, "sha": current_sha},
                )
            )

    return signals, state_updates


def scan_repository_text(full_name: str, sources: list[dict[str, str]]) -> list[Signal]:
    signals: list[Signal] = []
    for signal_type, terms in KEYWORD_GROUPS.items():
        for term in terms:
            needle = term.lower()
            for source in sources:
                text = source.get("text", "").lower()
                if needle not in text:
                    continue
                source_name = source.get("name", "unknown")
                signals.append(
                    Signal(
                        signal_type=signal_type,
                        key=term,
                        title=f"{signal_type.replace('_', ' ').title()} found",
                        severity=SEVERITY_BY_TYPE[signal_type],
                        details=f"Found '{term}' in {source_name}.",
                        fingerprint=f"text:{signal_type}:{source_name}:{term}",
                        url=source.get("url"),
                        metadata={"source": source_name, "term": term},
                    )
                )
                break
    return signals


def scan_commit_messages(full_name: str, commits: list[dict[str, Any]]) -> list[Signal]:
    joined_messages = "\n".join(
        str(commit.get("commit", {}).get("message", "")) for commit in commits
    ).lower()
    signals: list[Signal] = []
    if not joined_messages:
        return signals

    for signal_type, terms in KEYWORD_GROUPS.items():
        for term in terms:
            if term.lower() not in joined_messages:
                continue
            first_url = next(
                (
                    commit.get("html_url")
                    for commit in commits
                    if term.lower() in str(commit.get("commit", {}).get("message", "")).lower()
                ),
                None,
            )
            signals.append(
                Signal(
                    signal_type=signal_type,
                    key=term,
                    title=f"Recent commit mentions {term}",
                    severity=SEVERITY_BY_TYPE[signal_type],
                    details=f"Recent commit messages in {full_name} mention '{term}'.",
                    fingerprint=f"commit-message:{signal_type}:{term}",
                    url=first_url,
                    metadata={"source": "recent_commits", "term": term},
                )
            )
    return signals


def flatten_keyword_terms() -> list[tuple[str, str]]:
    terms: list[tuple[str, str]] = []
    for signal_type, group_terms in KEYWORD_GROUPS.items():
        for term in group_terms:
            terms.append((signal_type, term))
    return terms


def scan_code_search(
    api: GitHubClient,
    full_name: str,
    *,
    max_terms: int,
) -> tuple[list[Signal], list[str]]:
    signals: list[Signal] = []
    errors: list[str] = []
    searched = 0

    for signal_type, term in flatten_keyword_terms():
        if searched >= max_terms:
            break
        if term in NOISY_CODE_SEARCH_TERMS:
            continue
        searched += 1
        try:
            result = api.search_code(full_name, term, max_results=3)
        except GitHubAPIError as exc:
            errors.append(f"{full_name}: code search failed for '{term}': {exc}")
            if "rate limit exhausted" in str(exc).lower() or "remainder of run" in str(exc).lower():
                break
            continue

        total_count = int(result.get("total_count", 0))
        if total_count <= 0:
            continue
        search_url = f"https://github.com/search?q={quote_plus(f'repo:{full_name} \"{term}\"')}&type=code"
        signals.append(
            Signal(
                signal_type=signal_type,
                key=term,
                title=f"Code search hit for {term}",
                severity=SEVERITY_BY_TYPE[signal_type],
                details=f"GitHub code search found {total_count} match(es) for '{term}'.",
                fingerprint=f"code-search:{signal_type}:{term}",
                url=search_url,
                metadata={"source": "code_search", "term": term, "matches": total_count},
            )
        )

    return signals, errors
