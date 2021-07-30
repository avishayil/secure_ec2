"""Main module."""
from secure_ec2.src.api import (
    create_security_group,
    get_default_vpc,
    get_latest_ami,
    get_subnet_id,
    provision_ec2_instance,
)


def main_(
    os_type: str,
    num_instances: int,
    keypair: str,
    instance_type: str,
    profile: str = None,
    region: str = "us-east-1",
) -> None:
    image_id = get_latest_ami(os_type=os_type, profile=profile, region=region)
    vpc_id = get_default_vpc(profile=profile, region=region)
    subnet_id = get_subnet_id(profile=profile, region=region)
    security_group_id = create_security_group(
        vpc_id=vpc_id, os_type=os_type, profile=profile, region=region
    )
    instance_id = provision_ec2_instance(
        image_id=image_id,
        subnet_id=subnet_id,
        security_group_id=security_group_id,
        keypair=keypair,
        instance_type=instance_type,
        num_instances=num_instances,
        profile=profile,
        region=region,
    )
    return instance_id
