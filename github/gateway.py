from __future__ import annotations
from dataclasses import dataclass
import base64
import json
from typing import Any
from urllib import request, error
from github.policy import GitHubAuthorization, validate_authorization
from github.token import FineGrainedPATConfig

class GitHubGatewayError(RuntimeError):
    pass

@dataclass(frozen=True)
class GitHubChange:
    path: str
    content: str
    operation: str = "update"

class FineGrainedPATGateway:
    """PR-first GitHub gateway. It never merges and never writes main."""
    def __init__(self, config: FineGrainedPATConfig) -> None:
        self.config = config

    def _request(self, method: str, path: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
        url = self.config.api_base.rstrip("/") + "/" + path.lstrip("/")
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": "Bearer " + self.config.token,
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "MyPro-GitHubGateway/0.1",
        }
        data = None
        if body is not None:
            data = json.dumps(body, ensure_ascii=False).encode("utf-8")
            headers["Content-Type"] = "application/json"
        req = request.Request(url, data=data, headers=headers, method=method)
        try:
            with request.urlopen(req, timeout=30) as response:
                raw = response.read().decode("utf-8")
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise GitHubGatewayError("GitHub API " + str(exc.code) + ": " + detail[:500]) from exc
        except error.URLError as exc:
            raise GitHubGatewayError("GitHub connection failed: " + str(exc.reason)) from exc
        return json.loads(raw) if raw else {}

    def read_file(self, path: str, ref: str = "main") -> str:
        data = self._request("GET", "/repos/" + self.config.repository + "/contents/" + path + "?ref=" + ref)
        if data.get("type") != "file":
            raise GitHubGatewayError("GitHub path is not a file: " + path)
        return base64.b64decode(data["content"].replace("\n", "")).decode("utf-8")

    def read_commit(self, sha: str) -> dict[str, Any]:
        return self._request("GET", "/repos/" + self.config.repository + "/commits/" + sha)

    def create_branch(self, *, authorization: GitHubAuthorization, branch: str, base_sha: str) -> dict[str, Any]:
        validate_authorization(authorization, repository=self.config.repository, operation="write_branch")
        if branch == "main" or branch.startswith("main/"):
            raise GitHubGatewayError("direct writes to main are forbidden")
        return self._request("POST", "/repos/" + self.config.repository + "/git/refs",
                             {"ref": "refs/heads/" + branch, "sha": base_sha})

    def write_file(self, *, authorization: GitHubAuthorization, branch: str,
                   change: GitHubChange) -> dict[str, Any]:
        validate_authorization(authorization, repository=self.config.repository,
                               operation="write_branch", paths=(change.path,))
        if branch == "main":
            raise GitHubGatewayError("direct writes to main are forbidden")
        payload = {
            "message": "MyPro authorized change: " + change.path,
            "content": base64.b64encode(change.content.encode("utf-8")).decode("ascii"),
            "branch": branch,
        }
        if change.operation == "update":
            current = self._request("GET", "/repos/" + self.config.repository +
                                    "/contents/" + change.path + "?ref=" + branch)
            payload["sha"] = current["sha"]
        elif change.operation != "create":
            raise GitHubGatewayError("unsupported change operation: " + change.operation)
        return self._request("PUT", "/repos/" + self.config.repository + "/contents/" + change.path, payload)

    def create_pull_request(self, *, authorization: GitHubAuthorization, branch: str,
                            title: str, body: str) -> dict[str, Any]:
        validate_authorization(authorization, repository=self.config.repository, operation="create_pr")
        if branch == "main":
            raise GitHubGatewayError("a pull request head cannot be main")
        return self._request("POST", "/repos/" + self.config.repository + "/pulls",
                             {"title": title, "head": branch, "base": authorization.target_branch, "body": body})

    def apply_authorized_change(self, *, authorization: GitHubAuthorization, branch: str,
                                base_sha: str, changes: list[GitHubChange],
                                pr_title: str, pr_body: str) -> dict[str, Any]:
        if authorization.target_branch == branch:
            raise GitHubGatewayError("source branch must differ from target branch")
        self.create_branch(authorization=authorization, branch=branch, base_sha=base_sha)
        commits = [self.write_file(authorization=authorization, branch=branch, change=c) for c in changes]
        pr = self.create_pull_request(authorization=authorization, branch=branch,
                                       title=pr_title, body=pr_body)
        return {"repository": self.config.repository, "authorization_id": authorization.authorization_id,
                "branch": branch, "target_branch": authorization.target_branch,
                "commits": commits, "pull_request": pr}
