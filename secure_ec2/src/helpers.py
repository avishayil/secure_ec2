"""Helper methods that secure_ec2 use, mostly used to do offline and non-cloud calculations."""

import getpass
import re

import requests
from halo import Halo

from secure_ec2.src.constants import (
    LAUNCH_TEMPLATE_SUFFIX,
    MODULE_NAME,
    MetadataOptions,
)


def get_connection_port(os_type: str) -> int:
    """Get default connection port per the OS type."""
    if os_type.lower() == "windows":
        return 3389
    else:
        return 22


def get_username() -> str:
    """Get the current computer user in lowercase safe format."""
    formatted_user_name = re.sub("[^a-zA-Z0-9 -]", "", f"{getpass.getuser().lower()}")
    return formatted_user_name


@Halo(text="Discovering endpoint public IP address\r\n", spinner="dots")
def get_ip_address() -> str:
    """Get the public IP address of the computer."""
    ip_address = requests.get("http://checkip.amazonaws.com").text.rstrip()
    return ip_address


def get_os_regex(os_type: str) -> str:
    """Get the regex by operating system."""
    if os_type.lower() == "windows":
        os_regex = "Windows_Server-2019-English-Full-Base-*"
    elif os_type.lower() == "linux":
        os_regex = "amzn2-ami-hvm-2.0*"
    else:
        os_regex = "Windows_Server-2016-English-Nano-Base-2017.10.13"
    return os_regex


def get_launch_template_name(os_type: str) -> str:
    """Build the launch template name by concatenating the username and suffix."""
    local_username = get_username()
    return f"{local_username}-{MODULE_NAME}-{os_type.lower()}-{LAUNCH_TEMPLATE_SUFFIX}"


def normalize_metadata_options(value) -> MetadataOptions:
    """Normalize a string / enum into a MetadataOptions member.

    Accepts a MetadataOptions instance (returned as-is) or a string matching
    an enum value ("v2", "v1v2", "disabled"), case-insensitively.
    """
    if isinstance(value, MetadataOptions):
        return value
    try:
        return MetadataOptions(str(value).strip().lower())
    except ValueError as error:
        raise ValueError(
            f"{value!r} is not a valid IMDS metadata option. "
            f"Expected one of: {[option.value for option in MetadataOptions]}"
        ) from error


def build_metadata_options(metadata_options: MetadataOptions) -> dict:
    """Translate a MetadataOptions member into an EC2 LaunchTemplate MetadataOptions block.

    IMDSv2 is enforced (HttpTokens=required) for every option except V1ANDV2,
    and the IMDS endpoint is disabled entirely for DISABLED.
    """
    metadata_options = normalize_metadata_options(metadata_options)
    is_disabled = metadata_options == MetadataOptions.DISABLED
    accepts_v1 = metadata_options == MetadataOptions.V1ANDV2
    return {
        "HttpEndpoint": "disabled" if is_disabled else "enabled",
        "HttpTokens": "optional" if accepts_v1 else "required",
        "HttpPutResponseHopLimit": 1,
    }
