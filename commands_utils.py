def is_command(text: str, command: str) -> bool:
    if text is None:
        return False
    msg_split = text.strip().split()
    return len(msg_split) != 0 and text.strip().split()[0] == ("/" + command)
