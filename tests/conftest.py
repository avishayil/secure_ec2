"""Define common methods and fixtures that should be shared across testing modules."""

import pytest
from moto import mock_ec2, mock_iam, mock_sts

from secure_ec2.src import constants, helpers


def mock_get_ip_address():
    """Return a static mocked ip address."""
    return "192.168.1.1"


def mock_get_amazon_ami_owner_id():
    """Return a static mocked amazon AMI's owner ID."""
    return "123456789012"


pytest.MonkeyPatch().setattr(helpers, "get_ip_address", mock_get_ip_address)
pytest.MonkeyPatch().setattr(
    constants, "AMAZON_AMI_OWNER_ID", mock_get_amazon_ami_owner_id()
)
from secure_ec2.src.aws import get_boto3_client, get_boto3_resource  # noqa: E402


@pytest.fixture(autouse=True)
def ec2_client_stub():
    """Use moto EC2 client stub in tests instead of a real boto3 client."""
    with mock_ec2():
        ec2_client = get_boto3_client(
            service="ec2",
        )
        yield ec2_client


@pytest.fixture(autouse=True)
def ec2_resource_stub():
    """Use moto EC2 resource stub in tests instead of a real boto3 resource."""
    with mock_ec2():
        ec2_resource = get_boto3_resource(
            service="ec2",
        )
        yield ec2_resource


@pytest.fixture(autouse=True)
def iam_client_stub():
    """Use moto IAM client stub in tests instead of a real boto3 client."""
    with mock_iam():
        iam_client = get_boto3_client(
            service="iam",
        )
        yield iam_client


@pytest.fixture(autouse=True)
def sts_client_stub():
    """Use moto STS client stub in tests instead of a real boto3 client."""
    with mock_sts():
        sts_client = get_boto3_client(
            service="sts",
        )
        yield sts_client
