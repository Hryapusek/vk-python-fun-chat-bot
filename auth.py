import sys
import vk_api
from time import sleep
import logging

logger = logging.getLogger("main")

TOKEN_FILE_NAME = "vk_common/token.txt"

def read_token() -> str:
    with open(TOKEN_FILE_NAME) as file:
        token = file.readline()
    return token

def get_token(fromFile: bool = False) -> str:
    if not fromFile and len(sys.argv) == 3:
        token = sys.argv[1]
        with open(TOKEN_FILE_NAME, 'w') as file:
            file.write(token)
        return token
    return read_token()

def auth(fromFile: bool = False) -> vk_api.VkApi:
    count = 1
    MAX_COUNT = 10
    while count < MAX_COUNT:
        try:
            logger.info("Starting auth...")
            logger.info("Try number: " + str(count))
            token = get_token(fromFile)
            logger.info("Token: " + token)
            vk_session = vk_api.VkApi(
                api_version="5.131",
                token=token,
            )
            logger.info("Auth finished successfully.")
            return vk_session
        except Exception as e:
            logger.warning("Exception: " + str(e))
            logger.info("Auth failed! Retry in 3 seconds...")
            count += 1
            if count != MAX_COUNT:
                sleep(3)
    if count == MAX_COUNT:
        raise Exception("Max retry count exceeded.")
