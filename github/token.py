from __future__ import annotations
from dataclasses import dataclass
import os

class GitHubCredentialError(RuntimeError):
    pass

@dataclass(frozen=True)
class FineGrainedPATConfig:
    repository: str
    token_env: str = "MYPRO_GITHUB_TOKEN"
    api_base: str = "https://api.github.com"

    @property
    def token(self) -> str:
        value = os.environ.get(self.token_env)
        if not value:
            raise GitHubCredentialError("GitHub token is missing; set " + self.token_env)
        return value

    def redacted(self) -> dict[str, str]:
        return {"repository": self.repository, "token_env": self.token_env, "api_base": self.api_base}
