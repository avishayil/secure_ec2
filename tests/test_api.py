from secure_ec2.src.api import (
    create_security_group,
    create_ssm_instance_profile,
    get_default_vpc,
    get_key_pairs,
    get_latest_ami,
    get_subnet_id,
    provision_ec2_instance,
)
from secure_ec2.src.constants import SSM_ROLE_NAME


def test_get_key_pairs(ec2_client_stub):
    key_pairs = get_key_pairs()
    assert isinstance(key_pairs, list)


def test_get_subnet_id(ec2_client_stub):
    subnet_id = get_subnet_id()
    assert isinstance(subnet_id, str)


def test_get_default_vpc(ec2_client_stub):
    vpc_id = get_default_vpc()
    assert isinstance(vpc_id, str)


def test_get_latest_ami(ec2_client_stub):
    image_id = get_latest_ami(os_type="Demo")
    assert isinstance(image_id, str)


def test_create_security_group(ec2_client_stub):
    security_group_id = create_security_group(vpc_id="vpc-123abcd", os_type="Windows")
    assert isinstance(security_group_id, str)


def test_provision_ec2_instance(ec2_client_stub, ec2_resource_stub):
    ec2_client_stub.create_key_pair(KeyName="demo-kp")
    image_id = get_latest_ami(os_type="Demo")
    subnet_id = get_subnet_id()
    security_group_id = create_security_group(vpc_id="vpc-123abcd", os_type="Windows")
    key_pair = get_key_pairs()[0]
    instance_id = provision_ec2_instance(
        image_id=image_id,
        subnet_id=subnet_id,
        security_group_id=security_group_id,
        keypair=key_pair,
        instance_type="t2.micro",
        num_instances=1,
        clip=False,
    )
    assert isinstance(instance_id, str)


def test_create_ssm_instance_profile(iam_client_stub):
    instance_profile = create_ssm_instance_profile()
    assert isinstance(instance_profile, str)
    assert instance_profile == SSM_ROLE_NAME
