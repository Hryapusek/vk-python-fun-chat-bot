import sys
import vk_api
from time import sleep
from vk_api import longpoll
import logging
import stats
import auth
from cock_command import CockSizeCommand
from chat_stats_command import ChatStatsCommand
from user_stats_command import UserStatsCommand

logger = logging.getLogger("main")
commands = []


def configure_main_logger():
    logger = logging.getLogger("main")
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def configure_stats_logger():
    logger = logging.getLogger("stats")
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


configure_main_logger()
configure_stats_logger()


def is_command(text: str, command: str) -> bool:
    if text is None:
        return False
    msg_split = text.strip().split()
    return len(msg_split) != 0 and text.strip().split()[0] == ("/" + command)


def log_message_info(event: longpoll.Event):
    logger.debug(
        "Message text: " + str(event.message)[:15] if event.message else "None"
    )
    user_id = int(event.user_id)
    logger.debug("Message from_id: " + str(user_id))
    time_str = str(event.datetime)
    logger.debug("Message date: " + time_str)


def process_message(event: longpoll.Event):
    if not event.user_id or not event.from_chat or event.chat_id != CHAT_ID:
        logger.debug("Skipping this new message with respect to conditions.")
        return
    logger.info("New message in the given chat.")
    log_message_info(event)
    for cmd in commands:
        if cmd.is_this_command(event.message):
            logger.info(cmd.name + " command found.")
            cmd.execute(vk_session, event)
            logger.info("Execution finished successfully.")
            return
    else:
        logger.info("No command was found")


def init_commands(vk_session: vk_api.VkApi):
    statistics = stats.Stats(vk_session, CHAT_ID)
    statistics.retrieve_stats(True)
    logger.info("Users count in stats: " + str(statistics.get_users_count()))
    global commands
    statsCmd = UserStatsCommand(statistics)
    infoCmd = ChatStatsCommand(statistics)
    cockCmd = CockSizeCommand()
    commands = [statsCmd, infoCmd, cockCmd]


CHAT_ID = int(sys.argv[len(sys.argv) - 1])
retryCount = 1
MAX_RETRY_COUNT = 50

vk_session = auth.auth()
init_commands(vk_session)
first_iteration = True

while True:
    try:
        poll = longpoll.VkLongPoll(vk_session, 1000)
        logger.info("Starting polling messages")
        for event in poll.listen():
            logger.debug("New event found.")
            retryCount = 1
            try:
                if event.type != longpoll.VkEventType.MESSAGE_NEW:
                    logger.debug("Skipping event - not message_new type.")
                    continue
                logger.debug("New message found.")
                process_message(event)
            except Exception as e:
                logger.warning("Exception in event handler.")
                logger.warning("Exception: " + str(e))
                logger.warning("Skipping current event.")

    except Exception as e:
        logger.warning("Fatal exception caught.")
        logger.warning("Exception: " + str(e))
        retryCount += 1
        if retryCount >= MAX_RETRY_COUNT:
            logger.error("Max try count exceeded. Finishing program.")
            exit(1)
        logger.info("Restart in 3 seconds.")
        sleep(3)
        vk_session = auth.auth()
