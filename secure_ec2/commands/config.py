import sys

import click
from PyInquirer import Token, prompt, style_from_dict

from secure_ec2.src.api import create_launch_template
from secure_ec2.src.aws import get_boto3_client
from secure_ec2.src.helpers import get_logger

logger = get_logger()


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
def config(profile: str, region: str, os_type: str):

    ec2_client = get_boto3_client(region=region, profile=profile, service="ec2")

    if not os_type:

        style = style_from_dict(
            {
                Token.QuestionMark: "#E91E63 bold",
                Token.Selected: "#673AB7 bold",
                Token.Instruction: "",
                Token.Answer: "#2196f3 bold",
                Token.Question: "",
            }
        )

        questions = [
            {
                "type": "rawlist",
                "name": "os_type",
                "message": "What type of OS?",
                "choices": ["Windows", "Linux"],
            }
        ]
        answers = prompt(questions, style=style)

        if len(answers) > 0:
            logger.info("Creating launch template with the selected configuration")
            print("Creating launch template with the selected configuration")
            create_launch_template(
                os_type=answers["os_type"].lower(),
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
            ec2_client=ec2_client,
        )
        print(
            "Configuration completed. secure_ec2 is now ready to launch some instances!"
        )
        sys.exit(0)
