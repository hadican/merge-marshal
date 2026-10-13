import os
import unittest
from unittest.mock import patch

from config import Config

REQUIRED_ENV = {
    "SLACK_TOKEN": "slack-token",
    "GITHUB_TOKEN": "github-token",
    "GITHUB_ORGANIZATION_NAME": "org",
    "DEFAULT_SLACK_EMAIL": "default@example.com",
}


@patch.object(Config, "_load_author_mapping", return_value={})
class ConfigTest(unittest.TestCase):
    def test_ignore_users_is_optional(self, _):
        with patch.dict(os.environ, REQUIRED_ENV, clear=True):
            self.assertEqual(Config().ignore_users, [])

    def test_ignore_users_is_comma_separated(self, _):
        with patch.dict(os.environ, {**REQUIRED_ENV, "IGNORE_USERS": "machine-user, other-user,"}, clear=True):
            self.assertEqual(Config().ignore_users, ["machine-user", "other-user"])


if __name__ == "__main__":
    unittest.main()
