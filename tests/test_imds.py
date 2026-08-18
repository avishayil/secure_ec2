"""Tests for IMDSv2 enforcement and instance-metadata options on the launch template."""

import pytest

from secure_ec2.src.api import create_launch_template, get_latest_launch_template
from secure_ec2.src.constants import MetadataOptions
from secure_ec2.src.helpers import (
    build_metadata_options,
    normalize_metadata_options,
)


def _get_metadata_options(ec2_client, os_type: str) -> dict:
    """Fetch the MetadataOptions block from the default launch template version."""
    launch_template = get_latest_launch_template(os_type=os_type, ec2_client=ec2_client)
    versions = ec2_client.describe_launch_template_versions(
        LaunchTemplateId=launch_template["LaunchTemplateId"],
        Versions=["$Default"],
    )
    return versions["LaunchTemplateVersions"][0]["LaunchTemplateData"][
        "MetadataOptions"
    ]


def _seed_linux_ami(ec2_client):
    ec2_client.copy_image(
        Name="amzn2-ami-hvm-2.0-test",
        SourceImageId="ami-000c540e28953ace2",
        SourceRegion="us-east-1",
    )


def test_build_metadata_options_v2_enforces_imdsv2():
    """The default V2 option must enforce IMDSv2 (HttpTokens=required, endpoint enabled)."""
    block = build_metadata_options(MetadataOptions.V2)
    assert block["HttpTokens"] == "required"
    assert block["HttpEndpoint"] == "enabled"


def test_build_metadata_options_v1andv2_allows_legacy():
    """V1ANDV2 keeps the endpoint enabled but allows optional tokens (legacy IMDSv1)."""
    block = build_metadata_options(MetadataOptions.V1ANDV2)
    assert block["HttpTokens"] == "optional"
    assert block["HttpEndpoint"] == "enabled"


def test_build_metadata_options_disabled_turns_off_endpoint():
    """DISABLED must turn the IMDS endpoint off entirely."""
    block = build_metadata_options(MetadataOptions.DISABLED)
    assert block["HttpEndpoint"] == "disabled"


def test_normalize_metadata_options_from_string():
    """String values normalize to the matching enum member (case-insensitively)."""
    assert normalize_metadata_options("v2") == MetadataOptions.V2
    assert normalize_metadata_options("V1V2") == MetadataOptions.V1ANDV2
    assert normalize_metadata_options("disabled") == MetadataOptions.DISABLED
    assert normalize_metadata_options(MetadataOptions.V2) == MetadataOptions.V2


def test_normalize_metadata_options_invalid_raises():
    """An unknown IMDS value raises a helpful ValueError."""
    with pytest.raises(ValueError):
        normalize_metadata_options("nonsense")


def test_create_launch_template_enforces_imdsv2_by_default(ec2_client_stub):
    """KEY REGRESSION: provisioning creates a launch template with IMDSv2 enforced."""
    _seed_linux_ami(ec2_client_stub)
    create_launch_template(os_type="linux", ec2_client=ec2_client_stub)

    metadata = _get_metadata_options(ec2_client_stub, "linux")
    assert metadata["HttpTokens"] == "required"
    assert metadata["HttpEndpoint"] == "enabled"


def test_create_launch_template_allows_imdsv1_when_requested(ec2_client_stub):
    """The V1ANDV2 toggle produces a template that also accepts IMDSv1."""
    _seed_linux_ami(ec2_client_stub)
    create_launch_template(
        os_type="linux",
        ec2_client=ec2_client_stub,
        metadata_options=MetadataOptions.V1ANDV2,
    )

    metadata = _get_metadata_options(ec2_client_stub, "linux")
    assert metadata["HttpTokens"] == "optional"
    assert metadata["HttpEndpoint"] == "enabled"


def test_create_launch_template_updates_existing_version_with_imds(ec2_client_stub):
    """Re-running config updates the existing template to a new default version.

    Exercises the 'launch template already exists' branch and confirms the new
    default version still enforces IMDSv2.
    """
    _seed_linux_ami(ec2_client_stub)
    create_launch_template(os_type="linux", ec2_client=ec2_client_stub)
    # Second call hits the AlreadyExists branch -> new version -> modify default.
    create_launch_template(os_type="linux", ec2_client=ec2_client_stub)

    launch_template = get_latest_launch_template(
        os_type="linux", ec2_client=ec2_client_stub
    )
    assert launch_template["LatestVersionNumber"] >= 2

    metadata = _get_metadata_options(ec2_client_stub, "linux")
    assert metadata["HttpTokens"] == "required"


def test_create_launch_template_disables_imds_when_no_role(ec2_client_stub):
    """The DISABLED path (no instance role needed) turns off the IMDS endpoint."""
    _seed_linux_ami(ec2_client_stub)
    create_launch_template(
        os_type="linux",
        ec2_client=ec2_client_stub,
        metadata_options=MetadataOptions.DISABLED,
    )

    metadata = _get_metadata_options(ec2_client_stub, "linux")
    assert metadata["HttpEndpoint"] == "disabled"
