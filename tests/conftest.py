from unittest.mock import patch

import pytest
from botocore.stub import Stubber

from secure_ec2.src import helpers
from tests.mocks import mock_get_ip_address

pytest.MonkeyPatch().setattr(helpers, "get_ip_address", mock_get_ip_address)
from secure_ec2.src.aws import ec2_client, iam_client  # noqa: E402


@pytest.fixture(autouse=True)
def ec2_client_stub():
    with Stubber(ec2_client) as stubber:
        yield stubber
        stubber.assert_no_pending_responses()


@pytest.fixture(autouse=True)
def ec2_resource_stub():
    with patch("secure_ec2.src.aws.ec2_resource", return_value={}):
        yield


@pytest.fixture(autouse=True)
def iam_client_stub():
    with Stubber(iam_client) as stubber:
        yield stubber
        stubber.assert_no_pending_responses()
