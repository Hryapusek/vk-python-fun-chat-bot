import vk_api
from vk_api import longpoll
import logging
from commands_utils import *
import random


class AskCommand:
    name = "AskCommand"
    command_trigger = "ask"

    def __init__(self) -> None:
        self.logger = logging.getLogger("main")

    def send_response_message(self, event: longpoll.Event, vk_session: vk_api.VkApi):
        num = random.randint(0, 1)
        text = "BOT MESSAGE:\n"
        text += "Да." if num == 1 else "Нет."
        simple_reply_to_message(vk_session, event.peer_id, event.message_id, text)

    def is_this_command(self, message: str) -> bool:
        return is_command(message, self.command_trigger)

    def execute(self, vk_session: vk_api.VkApi, event: longpoll.Event):
        self.logger.debug("Sending response message.")
        self.send_response_message(event, vk_session)
