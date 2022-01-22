import logging
import sys

import click

from secure_ec2.commands.config import config
from secure_ec2.commands.launch import launch

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger_handler = logging.StreamHandler(sys.stdout)
logger_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger_handler.setFormatter(formatter)
logger.addHandler(logger_handler)


@click.group(help="CLI tool that helps you to provision EC2 instances securely")
def cli():
    pass


cli.add_command(config)
cli.add_command(launch)

if __name__ == "__main__":
    cli()
