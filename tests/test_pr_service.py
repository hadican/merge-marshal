import unittest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

from pr_service import PRService


def approved_pr(number, login, user_type="User"):
    created_at = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%dT%H:%M:%SZ")
    return {
        "number": number,
        "title": f"PR {number}",
        "html_url": f"https://github.com/org/repo/pull/{number}",
        "created_at": created_at,
        "draft": False,
        "user": {"login": login, "type": user_type},
        "base": {"repo": {"name": "repo"}},
        "labels": [],
    }


class ReportPRsTest(unittest.IsolatedAsyncioTestCase):
    async def notified_owners(self, prs, ignore_users=None):
        github_service = MagicMock()
        github_service.list_private_repos = AsyncMock(return_value=[{"name": "repo", "full_name": "org/repo"}])
        github_service.get_open_prs = AsyncMock(return_value=prs)
        github_service.get_pr_reviews = AsyncMock(return_value=[{"state": "APPROVED"}])
        notification_service = MagicMock()
        notification_service.notify = AsyncMock()

        await PRService(github_service, notification_service, ignore_users or []).report_prs("org")

        return [call.args[0]["owner"] for call in notification_service.notify.await_args_list]

    async def test_notifies_human_authors(self):
        self.assertEqual(await self.notified_owners([approved_pr(1, "alice")]), ["alice"])

    async def test_skips_bot_authors(self):
        prs = [approved_pr(1, "alice"), approved_pr(2, "dependabot[bot]", user_type="Bot")]
        self.assertEqual(await self.notified_owners(prs), ["alice"])

    async def test_skips_ignored_users(self):
        prs = [approved_pr(1, "alice"), approved_pr(2, "machine-user")]
        self.assertEqual(await self.notified_owners(prs, ignore_users=["machine-user"]), ["alice"])


if __name__ == "__main__":
    unittest.main()
