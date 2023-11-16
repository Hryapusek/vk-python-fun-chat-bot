import vk_api
from vk_api import longpoll
import logging
import random
from commands_utils import *


class CockSizeCommand:
    name = "CockSize"
    command_trigger = "cock"

    def __init__(self) -> None:
        self.logger = logging.getLogger("main")
        pass

    def send_response_message(
        self, event: longpoll.Event, vk_session: vk_api.VkApi, cock_size: int
    ):
        text = (
            "BOT MESSAGE:\nРазмер вашего члена "
            + str(cock_size)
            + " см.\n"
            + "c"
            + cock_size * "="
            + "3"
        )
        simple_reply_to_message(vk_session, event.peer_id, event.message_id, text)

    def is_this_command(self, message: str) -> bool:
        return is_command(message, self.command_trigger)

    def __generate_cock_size() -> float:
        size = int(random.gauss(13, 3))
        if size < 0:
            size *= -1
        return size

    def execute(self, vk_session: vk_api.VkApi, event: longpoll.Event):
        self.logger.debug("Sending response message.")
        self.send_response_message(
            event, vk_session, CockSizeCommand.__generate_cock_size()
        )
