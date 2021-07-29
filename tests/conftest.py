import pytest
from moto import mock_ec2, mock_iam

from secure_ec2.src import helpers


def mock_get_ip_address():
    return "192.168.1.1"


pytest.MonkeyPatch().setattr(helpers, "get_ip_address", mock_get_ip_address)
from secure_ec2.src.aws import get_boto3_client, get_boto3_resource  # noqa: E402


@pytest.fixture(autouse=True)
def ec2_client_stub():
    with mock_ec2():
        ec2_client = get_boto3_client(
            service="ec2", profile="default", region="us-east-1"
        )
        yield ec2_client


@pytest.fixture(autouse=True)
def ec2_resource_stub():
    with mock_ec2():
        ec2_resource = get_boto3_resource(
            service="ec2", profile="default", region="us-east-1"
        )
        yield ec2_resource


@pytest.fixture(autouse=True)
def iam_client_stub():
    with mock_iam():
        iam_client = get_boto3_client(
            service="iam", profile="default", region="us-east-1"
        )
        yield iam_client
