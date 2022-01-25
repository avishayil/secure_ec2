"""Tests definition for the AWS methods that secure_ec2 use."""

from secure_ec2.src.aws import (
    get_available_regions,
    get_boto3_client,
    get_boto3_resource,
    get_current_account_id,
    get_region_from_boto3_client,
)


def test_get_ec2_client():
    """Testing the get_boto3_client of ec2 service method."""
    ec2_client = get_boto3_client(service="ec2")
    assert isinstance(ec2_client, object)


def test_get_iam_client():
    """Testing the get_boto3_client of iam service method."""
    iam_client = get_boto3_client(service="iam")
    assert isinstance(iam_client, object)


def test_get_ec2_resource():
    """Testing the get_boto3_resource of ec2 service method."""
    ec2_client = get_boto3_resource(service="ec2")
    assert isinstance(ec2_client, object)


def test_get_available_regions():
    """Testing the get_available_regions method."""
    available_regions = get_available_regions(service="ec2")
    assert isinstance(available_regions, list)


def test_get_current_account_id(sts_client_stub):
    """Testing the get_current_account_id method."""
    current_account_id = get_current_account_id(sts_client=sts_client_stub)
    assert isinstance(current_account_id, str)


def test_get_region_from_boto3_client(ec2_client_stub):
    """Testing the get_region_from_boto3_client method."""
    current_region = get_region_from_boto3_client(boto3_client=ec2_client_stub)
    assert isinstance(current_region, str)
