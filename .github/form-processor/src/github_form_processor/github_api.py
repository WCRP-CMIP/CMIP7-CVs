"""Small GitHub REST API client used by the workflow."""

from __future__ import annotations

import base64
import json
from collections.abc import Iterable
from typing import Any
from urllib.error import HTTPError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen


class GitHubApiError(RuntimeError):
    """Error raised when the GitHub API returns an unexpected response."""


class GitHubClient:
    """Minimal GitHub REST client for issue, branch, file and PR operations."""

    def __init__(
        self, repository: str, token: str, api_url: str = "https://api.github.com"
    ) -> None:
        self.repository = repository
        self.owner = repository.split("/", maxsplit=1)[0]
        self.token = token
        self.api_url = api_url.rstrip("/")

    def comment_issue(self, issue_number: int, body: str) -> dict[str, Any]:
        """Create a comment on an issue."""
        return self._request(
            "POST",
            f"/repos/{self.repository}/issues/{issue_number}/comments",
            {"body": body},
            ok_statuses={201},
        )

    def assign_issue(
        self, issue_number: int, assignees: Iterable[str]
    ) -> dict[str, Any]:
        """Assign users to an issue or pull request."""
        return self._request(
            "POST",
            f"/repos/{self.repository}/issues/{issue_number}/assignees",
            {"assignees": list(assignees)},
            ok_statuses={201},
        )

    def get_ref_sha(self, branch: str) -> str:
        """Return the commit SHA for a branch head."""
        payload = self._request(
            "GET", f"/repos/{self.repository}/git/ref/heads/{branch}"
        )
        return str(payload["object"]["sha"])

    def branch_exists(self, branch: str) -> bool:
        """Return whether a branch exists."""
        payload = self._request(
            "GET",
            f"/repos/{self.repository}/git/ref/heads/{branch}",
            allow_404=True,
        )
        return payload is not None

    def create_branch(self, branch: str, sha: str) -> dict[str, Any]:
        """Create a branch at a commit SHA."""
        return self._request(
            "POST",
            f"/repos/{self.repository}/git/refs",
            {"ref": f"refs/heads/{branch}", "sha": sha},
            ok_statuses={201},
        )

    def content_exists(self, path: str, branch: str) -> bool:
        """Return whether a file exists on a branch."""
        return self._get_file_sha(path, branch) is not None

    def put_file(
        self, path: str, branch: str, content: str, message: str
    ) -> dict[str, Any]:
        """Create or update a UTF-8 text file on a branch."""
        existing_sha = self._get_file_sha(path, branch)
        payload = {
            "message": message,
            "content": base64.b64encode(content.encode("utf-8")).decode("ascii"),
            "branch": branch,
        }
        if existing_sha:
            payload["sha"] = existing_sha

        return self._request(
            "PUT",
            f"/repos/{self.repository}/contents/{quote(path, safe='/')}",
            payload,
            ok_statuses={200, 201},
        )

    def delete_file(self, path: str, branch: str, message: str) -> dict[str, Any]:
        """Delete a file from a branch if it exists."""
        existing_sha = self._get_file_sha(path, branch)
        if existing_sha is None:
            return {}

        return self._request(
            "DELETE",
            f"/repos/{self.repository}/contents/{quote(path, safe='/')}",
            {
                "message": message,
                "sha": existing_sha,
                "branch": branch,
            },
            ok_statuses={200},
        )

    def create_pull_request(
        self, title: str, head: str, base: str, body: str
    ) -> dict[str, Any]:
        """Create a pull request."""
        return self._request(
            "POST",
            f"/repos/{self.repository}/pulls",
            {
                "title": title,
                "head": head,
                "base": base,
                "body": body,
                "maintainer_can_modify": True,
            },
            ok_statuses={201},
        )

    def find_pull_requests_for_branch(self, branch: str) -> list[dict[str, Any]]:
        """Return pull requests whose head is the named branch in this repository."""
        query = urlencode({"head": f"{self.owner}:{branch}", "state": "all"})
        payload = self._request("GET", f"/repos/{self.repository}/pulls?{query}")
        if not isinstance(payload, list):
            raise GitHubApiError("Expected a list of pull requests from GitHub.")
        return payload

    def find_pull_requests_for_issue(self, issue_number: int) -> list[dict[str, Any]]:
        """Return pull requests that refer to the source issue in their body."""
        query = urlencode({"state": "all", "per_page": 100})
        payload = self._request("GET", f"/repos/{self.repository}/pulls?{query}")
        if not isinstance(payload, list):
            raise GitHubApiError("Expected a list of pull requests from GitHub.")

        issue_markers = (
            f"generated from #{issue_number}",
            f"Closes #{issue_number}",
            f"closes #{issue_number}",
        )
        return [
            pull
            for pull in payload
            if any(marker in str(pull.get("body", "")) for marker in issue_markers)
        ]

    def _get_file_sha(self, path: str, branch: str) -> str | None:
        query = urlencode({"ref": branch})
        payload = self._request(
            "GET",
            f"/repos/{self.repository}/contents/{quote(path, safe='/-_.')}?{query}",
            allow_404=True,
        )
        if payload is None:
            return None
        if isinstance(payload, list):
            raise GitHubApiError(
                f"Expected `{path}` to be a file, but GitHub returned a directory."
            )
        return str(payload["sha"])

    def _request(
        self,
        method: str,
        path: str,
        data: dict[str, Any] | None = None,
        *,
        ok_statuses: set[int] | None = None,
        allow_404: bool = False,
    ) -> Any:
        if ok_statuses is None:
            ok_statuses = {200}

        body = None if data is None else json.dumps(data).encode("utf-8")
        request = Request(
            f"{self.api_url}{path}",
            data=body,
            method=method,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
                "User-Agent": "github-form-processor",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )

        try:
            with urlopen(request) as response:
                response_body = response.read().decode("utf-8")
                status = int(response.status)
        except HTTPError as exc:
            if allow_404 and exc.code == 404:
                return None
            error_body = exc.read().decode("utf-8", errors="replace")
            raise GitHubApiError(
                f"GitHub API {method} {path} failed: HTTP {exc.code}: {error_body}"
            ) from exc

        if status not in ok_statuses:
            raise GitHubApiError(
                f"GitHub API {method} {path} returned unexpected status {status}."
            )

        if not response_body:
            return {}
        return json.loads(response_body)
