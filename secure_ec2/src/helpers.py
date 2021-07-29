import getpass
import re

import requests
from halo import Halo


def get_connection_port(os_type: str) -> int:
    """Get default connection port per the OS type"""
    if os_type.lower() == "windows":
        return 3389
    else:
        return 22


def get_username() -> str:
    """Get the current computer user in lowercase safe format"""
    formatted_user_name = re.sub("[^a-zA-Z0-9 -]", "", f"{getpass.getuser().lower()}")
    return formatted_user_name


def get_ip_address() -> str:
    """Get the public IP address of the computer"""
    with Halo(text="Getting IP address", spinner="dots"):
        ip_address = requests.get("http://checkip.amazonaws.com").text.rstrip()
        return ip_address


def get_os_regex(os_type: str) -> str:
    """Get the regex by operating system"""
    if os_type.lower() == "windows":
        os_regex = "Windows_Server-2019-English-Full-Base-*"
    elif os_type.lower() == "linux":
        os_regex = "amzn2-ami-hvm-2.0*"
    else:
        os_regex = "Windows_Server-2016-English-Nano-Base-2017.10.13"
    return os_regex
