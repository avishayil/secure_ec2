import logging
import re

from secure_ec2.src.helpers import (
    get_connection_port,
    get_ip_address,
    get_launch_template_name,
    get_logger,
    get_os_regex,
    get_username,
)


def test_get_connection_port():
    windows_connection_port = get_connection_port(os_type="windows")
    linux_connection_port = get_connection_port(os_type="linux")
    assert windows_connection_port == 3389
    assert linux_connection_port == 22


def test_get_username():
    username = get_username()
    assert isinstance(username, str)


def test_get_ip_address():
    ip_address = get_ip_address()
    assert re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", ip_address)


def test_get_os_regex():
    windows_os_regex = get_os_regex(os_type="Windows")
    linux_os_regex = get_os_regex(os_type="Linux")
    assert windows_os_regex == "Windows_Server-2019-English-Full-Base-*"
    assert linux_os_regex == "amzn2-ami-hvm-2.0*"


def test_get_launch_template_name():
    launch_template_name = get_launch_template_name(os_type="Linux")
    assert isinstance(launch_template_name, str)


def test_get_logger():
    logger = get_logger()
    assert isinstance(logger, logging.Logger)
