import logging
from typing import Optional

from slack_sdk.errors import SlackApiError
from slack_sdk.web.async_client import AsyncWebClient


class SlackService:
    def __init__(self, token):
        self.client = AsyncWebClient(token=token)
        self.logger = logging.getLogger(self.__class__.__name__)

    async def get_user_id_by_email(self, email) -> Optional[str]:
        try:
            response = await self.client.users_lookupByEmail(email=email)
            return response["user"]["id"]
        except SlackApiError as e:
            self.logger.error(f"Failed to fetch user ID for email={email} error={e.response['error']}")
            return None
        except Exception as e:
            self.logger.error(f"Error fetching user ID for email={email} error={str(e)}")
            return None

    async def send_message(self, message, user_id) -> bool:
        try:
            await self.client.chat_postMessage(channel=user_id, text=message)
            return True
        except SlackApiError as e:
            self.logger.error(f"Failed to send Slack message with error={e.response['error']}")
            return False
        except Exception as e:
            self.logger.error(f"Failed to send Slack message with error={str(e)}")
            return False
