import asyncio

from config import Config
from github_service import GitHubService
from notification_service import NotificationService
from pr_service import PRService
from slack_service import SlackService


async def main():
    config = Config()
    slack_service = SlackService(config.slack_token)
    github_service = GitHubService(config.github_token)
    notification_service = NotificationService(slack_service, config)
    pr_service = PRService(github_service, notification_service)
    await pr_service.report_prs(config.organization_name)


if __name__ == "__main__":
    asyncio.run(main())
