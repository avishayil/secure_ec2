"""Launch phase that is invoked from the command line and provisions an EC2 instance."""

import sys

import click
from InquirerPy import prompt
from InquirerPy.validator import NumberValidator

from secure_ec2.src.api import (
    get_key_pairs,
    get_latest_launch_template,
    provision_ec2_instance,
)
from secure_ec2.src.aws import get_boto3_client, get_boto3_resource
from secure_ec2.src.base_logger import logger


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
    "-n",
    "--num_instances",
    is_flag=False,
    help="Number of instances to provision securely",
    type=click.INT,
)
@click.option(
    "-k", "--keypair", is_flag=False, help="Keypair name to launch the instance with"
)
@click.option(
    "-i",
    "--instance_type",
    is_flag=False,
    help="Instance type, affects compute & networking performance",
)
@click.option(
    "-ip",
    "--instance_profile",
    is_flag=False,
    required=False,
    default=None,
    help="Pre-defined IAM instance profile to attach (Session Manager launches only)",
)
@click.option(
    "-nc",
    "--no_clip",
    is_flag=True,
    help="Should we avoid copying the Session Manager URL to the clipboard",
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
def launch(
    os_type: str,
    num_instances: str,
    keypair: str,
    instance_type: str,
    instance_profile: str,
    no_clip: bool,
    profile: str,
    region: str,
):
    """Invoke the launch phase for the selected configuration and launch template properties."""
    ec2_client = get_boto3_client(region=region, profile=profile, service="ec2")
    iam_client = get_boto3_client(region=region, profile=profile, service="iam")
    ec2_resource = get_boto3_resource(region=region, profile=profile, service="ec2")

    keypairs = get_key_pairs(ec2_client=ec2_client)

    if not (num_instances and keypair and instance_type):
        questions = [
            {
                "type": "list",
                "name": "os_type",
                "message": "What type of OS?",
                "choices": ["Windows", "Linux"],
            },
            {
                "type": "input",
                "name": "num_instances",
                "message": "How many instances?",
                "validate": NumberValidator(),
                "filter": lambda val: int(val),
            },
            {
                "type": "list",
                "name": "keypair",
                "message": "Keypair",
                "choices": keypairs + ["None"],
            },
            {
                "type": "input",
                "name": "instance_profile",
                "message": "Pre-defined instance profile (leave blank to auto-create one for Session Manager)",
                "when": lambda result: result["keypair"] == "None",
            },
            {"type": "input", "name": "instance_type", "message": "Instance Type"},
        ]
        answers = prompt(questions)
        launch_template = get_latest_launch_template(
            os_type=answers["os_type"], ec2_client=ec2_client
        )

        if answers:
            logger.info(
                "Provisioning secure EC2 instance with the selected configuration"
            )
            print("Provisioning secure EC2 instance with the selected configuration")

            provision_ec2_instance(
                launch_template=launch_template,
                num_instances=answers["num_instances"],
                keypair=answers["keypair"],
                instance_type=answers["instance_type"],
                instance_profile=answers.get("instance_profile") or None,
                ec2_client=ec2_client,
                iam_client=iam_client,
                ec2_resource=ec2_resource,
                no_clip=no_clip,
            )

            print("Secure instance provisioning completed successfully")
            sys.exit(0)
        sys.exit(1)
    else:
        logger.info("Provisioning secure EC2 instance with the selected configuration")
        print("Provisioning secure EC2 instance with the selected configuration")

        launch_template = get_latest_launch_template(
            os_type=os_type, ec2_client=ec2_client
        )
        provision_ec2_instance(
            launch_template=launch_template,
            num_instances=num_instances,
            keypair=keypair,
            instance_type=instance_type,
            instance_profile=instance_profile,
            ec2_client=ec2_client,
            iam_client=iam_client,
            ec2_resource=ec2_resource,
            no_clip=no_clip,
        )

        print("Secure instance provisioning completed successfully")
        sys.exit(0)
