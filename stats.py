from __future__ import annotations
import sys
from time import sleep
from datetime import datetime
import logging
import auth
import sortedcontainers
import vk_api
import os

class User:
    def __init__(self, id: int, msg_count: int = 0) -> None:
        self.user_id = id
        self.msg_count = msg_count

    def __lt__(self, other: User):
        return self.user_id < other.user_id

    def __eq__(self, other: User) -> bool:
        return self.user_id == other.user_id

    def __hash__(self) -> int:
        return hash(self.user_id)


class Stats:
    PEER_CHAT_START_ID = 2000000000
    MONTH = 60 * 60 * 24 * 30
    PACKET_SIZE = 200
    STATS_FILE_NAME = "vk_common/stats.txt"

    def __init__(self, vk_session: vk_api.VkApi, CHAT_ID: int) -> None:
        if vk_session is None:
            self.vk_session = auth.auth(True)
        else:
            self.vk_session = vk_session
        self.CHAT_ID = CHAT_ID
        self.current_time = datetime.utcnow().timestamp()
        self.lowerest_time = self.current_time - 3 * Stats.MONTH
        self.users_set = sortedcontainers.SortedSet(None, lambda user: user.user_id)
        self.current_offset = 0
        self.peer_id = Stats.PEER_CHAT_START_ID + CHAT_ID
        self.__init_logger()

    def __init_logger(self):
        self.logger = logging.getLogger("stats")

    def retrieve_stats(self, cached: bool = False):
        if cached and os.path.isfile(Stats.STATS_FILE_NAME):
            self.logger.info("Found cached file. Starting reading")
            self.__read_stats_from_file()
            self.logger.info("Stats reading was successfull")
            return
        self.logger.info("Cache is not used. Updating stats from vk.com")
        while not self.current_time < self.lowerest_time:
            res = self.vk_session.method(
                "messages.getHistory",
                {
                    "offset": self.current_offset,
                    "peer_id": self.peer_id,
                    "count": Stats.PACKET_SIZE,
                },
            )
            if len(res["items"]) == 0:
                self.logger.info("No more items found. Finishing processing messages")
                break
            for message in res["items"]:
                self.__process_message(message)
                self.current_offset += 1
                self.current_time = int(message["date"])
                self.logger.info(str(self.current_offset) + " messages processed")
                if self.current_time < self.lowerest_time:
                    self.logger.info(
                        "Timeline limit reached. Finishing processing messages"
                    )
                    break
            else:
                sleep(0.3)
                continue
            break
        self.__write_stats_to_file()

    def __read_stats_from_file(self):
        with open(Stats.STATS_FILE_NAME) as statsFile:
                lines = statsFile.readlines()
        for line in lines:
            user_id, msg_count = map(int, line.split(' '))
            self.users_set.add(User(user_id, msg_count))

    def __write_stats_to_file(self):
        with open(Stats.STATS_FILE_NAME, "w") as statsFile:
            for item in self.users_set:
                statsFile.write(str(item.user_id) + " " + str(item.msg_count) + "\n")

    def __process_message(self, msg):
        try:
            self.logger.info("Processing another message.")
            self.__log_message_info(msg)
            user_id = int(msg["from_id"])
            if user_id <= 0:
                self.logger.info("Message not from user. Skipping")
                return
            if not self.users_set.__contains__(User(user_id)):
                self.logger.info("Added user " + str(user_id))
                self.users_set.add(User(user_id))
            self.users_set[self.users_set.index(User(user_id))].msg_count += 1
            self.logger.info("Processed successfully.")
        except Exception as e:
            self.logger.warning("Exception in message processor.")
            self.logger.warning("Exception: " + str(e))
            self.logger.warning("Skipping current message.")

    def __log_message_info(self, msg):
        self.logger.debug(
            "Message text: " + str(msg["text"])[:15] if msg["text"] else "None"
        )
        user_id = int(msg["from_id"])
        self.logger.debug("Message from_id: " + str(user_id))
        time_str = str(datetime.fromtimestamp(int(msg["date"])))
        self.logger.info("Message date: " + time_str)
        hasUser = self.users_set.__contains__(User(user_id))
        self.logger.debug("Has this user: " + str(hasUser))
        if hasUser:
            self.logger.debug(
                "Message count: "
                + str(self.users_set[self.users_set.index(User(user_id))].msg_count)
            )

    def get_user_message_count(self, user_id: int) -> int:
        if not self.users_set.__contains__(User(user_id)):
            return 0
        return self.users_set[self.users_set.index(User(user_id))].msg_count

    def get_users_count(self) -> int:
        return len(self.users_set)



if __name__ == "__main__":
    logger = logging.getLogger("stats")
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    if len(sys.argv) != 2:
        logger.critical("You must specify chat id in CMD line args")
        exit(1)

    CHAT_ID = 0
    try:
        CHAT_ID = int(sys.argv[1])
    except:
        logger.critical("Can not convert CMD arg to chat id")
        exit(1)

    try:
        vk_session = auth.auth(True)
        stats = Stats(vk_session, CHAT_ID)
        stats.retrieve_stats()
    except Exception as e:
        logger.warning("Fatal exception caught.")
        logger.warning("Exception: " + str(e))
        exit(1)

    logger.info("Finished. Output file created.")
