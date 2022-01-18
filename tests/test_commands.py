from click.testing import CliRunner

from secure_ec2.commands.config import config
from secure_ec2.commands.launch import launch


def test_config_happy_windows(ec2_client_stub):

    ec2_client_stub.copy_image(
        Name="Windows_Server-2019-English-Full-Base-test",
        SourceImageId="ami-000c540e28953ace2",
        SourceRegion="us-east-1",
    )

    runner = CliRunner()
    config_result = runner.invoke(
        config,
        ["-t", "Windows"],
    )

    assert config_result.exit_code == 0


def test_config_happy_linux(ec2_client_stub):

    ec2_client_stub.copy_image(
        Name="amzn2-ami-hvm-2.0-test",
        SourceImageId="ami-000c540e28953ace2",
        SourceRegion="us-east-1",
    )

    runner = CliRunner()
    config_result = runner.invoke(
        config,
        ["-t", "Linux"],
    )

    assert config_result.exit_code == 0


def test_launch_happy_linux(ec2_client_stub):

    ec2_client_stub.copy_image(
        Name="amzn2-ami-hvm-2.0-test",
        SourceImageId="ami-000c540e28953ace2",
        SourceRegion="us-east-1",
    )

    runner = CliRunner()

    # Run config test to fill a mock launch template

    runner.invoke(
        config,
        ["-t", "Linux"],
    )

    # Run launch test after filling the mock launch template

    launch_result = runner.invoke(
        launch,
        ["-t", "Linux", "-n", "1", "-k", "demo-kp", "-i", "t2.micro", "-nc"],
    )

    assert launch_result.exit_code == 0


def test_launch_happy_windows(ec2_client_stub):

    ec2_client_stub.copy_image(
        Name="Windows_Server-2019-English-Full-Base-test",
        SourceImageId="ami-000c540e28953ace2",
        SourceRegion="us-east-1",
    )

    runner = CliRunner()

    # Run config test to fill a mock launch template

    runner.invoke(
        config,
        ["-t", "Windows"],
    )

    # Run launch test after filling the mock launch template

    launch_result = runner.invoke(
        launch,
        ["-t", "Windows", "-n", "1", "-k", "demo-kp", "-i", "t2.micro", "-nc"],
    )

    assert launch_result.exit_code == 0


def test_config_incorrent_os():

    runner = CliRunner()
    config_result = runner.invoke(
        config,
        ["-t", "Demo"],
    )

    assert config_result.exit_code == 2


def test_launch_happy_linux_ssm(ec2_client_stub):

    ec2_client_stub.copy_image(
        Name="amzn2-ami-hvm-2.0-test",
        SourceImageId="ami-000c540e28953ace2",
        SourceRegion="us-east-1",
    )

    runner = CliRunner()

    # Run config test to fill a mock launch template

    runner.invoke(
        config,
        ["-t", "Linux"],
    )

    # Run launch test after filling the mock launch template

    launch_result = runner.invoke(
        launch,
        ["-t", "Linux", "-n", "1", "-k", "None", "-i", "t2.micro", "-nc"],
    )

    assert launch_result.exit_code == 0


def test_launch_happy_windows_ssm(ec2_client_stub):

    ec2_client_stub.copy_image(
        Name="Windows_Server-2019-English-Full-Base-test",
        SourceImageId="ami-000c540e28953ace2",
        SourceRegion="us-east-1",
    )

    runner = CliRunner()

    # Run config test to fill a mock launch template

    runner.invoke(
        config,
        ["-t", "Windows"],
    )

    # Run launch test after filling the mock launch template

    launch_result = runner.invoke(
        launch,
        ["-t", "Windows", "-n", "1", "-k", "None", "-i", "t2.micro", "-nc"],
    )

    assert launch_result.exit_code == 0
