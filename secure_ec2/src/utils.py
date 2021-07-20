import logging

import boto3

ec2_client = boto3.client("ec2")
ec2_resource = boto3.resource("ec2")
sts_client = boto3.client("sts")
iam_client = boto3.client("iam")


def init_logger():
    """Initializing a logger instance
    Args:
    Returns:
        logger instance
    Raises:
        None
    """

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler("debug.log")
    file_handler.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    return logger


def get_logger():
    """Returning the logger instance
    Args:
    Returns:
        logger instance
    Raises:
        None
    """
    logger = logging.getLogger(__name__)
    return logger
