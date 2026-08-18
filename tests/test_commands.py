"""Tests definition for the command invocations that secure_ec2 use."""

from click.testing import CliRunner

from secure_ec2.commands import config as config_module
from secure_ec2.commands import launch as launch_module
from secure_ec2.commands.config import config
from secure_ec2.commands.launch import launch


def test_config_happy_windows(ec2_client_stub):
    """Tests the happy path of Windows EC2 launch template provisioning."""
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
    """Tests the happy path of Linux EC2 launch template provisioning."""
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
    """Tests the happy path of Linux EC2 instance provisioning."""
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
    """Tests the happy path of Windows EC2 instance provisioning."""
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
    """Tests failure when incorrect OS is passed."""
    runner = CliRunner()
    config_result = runner.invoke(
        config,
        ["-t", "Demo"],
    )

    assert config_result.exit_code == 2


def test_launch_happy_linux_ssm(ec2_client_stub):
    """Tests the happy path of Linux EC2 instance provisioning with Session Manager."""
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


def test_config_interactive_prompt_stubbed(ec2_client_stub, monkeypatch):
    """Interactive config path works with the InquirerPy prompt stubbed out."""
    ec2_client_stub.copy_image(
        Name="amzn2-ami-hvm-2.0-test",
        SourceImageId="ami-000c540e28953ace2",
        SourceRegion="us-east-1",
    )

    monkeypatch.setattr(
        config_module,
        "prompt",
        lambda questions: {"os_type": "Linux", "imds": "disabled"},
    )

    runner = CliRunner()
    config_result = runner.invoke(config, [])
    assert config_result.exit_code == 0

    # The stubbed IMDS choice must be reflected on the launch template.
    template = ec2_client_stub.describe_launch_templates()["LaunchTemplates"][0]
    versions = ec2_client_stub.describe_launch_template_versions(
        LaunchTemplateId=template["LaunchTemplateId"], Versions=["$Default"]
    )["LaunchTemplateVersions"]
    metadata = versions[0]["LaunchTemplateData"]["MetadataOptions"]
    assert metadata["HttpEndpoint"] == "disabled"


def test_launch_interactive_prompt_stubbed(ec2_client_stub, monkeypatch):
    """Interactive launch path works with the InquirerPy prompt stubbed out."""
    ec2_client_stub.copy_image(
        Name="amzn2-ami-hvm-2.0-test",
        SourceImageId="ami-000c540e28953ace2",
        SourceRegion="us-east-1",
    )

    runner = CliRunner()
    # Seed the launch template via the non-interactive config path.
    runner.invoke(config, ["-t", "Linux"])

    monkeypatch.setattr(
        launch_module,
        "prompt",
        lambda questions: {
            "os_type": "Linux",
            "num_instances": 1,
            "keypair": "None",
            "instance_profile": "",
            "instance_type": "t2.micro",
        },
    )

    launch_result = runner.invoke(launch, ["-nc"])
    assert launch_result.exit_code == 0


def test_launch_happy_windows_ssm(ec2_client_stub):
    """Tests the happy path of Windows EC2 instance provisioning with Session Manager."""
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
