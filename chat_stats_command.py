import vk_api
from vk_api import longpoll
import logging
import stats
from commands_utils import *

class ChatStatsCommand:
    name = "InfoCommand"
    command_trigger = "chat_stats"

    def __init__(self, statistics: stats.Stats) -> None:
        self.statistics = statistics
        self.logger = logging.getLogger("main")

    def send_response_message(
        self, event: longpoll.Event, vk_session: vk_api.VkApi, users_count: int
    ):
        self.logger.debug("User id: " + str(event.user_id))
        self.logger.debug("Users count: " + str(users_count))
        text = ("BOT MESSAGE:\nЗа последние 3 месяца "
            + str(users_count)
            + " людей писали в этой беседе.")
        simple_reply_to_message(vk_session, event.peer_id, event.message_id, text)

    def is_this_command(self, message: str) -> bool:
        return is_command(message, self.command_trigger)

    def execute(self, vk_session: vk_api.VkApi, event: longpoll.Event):
        users_count = self.statistics.get_users_count()
        self.logger.debug("Sending response message.")
        self.send_response_message(event, vk_session, users_count)
