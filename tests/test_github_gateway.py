import os
import unittest
from unittest.mock import patch
from github.gateway import FineGrainedPATGateway, GitHubChange, GitHubGatewayError
from github.policy import AuthorizationError, GitHubAuthorization, validate_authorization
from github.token import FineGrainedPATConfig

class GatewayTests(unittest.TestCase):
    def setUp(self):
        self.auth = GitHubAuthorization(
            "auth_1", "task_1", "Yugatn/MyPro", "mira",
            frozenset({"write_branch", "create_pr"}), ("spec/", "github/"), "main"
        )

    def test_token_is_environment_only(self):
        with patch.dict(os.environ, {"MYPRO_GITHUB_TOKEN": "secret"}, clear=True):
            config = FineGrainedPATConfig("Yugatn/MyPro")
            self.assertEqual(config.token, "secret")
            self.assertNotIn("secret", str(config.redacted()))

    def test_main_write_authorization_is_denied(self):
        with self.assertRaises(AuthorizationError):
            validate_authorization(self.auth, repository="Yugatn/MyPro", operation="write_branch")

    def test_path_scope_is_enforced(self):
        with self.assertRaises(AuthorizationError):
            validate_authorization(self.auth, repository="Yugatn/MyPro",
                                   operation="write_branch", paths=("README.md",))

    def test_gateway_has_no_merge_capability(self):
        gateway = FineGrainedPATGateway(FineGrainedPATConfig("Yugatn/MyPro"))
        self.assertFalse(hasattr(gateway, "merge_pull_request"))

    def test_main_branch_is_rejected(self):
        gateway = FineGrainedPATGateway(FineGrainedPATConfig("Yugatn/MyPro"))
        auth = GitHubAuthorization("auth_2", "task_2", "Yugatn/MyPro", "mira",
                                    frozenset({"write_branch"}), ("github/",), "dev")
        with self.assertRaises(GitHubGatewayError):
            gateway.write_file(authorization=auth, branch="main",
                               change=GitHubChange("github/x.py", "x"))

if __name__ == "__main__":
    unittest.main()
