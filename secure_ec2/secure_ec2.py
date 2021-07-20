"""Main module."""
from secure_ec2.src.aws import (
    create_security_group,
    get_default_vpc,
    get_latest_ami,
    get_subnet_id,
    provision_ec2_instance,
)


def main_(os_type: str, num_instances: int, keypair: str, instance_type: str):
    image_id = get_latest_ami(os_type=os_type)
    vpc_id = get_default_vpc()
    subnet_id = get_subnet_id()
    security_group_id = create_security_group(vpc_id=vpc_id, os_type=os_type)
    provision_ec2_instance(
        image_id=image_id,
        subnet_id=subnet_id,
        security_group_id=security_group_id,
        keypair=keypair,
        instance_type=instance_type,
        num_instances=num_instances,
    )
