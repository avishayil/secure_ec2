"""Configuration phase that is invoked from the command line and provisions a launch template."""

import logging
import sys

import click
from InquirerPy import prompt

from secure_ec2.src.api import create_launch_template
from secure_ec2.src.aws import get_boto3_client
from secure_ec2.src.constants import MetadataOptions
from secure_ec2.src.helpers import normalize_metadata_options

logger = logging.getLogger(__name__)

# Human-readable IMDS choices mapped to their MetadataOptions value.
IMDS_CHOICES = [
    {
        "name": "Enforce IMDSv2 only (recommended, secure by default)",
        "value": MetadataOptions.V2.value,
    },
    {
        "name": "Allow legacy IMDSv1 and IMDSv2",
        "value": MetadataOptions.V1ANDV2.value,
    },
    {
        "name": "Disable IMDS entirely (no instance role needed)",
        "value": MetadataOptions.DISABLED.value,
    },
]


@click.option(
    "-t",
    "--os_type",
    type=click.Choice(["Windows", "Linux"], case_sensitive=False),
    required=False,
    default=None,
    is_flag=False,
    help="Operating System",
)
@click.option(
    "-m",
    "--imds",
    type=click.Choice(
        [option.value for option in MetadataOptions], case_sensitive=False
    ),
    required=False,
    default=None,
    is_flag=False,
    help="Instance Metadata Service mode: v2 (enforce IMDSv2), v1v2 (allow legacy), disabled",
)
@click.option(
    "-p",
    "--profile",
    required=False,
    default=None,
    is_flag=False,
    help="AWS profile name to use",
)
@click.option(
    "-r",
    "--region",
    required=False,
    default="us-east-1",
    is_flag=False,
    help="AWS region to use",
)
@click.command()
def config(profile: str, region: str, os_type: str, imds: str):
    """Invoke the configuration phase for the selected operating system."""
    ec2_client = get_boto3_client(region=region, profile=profile, service="ec2")

    if not os_type:
        questions = [
            {
                "type": "list",
                "name": "os_type",
                "message": "What type of OS?",
                "choices": ["Windows", "Linux"],
            },
            {
                "type": "list",
                "name": "imds",
                "message": "Instance Metadata Service (IMDS) configuration?",
                "choices": IMDS_CHOICES,
                "default": MetadataOptions.V2.value,
            },
        ]
        answers = prompt(questions)

        if answers:
            logger.info("Creating launch template with the selected configuration")
            print("Creating launch template with the selected configuration")
            create_launch_template(
                os_type=answers["os_type"].lower(),
                metadata_options=normalize_metadata_options(answers["imds"]),
                ec2_client=ec2_client,
            )
            print(
                "Configuration completed. secure_ec2 is now ready to launch some instances!"
            )
            sys.exit(0)
        sys.exit(1)
    else:
        logger.info("Creating launch template with the selected configuration")
        print("Creating launch template with the selected configuration")
        create_launch_template(
            os_type=os_type.lower(),
            metadata_options=normalize_metadata_options(
                imds or MetadataOptions.V2.value
            ),
            ec2_client=ec2_client,
        )
        print(
            "Configuration completed. secure_ec2 is now ready to launch some instances!"
        )
        sys.exit(0)
