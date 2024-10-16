import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any

from github_service import GitHubService
from notification_service import NotificationService


class PRService:
    def __init__(self, github_service: GitHubService, notification_service: NotificationService):
        self.github_service = github_service
        self.notification_service = notification_service
        self.batch_size = 5

    async def report_prs(self, organization_name: str):
        repos = await self.github_service.list_private_repos(organization_name)
        prs_semaphore = asyncio.Semaphore(self.batch_size)

        async def get_prs(repo):
            async with prs_semaphore:
                return await self.__get_filtered_prs(repo)

        tasks = [get_prs(repo) for repo in repos]
        results = await asyncio.gather(*tasks)
        for repo, filtered_prs in zip(repos, results):
            for pr in filtered_prs:
                created_at: datetime = pr['created_at']
                ten_days_ago = datetime.now() - timedelta(days=10)

                if 'long-term' not in pr['labels'] or created_at < ten_days_ago:
                    await self.notification_service.notify(pr)

    async def __get_filtered_prs(self, repo: Dict[str, str]) -> List[Dict[str, Any]]:
        prs = await self.github_service.get_open_prs(repo)
        now = datetime.now()
        three_days_ago = now - timedelta(days=3)
        filtered_prs = []
        review_semaphore = asyncio.Semaphore(self.batch_size)

        async def get_pr_reviews(pr_number):
            async with review_semaphore:
                return await self.github_service.get_pr_reviews(repo, pr_number)

        for pr in prs:
            if pr["draft"]:
                continue
            created_at = datetime.strptime(pr["created_at"], "%Y-%m-%dT%H:%M:%SZ")
            if created_at < three_days_ago:
                reviews = await asyncio.create_task(get_pr_reviews(pr['number']))
                approvals = sum(1 for review in reviews if review["state"] == "APPROVED")
                if approvals >= 1:
                    days_open = (now - created_at).days
                    filtered_prs.append({
                        "number": pr["number"],
                        "title": pr["title"],
                        "url": pr["html_url"],
                        "created_at": created_at,
                        "days_open": days_open,
                        "approvals": approvals,
                        "owner": pr["user"]["login"],
                        "repo_name": pr['base']['repo']['name'],
                        "labels": [label["name"] for label in pr["labels"]]
                    })
        return filtered_prs
