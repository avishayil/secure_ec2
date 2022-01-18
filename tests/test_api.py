from secure_ec2.src.api import (
    create_security_group,
    create_ssm_instance_profile,
    get_default_vpc,
    get_key_pairs,
    get_latest_ami_id,
    get_latest_launch_template,
    get_subnet_id,
    provision_ec2_instance,
)
from secure_ec2.src.constants import MODULE_NAME, SSM_ROLE_NAME
from secure_ec2.src.helpers import get_launch_template_name, get_username


def test_get_key_pairs(ec2_client_stub):
    key_pairs = get_key_pairs(ec2_client=ec2_client_stub)
    assert isinstance(key_pairs, list)


def test_get_subnet_id(ec2_client_stub):
    subnet_id = get_subnet_id(ec2_client=ec2_client_stub)
    assert isinstance(subnet_id, str)


def test_get_default_vpc(ec2_client_stub):
    vpc_id = get_default_vpc(ec2_client=ec2_client_stub)
    assert isinstance(vpc_id, str)


def test_get_latest_ami_id(ec2_client_stub):
    ec2_client_stub.copy_image(
        Name="amzn2-ami-hvm-2.0-test",
        SourceImageId="ami-000c540e28953ace2",
        SourceRegion="us-east-1",
    )
    image_id = get_latest_ami_id(os_type="Linux", ec2_client=ec2_client_stub)
    assert isinstance(image_id, str)


def test_create_security_group(ec2_client_stub):
    security_group = create_security_group(
        vpc_id="vpc-123abcd", os_type="Windows", ec2_client=ec2_client_stub
    )
    assert isinstance(security_group["GroupId"], str)


def test_get_latest_launch_template(ec2_client_stub):
    security_group = create_security_group(
        vpc_id="vpc-123abcd", os_type="Windows", ec2_client=ec2_client_stub
    )
    ec2_client_stub.copy_image(
        Name="amzn2-ami-hvm-2.0-test",
        SourceImageId="ami-000c540e28953ace2",
        SourceRegion="us-east-1",
    )
    username = get_username()
    image_id = get_latest_ami_id(os_type="Linux", ec2_client=ec2_client_stub)
    ec2_client_stub.create_launch_template(
        LaunchTemplateName=get_launch_template_name(os_type="Linux"),
        VersionDescription=f"Secure launch template for {username}, generated by {MODULE_NAME}",
        LaunchTemplateData={
            "BlockDeviceMappings": [
                {
                    "DeviceName": "/dev/xvda",
                    "Ebs": {
                        "Encrypted": True,
                        "DeleteOnTermination": True,
                        "VolumeSize": 30,
                        "VolumeType": "gp2",
                    },
                },
            ],
            "NetworkInterfaces": [
                {
                    "SubnetId": get_subnet_id(ec2_client=ec2_client_stub),
                    "DeviceIndex": 0,
                    "AssociatePublicIpAddress": True,
                    "Groups": [security_group["GroupId"]],
                }
            ],
            "ImageId": image_id,
            "Monitoring": {"Enabled": False},
        },
    )
    launch_template = get_latest_launch_template(
        os_type="Linux", ec2_client=ec2_client_stub
    )
    assert launch_template["LaunchTemplateName"] == get_launch_template_name(
        os_type="Linux"
    )


def test_provision_ec2_instance(ec2_client_stub, iam_client_stub, ec2_resource_stub):
    security_group = create_security_group(
        vpc_id="vpc-123abcd", os_type="Linux", ec2_client=ec2_client_stub
    )
    ec2_client_stub.copy_image(
        Name="amzn2-ami-hvm-2.0-test",
        SourceImageId="ami-000c540e28953ace2",
        SourceRegion="us-east-1",
    )
    ec2_client_stub.create_key_pair(KeyName="demo-kp")
    key_pair = get_key_pairs(ec2_client=ec2_client_stub)[0]
    username = get_username()
    image_id = get_latest_ami_id(os_type="Linux", ec2_client=ec2_client_stub)
    ec2_client_stub.create_launch_template(
        LaunchTemplateName=get_launch_template_name(os_type="Linux"),
        VersionDescription=f"Secure launch template for {username}, generated by {MODULE_NAME}",
        LaunchTemplateData={
            "BlockDeviceMappings": [
                {
                    "DeviceName": "/dev/xvda",
                    "Ebs": {
                        "Encrypted": True,
                        "DeleteOnTermination": True,
                        "VolumeSize": 30,
                        "VolumeType": "gp2",
                    },
                },
            ],
            "NetworkInterfaces": [
                {
                    "SubnetId": get_subnet_id(ec2_client=ec2_client_stub),
                    "DeviceIndex": 0,
                    "AssociatePublicIpAddress": True,
                    "Groups": [security_group["GroupId"]],
                }
            ],
            "ImageId": image_id,
            "Monitoring": {"Enabled": False},
        },
    )
    launch_template = get_latest_launch_template(
        os_type="Linux", ec2_client=ec2_client_stub
    )
    instance_id = provision_ec2_instance(
        launch_template=launch_template,
        keypair=key_pair,
        instance_type="t2.micro",
        num_instances=1,
        no_clip=True,
        ec2_client=ec2_client_stub,
        iam_client=iam_client_stub,
        ec2_resource=ec2_resource_stub,
    )
    assert isinstance(instance_id, str)


def test_create_ssm_instance_profile(iam_client_stub):
    instance_profile = create_ssm_instance_profile(iam_client=iam_client_stub)
    assert isinstance(instance_profile, str)
    assert instance_profile == SSM_ROLE_NAME
