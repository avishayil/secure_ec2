"""Constant variables that secure_ec2 use."""

from enum import Enum

MODULE_NAME = "secure_ec2"
LAUNCH_TEMPLATE_SUFFIX = "tpl"
SSM_ROLE_NAME = "SessionManagerInstanceProfile"
AMAZON_AMI_OWNER_ID = "801119661308"
EC2_TRUST_RELATIONSHIP = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {"Service": "ec2.amazonaws.com"},
            "Action": "sts:AssumeRole",
        }
    ],
}
LOGGING_FILE_NAME = ".secure_ec2.log"


class MetadataOptions(Enum):
    """Instance Metadata Service (IMDS) options for the launch template.

    V2       -- IMDS enabled, IMDSv2 enforced (HttpTokens=required). Default.
    V1ANDV2  -- IMDS enabled, both IMDSv1 and IMDSv2 accepted (HttpTokens=optional).
    DISABLED -- IMDS endpoint disabled entirely (recommended when no instance role is needed).
    """

    V2 = "v2"
    V1ANDV2 = "v1v2"
    DISABLED = "disabled"


# Default IMDS behavior: enforce IMDSv2 (secure by default).
DEFAULT_METADATA_OPTIONS = MetadataOptions.V2
