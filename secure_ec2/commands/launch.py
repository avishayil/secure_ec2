import sys

import click
from PyInquirer import Token, ValidationError, Validator, prompt, style_from_dict

from secure_ec2.src.api import (
    get_key_pairs,
    get_latest_launch_template,
    provision_ec2_instance,
)
from secure_ec2.src.aws import get_boto3_client, get_boto3_resource


class NumberValidator(Validator):
    def validate(self, document):
        try:
            int(document.text)
        except ValueError:
            raise ValidationError(
                message="Please enter a number", cursor_position=len(document.text)
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
    num_instances: str,
    keypair: str,
    instance_type: str,
    profile: str,
    region: str,
):
    ec2_client = get_boto3_client(region=region, profile=profile, service="ec2")
    iam_client = get_boto3_client(region=region, profile=profile, service="iam")
    ec2_resource = get_boto3_resource(region=region, profile=profile, service="ec2")

    style = style_from_dict(
        {
            Token.QuestionMark: "#E91E63 bold",
            Token.Selected: "#673AB7 bold",
            Token.Instruction: "",
            Token.Answer: "#2196f3 bold",
            Token.Question: "",
        }
    )

    keypairs = get_key_pairs(ec2_client=ec2_client)
    launch_template = get_latest_launch_template(ec2_client=ec2_client)

    if not (num_instances and keypair and instance_type):

        questions = [
            {
                "type": "input",
                "name": "num_instances",
                "message": "How many instances?",
                "validate": NumberValidator,
                "filter": lambda val: int(val),
            },
            {
                "type": "rawlist",
                "name": "keypair",
                "message": "KeyPair",
                "choices": keypairs + ["None"],
            },
            {"type": "input", "name": "instance_type", "message": "Instance Type"},
        ]
        answers = prompt(questions, style=style)

        if len(answers) > 0:
            provision_ec2_instance(
                launch_template=launch_template,
                num_instances=answers["num_instances"],
                keypair=answers["keypair"],
                instance_type=answers["instance_type"],
                ec2_client=ec2_client,
                iam_client=iam_client,
                ec2_resource=ec2_resource,
            )
            sys.exit(0)
        sys.exit(1)
    else:
        provision_ec2_instance(
            launch_template=launch_template,
            num_instances=num_instances,
            keypair=keypair,
            instance_type=instance_type,
            ec2_client=ec2_client,
            iam_client=iam_client,
            ec2_resource=ec2_resource,
        )
        sys.exit(0)
