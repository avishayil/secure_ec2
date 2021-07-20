import getpass
import re

import requests
from halo import Halo


def get_connection_port(os_type: str):
    if os_type.lower() == "windows":
        return 3389
    else:
        return 22


def get_username():
    formatted_user_name = re.sub("[^a-zA-Z0-9 -]", "", f"{getpass.getuser().lower()}")
    return formatted_user_name


def get_ip_address():
    with Halo(text="Getting IP address", spinner="dots"):
        ip_address = requests.get("http://checkip.amazonaws.com").text.rstrip()
        return ip_address
