ALLOWED_HOSTS = {
    "127.0.0.1",
    "localhost",
}

ALLOWED_ACTIONS = {
    "login",
    "search_member",
    "open_sub_account",
    "create_sub_account",
    "confirm_sub_account",
}

RISKY_ACTIONS = {
    "confirm_sub_account",
}


def check_url(url):
    if not any(host in url for host in ALLOWED_HOSTS):
        raise PermissionError(f"Blocked navigation to unauthorized URL: {url}")


def check_action(action):
    if action not in ALLOWED_ACTIONS:
        raise PermissionError(f"Blocked unauthorized action: {action}")

    if action in RISKY_ACTIONS:
        print(f"WARNING: risky action detected: {action}")
