from urllib.parse import urlparse


def get_domain(url: str) -> str:
    return urlparse(url).netloc


def join_lines(*lines_list: str) -> str:
    return "\n\n".join(*lines_list)


# Fixes PEER_ID_INVALID for channels
# https://github.com/pyrogram/pyrogram/issues/1314#issuecomment-2187830732
def get_peer_type_fixed(peer_id: int) -> str:
    peer_id_str = str(peer_id)
    if not peer_id_str.startswith("-"):
        return "user"
    elif peer_id_str.startswith("-100"):
        return "channel"
    else:
        return "chat"
