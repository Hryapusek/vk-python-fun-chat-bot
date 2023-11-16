import vk_api

def is_command(text: str, command: str) -> bool:
    if text is None:
        return False
    msg_split = text.strip().split()
    return len(msg_split) != 0 and text.strip().split()[0] == ("/" + command)

def simple_reply_to_message(vk_session: vk_api.VkApi, peer_id: int, message_id: int, text: str):
    method_params = {
            "random_id": 0,
            "peer_id": peer_id,
            "reply_to": message_id,
            "message": text,
        }
    vk_session.method("messages.send", method_params)
