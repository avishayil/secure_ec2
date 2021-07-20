"""Console script for secure_ec2."""
import sys

import click
from PyInquirer import Token, ValidationError, Validator, prompt, style_from_dict

from secure_ec2.secure_ec2 import main_
from secure_ec2.src.aws import get_key_pairs
from secure_ec2.src.utils import init_logger

style = style_from_dict(
    {
        Token.QuestionMark: "#E91E63 bold",
        Token.Selected: "#673AB7 bold",
        Token.Instruction: "",
        Token.Answer: "#2196f3 bold",
        Token.Question: "",
    }
)


class NumberValidator(Validator):
    def validate(self, document):
        try:
            int(document.text)
        except ValueError:
            raise ValidationError(
                message="Please enter a number", cursor_position=len(document.text)
            )


@click.command()
@click.option(
    "-p", "--os_type", is_flag=False, help="Operating system (Linux / Windows)"
)
@click.option(
    "-s",
    "--num_instances",
    is_flag=False,
    help="Number of instances to provision securely",
    type=click.INT,
)
@click.option(
    "-v", "--keypair", is_flag=False, help="Keypair name to launch the instance with"
)
@click.option(
    "-t",
    "--instance_type",
    is_flag=False,
    help="Instance type, affects compute & networking performance",
)
def main(os_type: str, num_instances: str, keypair: str, instance_type: str):
    """Tool to launch EC2 instances with secure parameters"""

    init_logger()

    if os_type and num_instances and keypair and instance_type:
        main_(
            os_type=os_type,
            num_instances=num_instances,
            keypair=keypair,
            instance_type=instance_type,
        )
        click.echo("Instance created successfully")
        sys.exit(0)
    else:
        try:
            keypairs = get_key_pairs()
        except Exception:
            click.echo("Error getting key pairs")
            sys.exit(1)

        questions = [
            {
                "type": "rawlist",
                "name": "os_type",
                "message": "What type of OS?",
                "choices": ["Windows", "Linux"],
            },
            {
                "type": "rawlist",
                "name": "keypair",
                "message": "KeyPair",
                "choices": keypairs + ["None"],
            },
            {"type": "input", "name": "instance_type", "message": "Instance Type"},
            {
                "type": "input",
                "name": "num_instances",
                "message": "How many instances?",
                "validate": NumberValidator,
                "filter": lambda val: int(val),
            },
        ]
        answers = prompt(questions, style=style)
        if len(answers) > 0:
            main_(
                os_type=answers.get("os_type"),
                num_instances=answers.get("num_instances"),
                keypair=answers.get("keypair"),
                instance_type=answers.get("instance_type"),
            )
            click.echo("Instance created successfully")
            sys.exit(0)
        sys.exit(1)


if __name__ == "__main__":
    main()  # pragma: no cover
