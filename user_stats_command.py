import vk_api
from vk_api import longpoll
import logging
import stats
from commands_utils import *

class UserStatsCommand:
    name = "StatsCommand"
    command_trigger = "my_stats"

    def __init__(self, statistics: stats.Stats) -> None:
        self.statistics = statistics
        self.logger = logging.getLogger("main")

    def send_response_message(
        self, event: longpoll.Event, vk_session: vk_api.VkApi, msg_count: int
    ):
        self.logger.info("User id: " + str(event.user_id))
        self.logger.info("Message count: " + str(msg_count))
        text = ("BOT MESSAGE:\nЗа последние 3 месяца вы отправили "
            + str(msg_count)
            + " сообщений.")
        simple_reply_to_message(vk_session, event.peer_id, event.message_id, text)

    def is_this_command(self, message: str) -> bool:
        return is_command(message, self.command_trigger)

    def execute(self, vk_session: vk_api.VkApi, event: longpoll.Event):
        msg_count = self.statistics.get_user_message_count(event.user_id)
        self.logger.debug("Sending response message.")
        self.send_response_message(event, vk_session, msg_count)

