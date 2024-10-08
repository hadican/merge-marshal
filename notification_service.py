import logging
from typing import Optional

from config import Config
from slack_service import SlackService


class NotificationService:
    def __init__(self, slack_service: SlackService, config: Config):
        self.slack_service = slack_service
        self.config = config
        self._default_user_id: Optional[str] = None
        self.logger = logging.getLogger(self.__class__.__name__)

    async def notify(self, pr):
        pr_url = pr['url']
        pr_owner = pr['owner']

        message = (
            f"Your PR `#{pr['number']}` in the `{pr['repo_name']}` has been open for over "
            f"3 days `({pr['days_open']})` and has at least 1 approval.\n"
            f"Please consider merging it.\n"
            f"If you think your PR is `not mergeable` for some reason, "
            f"please either convert it to a `draft` or add the `long-term` label to your PR.\n\n"
            f"`Title:` {pr['title']}\n"
            f"`URL:` {pr_url}\n"
            "----------------------------------"
        )

        slack_email = self.config.author_mapping.get(pr_owner)

        if not slack_email:
            author_mapping_message = f"No user was found in the author mapping with the username={pr_owner} for the PR url={pr_url}"
            self.logger.warning(author_mapping_message)
            await self.slack_service.send_message(author_mapping_message, await self.default_user_id)
            return

        user_id = await self.slack_service.get_user_id_by_email(slack_email)

        if not user_id:
            slack_user_message = f"Failed to fetch user ID from Slack for the email={slack_email} for the PR url={pr_url}"
            self.logger.warning(slack_user_message)
            await self.slack_service.send_message(slack_user_message, await self.default_user_id)
            return

        status = await self.slack_service.send_message(message, user_id)

        if not status:
            self.logger.warning(f"Failed to send Slack message for the PR url={pr_url}")

    @property
    async def default_user_id(self) -> str:
        if not self._default_user_id:
            user_id = await self.slack_service.get_user_id_by_email(self.config.default_slack_email)
            if not user_id:
                raise Exception(
                    f"Failed to retrieve default Slack user ID for the email: {self.config.default_slack_email}")

            self._default_user_id = user_id

        return self._default_user_id
