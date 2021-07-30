from click.testing import CliRunner

from secure_ec2.cli import main


def test_cli(ec2_client_stub, ec2_resource_stub):
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["-t", "Demo", "-n", "1", "-k", "demo-kp", "-i", "t2.micro"],
    )

    assert result.exit_code == 0
