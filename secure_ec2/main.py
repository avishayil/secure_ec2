import click

from secure_ec2.commands.config import config
from secure_ec2.commands.launch import launch
from secure_ec2.version import __version__


@click.group(help="CLI tool that helps you to provision EC2 instances securely")
@click.version_option(__version__)
@click.pass_context
def cli():
    pass


cli.add_command(config)
cli.add_command(launch)

if __name__ == "__main__":
    cli()
