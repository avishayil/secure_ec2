import logging
import sys

import boto3
from botocore.config import Config

from secure_ec2.src.helpers import get_logger

logger = get_logger()


def get_boto3_client(
    service: str, profile: str = None, region: str = "us-east-1"
) -> boto3.Session.client:
    """Get a boto3 client for a given service"""
    logging.getLogger("botocore").setLevel(logging.CRITICAL)
    session_data = {"region_name": region}
    if profile:
        session_data["profile_name"] = profile
    session = boto3.Session(**session_data)
    if is_regional_service(service) and region not in get_available_regions(service):
        logger.debug(f"The service {service} is not available in this region!")
        sys.exit()
    config = Config(read_timeout=5, connect_timeout=5, retries={"max_attempts": 10})
    client = session.client(service, config=config)
    logger.debug(
        f"{client.meta.endpoint_url} in {client.meta.region_name}: boto3 client login successful"
    )
    return client


def get_boto3_resource(
    service: str, profile: str = None, region: str = "us-east-1"
) -> boto3.Session.resource:
    """Get a boto3 resource for a given service"""
    logging.getLogger("botocore").setLevel(logging.CRITICAL)
    session_data = {"region_name": region}
    if profile:
        session_data["profile_name"] = profile
    session = boto3.Session(**session_data)

    resource = session.resource(service)
    return resource


def is_regional_service(service: str):
    """Check if a service is in the availble service list via the API and see if it global."""
    return "aws-global" not in boto3.session.Session().get_available_regions(
        service, allow_non_regional=True
    )


def get_available_regions(service: str):
    """AWS exposes their list of regions as an API. Gather the list."""
    regions = boto3.session.Session().get_available_regions(service)
    logger.debug(
        "The service %s does not have available regions. Returning us-east-1 as default"
    )
    if not regions:
        regions = ["us-east-1"]
    return regions


def get_current_account_id(sts_client: boto3.client) -> str:
    """Invoke API call to get the account id from the current boto3 session."""
    return sts_client.get_caller_identity().get("Account")


def construct_session_manager_url(instance_id: str, region: str = "us-east-1") -> str:
    """Assemble the AWS console session manager url with the current instance id and region."""
    session_manager_url = f"https://{region}.console.aws.amazon.com/systems-manager/session-manager/{instance_id}?region={region}"  # noqa: E501
    return session_manager_url


def construct_console_connect_url(instance_id: str, region: str = "us-east-1") -> str:
    """Assemble the AWS console instance connect url with the current instance id and region."""
    instance_connect_url = f"https://console.aws.amazon.com/ec2/v2/home?region={region}#ConnectToInstance:instanceId={instance_id}"  # noqa: E501
    return instance_connect_url


def get_region_from_boto3_client(boto3_client: boto3.client):
    current_region = boto3_client.meta.region_name
    return current_region
