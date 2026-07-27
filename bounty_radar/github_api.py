from __future__ import annotations

import base64
import time
from datetime import datetime
from typing import Any
from urllib.parse import quote

import requests

from bounty_radar.config import requests_verify_path


class GitHubAPIError(RuntimeError):
    pass


class GitHubNotFound(GitHubAPIError):
    pass


class GitHubClient:
    def __init__(self, token: str | None = None, api_base: str = "https://api.github.com") -> None:
        self.api_base = api_base.rstrip("/")
        self.token_provided = bool(token)
        self.code_search_unavailable_error: str | None = None
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "bounty-radar/0.1",
            }
        )
        self.session.verify = requests_verify_path()
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"

    def _get(self, url: str, *, params: dict[str, Any] | None = None) -> requests.Response:
        last_exc: requests.RequestException | None = None
        for attempt in range(3):
            try:
                return self.session.get(url, params=params, timeout=30)
            except requests.RequestException as exc:
                last_exc = exc
                if attempt == 2:
                    break
                time.sleep(1.5 * (attempt + 1))
        raise GitHubAPIError(f"GitHub transport error: {last_exc}") from last_exc

    def _request(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        *,
        allow_404: bool = False,
    ) -> Any:
        url = path if path.startswith("http") else f"{self.api_base}{path}"
        response = self._get(url, params=params)
        if response.status_code == 404 and allow_404:
            return None
        if response.status_code == 404:
            raise GitHubNotFound(f"GitHub resource not found: {url}")
        if response.status_code == 403 and response.headers.get("X-RateLimit-Remaining") == "0":
            reset_at = int(response.headers.get("X-RateLimit-Reset", "0"))
            wait_for = max(0, reset_at - int(time.time()))
            raise GitHubAPIError(f"GitHub rate limit exhausted; resets in {wait_for}s")
        if response.status_code >= 400:
            raise GitHubAPIError(f"GitHub API {response.status_code}: {response.text[:300]}")
        if not response.content:
            return None
        return response.json()

    def _paginate(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        *,
        max_pages: int = 5,
    ) -> list[dict[str, Any]]:
        url = f"{self.api_base}{path}"
        page_params = dict(params or {})
        items: list[dict[str, Any]] = []

        for _ in range(max_pages):
            response = self._get(url, params=page_params)
            if response.status_code == 403 and response.headers.get("X-RateLimit-Remaining") == "0":
                reset_at = int(response.headers.get("X-RateLimit-Reset", "0"))
                wait_for = max(0, reset_at - int(time.time()))
                raise GitHubAPIError(f"GitHub rate limit exhausted; resets in {wait_for}s")
            if response.status_code >= 400:
                raise GitHubAPIError(f"GitHub API {response.status_code}: {response.text[:300]}")
            data = response.json()
            if isinstance(data, list):
                items.extend(data)
            else:
                break
            next_url = response.links.get("next", {}).get("url")
            if not next_url:
                break
            url = next_url
            page_params = {}

        return items

    @staticmethod
    def _iso(dt: datetime) -> str:
        return dt.isoformat().replace("+00:00", "Z")

    def get_repo(self, full_name: str) -> dict[str, Any]:
        return self._request(f"/repos/{full_name}")

    def list_org_repos(
        self,
        org: str,
        *,
        include_archived: bool = False,
        max_repos: int = 75,
    ) -> list[dict[str, Any]]:
        pages = max(1, (max_repos + 99) // 100)
        repos = self._paginate(
            f"/orgs/{org}/repos",
            {"type": "public", "sort": "pushed", "direction": "desc", "per_page": 100},
            max_pages=pages,
        )
        filtered = [repo for repo in repos if include_archived or not repo.get("archived")]
        return filtered[:max_repos]

    def get_content_file(
        self,
        full_name: str,
        path: str,
        *,
        ref: str | None = None,
    ) -> dict[str, Any] | None:
        params = {"ref": ref} if ref else None
        encoded = quote(path, safe="/")
        data = self._request(f"/repos/{full_name}/contents/{encoded}", params, allow_404=True)
        if not data or isinstance(data, list):
            return None
        text = ""
        if data.get("encoding") == "base64" and data.get("content"):
            text = base64.b64decode(data["content"]).decode("utf-8", errors="replace")
        return {
            "path": data.get("path", path),
            "sha": data.get("sha"),
            "html_url": data.get("html_url"),
            "text": text,
        }

    def get_readme(self, full_name: str, *, ref: str | None = None) -> dict[str, Any] | None:
        params = {"ref": ref} if ref else None
        data = self._request(f"/repos/{full_name}/readme", params, allow_404=True)
        if not data:
            return None
        text = ""
        if data.get("encoding") == "base64" and data.get("content"):
            text = base64.b64decode(data["content"]).decode("utf-8", errors="replace")
        return {
            "path": data.get("path", "README"),
            "sha": data.get("sha"),
            "html_url": data.get("html_url"),
            "text": text,
        }

    def list_commits(
        self,
        full_name: str,
        *,
        since: datetime,
        until: datetime | None = None,
        max_pages: int = 3,
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {
            "since": self._iso(since),
            "per_page": 100,
        }
        if until:
            params["until"] = self._iso(until)
        return self._paginate(f"/repos/{full_name}/commits", params, max_pages=max_pages)

    def list_releases(self, full_name: str, *, max_releases: int = 5) -> list[dict[str, Any]]:
        pages = max(1, (max_releases + 99) // 100)
        releases = self._paginate(
            f"/repos/{full_name}/releases",
            {"per_page": min(max_releases, 100)},
            max_pages=pages,
        )
        return releases[:max_releases]

    def search_code(self, full_name: str, term: str, *, max_results: int = 3) -> dict[str, Any]:
        query = f'repo:{full_name} "{term}"'
        return self.search_code_query(query, max_results=max_results)

    def search_code_query(self, query: str, *, max_results: int = 3) -> dict[str, Any]:
        """Search public GitHub code without constraining the query to one repository."""
        if self.code_search_unavailable_error:
            raise GitHubAPIError(self.code_search_unavailable_error)
        try:
            return self._request("/search/code", {"q": query, "per_page": max_results})
        except GitHubAPIError as exc:
            if "rate limit exhausted" in str(exc).lower():
                self.code_search_unavailable_error = (
                    f"GitHub code search unavailable for remainder of run: {exc}"
                )
            raise
