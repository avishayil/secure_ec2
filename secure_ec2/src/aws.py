import logging
import sys

import boto3
from botocore.config import Config

logger = logging.getLogger(__name__)
fh = logging.FileHandler("debug.log")
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)


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


def get_current_account_id() -> str:
    sts_client = get_boto3_client(region="us-east-1", profile="default", service="sts")
    return sts_client.get_caller_identity().get("Account")
