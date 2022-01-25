"""Main module for secure_ec2 package."""

import logging
import sys

import click

from secure_ec2 import __version__
from secure_ec2.commands.config import config
from secure_ec2.commands.launch import launch
from secure_ec2.src.base_logger import logger

sys.tracebacklimit = 0


@click.option(
    "-d",
    "--debug",
    is_flag=True,
    help="Print debug logs",
)
@click.group(help="CLI tool that helps you to provision EC2 instances securely")
@click.version_option(__version__)
def cli(debug):
    """Entry point for the secure_ec2 CLI tool."""
    if debug:
        logger.setLevel(logging.DEBUG)
    pass


cli.add_command(config)
cli.add_command(launch)

if __name__ == "__main__":
    cli()
