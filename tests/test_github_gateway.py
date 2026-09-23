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

    def test_authorization_can_target_main_without_authorizing_direct_main_write(self):
        validate_authorization(self.auth, repository="Yugatn/MyPro", operation="write_branch")
        self.assertTrue(self.auth.permits("create_pr", repository="Yugatn/MyPro"))

    def test_path_scope_is_enforced(self):
        with self.assertRaises(AuthorizationError):
            validate_authorization(self.auth, repository="Yugatn/MyPro",
                                   operation="write_branch", paths=("README.md",))

    def test_gateway_has_no_merge_capability(self):
        gateway = FineGrainedPATGateway(FineGrainedPATConfig("Yugatn/MyPro"))
        self.assertFalse(hasattr(gateway, "merge_pull_request"))

    def test_main_branch_is_rejected(self):
        gateway = FineGrainedPATGateway(FineGrainedPATConfig("Yugatn/MyPro"))
        with self.assertRaises(GitHubGatewayError):
            gateway.write_file(authorization=self.auth, branch="main",
                               change=GitHubChange("github/x.py", "x"))

if __name__ == "__main__":
    unittest.main()
