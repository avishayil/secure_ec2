"""Tests for the defensive error-handling branches in the API layer."""

import pytest
from botocore.exceptions import ClientError

from secure_ec2.src.api import (
    create_security_group,
    create_ssm_instance_profile,
    get_default_vpc_id,
    get_key_pairs,
    get_latest_ami_id,
    get_subnet_id,
)
from secure_ec2.src.constants import SSM_ROLE_NAME


def _client_error(
    code: str = "AccessDenied", operation: str = "Describe"
) -> ClientError:
    return ClientError({"Error": {"Code": code, "Message": "boom"}}, operation)


def _raise_client_error(*args, **kwargs):
    raise _client_error()


def test_get_key_pairs_client_error_exits(ec2_client_stub, monkeypatch):
    """A ClientError while listing keypairs exits the program."""
    monkeypatch.setattr(ec2_client_stub, "describe_key_pairs", _raise_client_error)
    with pytest.raises(SystemExit):
        get_key_pairs(ec2_client=ec2_client_stub)


def test_get_subnet_id_client_error_exits(ec2_client_stub, monkeypatch):
    """A ClientError while fetching subnets exits the program."""
    monkeypatch.setattr(ec2_client_stub, "describe_subnets", _raise_client_error)
    with pytest.raises(SystemExit):
        get_subnet_id(vpc_id="vpc-123", ec2_client=ec2_client_stub)


def test_get_default_vpc_client_error_exits(ec2_client_stub, monkeypatch):
    """A ClientError while looking up the default VPC exits the program."""
    monkeypatch.setattr(ec2_client_stub, "describe_vpcs", _raise_client_error)
    with pytest.raises(SystemExit):
        get_default_vpc_id(ec2_client=ec2_client_stub)


def test_get_latest_ami_client_error_exits(ec2_client_stub, monkeypatch):
    """A ClientError while listing AMIs exits the program."""
    monkeypatch.setattr(ec2_client_stub, "describe_images", _raise_client_error)
    with pytest.raises(SystemExit):
        get_latest_ami_id(os_type="Linux", ec2_client=ec2_client_stub)


def test_create_security_group_describe_error_exits(ec2_client_stub, monkeypatch):
    """A non-NotFound ClientError while describing security groups exits the program."""
    monkeypatch.setattr(
        ec2_client_stub, "describe_security_groups", _raise_client_error
    )
    default_vpc_id = get_default_vpc_id(ec2_client=ec2_client_stub)
    with pytest.raises(SystemExit):
        create_security_group(
            vpc_id=default_vpc_id, os_type="Linux", ec2_client=ec2_client_stub
        )


def test_create_ssm_instance_profile_idempotent(iam_client_stub):
    """Creating the SSM instance profile twice returns the existing role name."""
    first = create_ssm_instance_profile(iam_client=iam_client_stub)
    second = create_ssm_instance_profile(iam_client=iam_client_stub)
    assert first == second == SSM_ROLE_NAME
