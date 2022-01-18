import json
from operator import itemgetter
from typing import Any

import boto3
import click
import pyperclip
from botocore.exceptions import ClientError
from halo import Halo

from secure_ec2.src.aws import (
    construct_console_connect_url,
    construct_session_manager_url,
    get_region_from_boto3_client,
)
from secure_ec2.src.constants import (
    AMAZON_AMI_OWNER_ID,
    EC2_TRUST_RELATIONSHIP,
    MODULE_NAME,
    SSM_ROLE_NAME,
)
from secure_ec2.src.helpers import (
    get_connection_port,
    get_ip_address,
    get_launch_template_name,
    get_logger,
    get_os_regex,
    get_username,
)

logger = get_logger()


def create_ssm_instance_profile(iam_client: boto3.client) -> str:
    with Halo(text="Creating IAM role for Session Manager\r\n", spinner="dots"):
        logger.debug("Creating IAM Role for Session Manager")
        try:
            create_role_response = iam_client.create_role(
                RoleName=SSM_ROLE_NAME,
                AssumeRolePolicyDocument=json.dumps(EC2_TRUST_RELATIONSHIP),
                Description="IAM Role for connecting to EC2 instance with Session Manager",
            )
            logger.debug("IAM Role for Session Manager created successfully")
        except ClientError as error:
            if error.response["Error"]["Code"] != "EntityAlreadyExists":
                logger.error("Unable to create IAM Role for Session Manager")
                raise Exception("Unable to create IAM Role for Session Manager", error)
            else:
                logger.debug("IAM Role for Session Manager already exists, proceeding")
                return SSM_ROLE_NAME

    with Halo(text="Attaching SSM policy to role\r\n", spinner="dots"):
        logger.debug("Attaching SSM policy to role")
        try:
            iam_client.attach_role_policy(
                RoleName=create_role_response["Role"]["RoleName"],
                PolicyArn="arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore",
            )
            logger.debug("Attached SSM policy to role successfully")
        except ClientError as error:
            logger.error("Unable to attach SSM policy to role")
            raise Exception("Unable to attach SSM policy to role", error)

    with Halo(text="Creating instance profile\r\n", spinner="dots"):
        logger.debug("Creating instance profile")
        iam_client.create_instance_profile(InstanceProfileName=SSM_ROLE_NAME)

    with Halo(text="Attaching instance profile to IAM role\r\n", spinner="dots"):
        logger.debug("Attaching instance profile to IAM role")
        try:
            iam_client.add_role_to_instance_profile(
                InstanceProfileName=SSM_ROLE_NAME, RoleName=SSM_ROLE_NAME
            )
            logger.debug("Attached instance profile to IAM role successfully")
        except ClientError as error:
            logger.error("Unable to attach instance profile to IAM role")
            raise Exception("Unable to attach instance profile to IAM role", error)
    return SSM_ROLE_NAME


def get_key_pairs(ec2_client: boto3.client) -> list:
    key_pair_list = []
    with Halo(text="Getting keypairs\r\n", spinner="dots"):
        logger.debug("Getting keypairs")
        try:
            describe_key_pairs_response = ec2_client.describe_key_pairs()
        except ClientError as error:
            raise Exception("Error utilizing AWS credentials", error)
    for key_pair in describe_key_pairs_response.get("KeyPairs"):
        key_pair_list.append(key_pair.get("KeyName"))
    return key_pair_list


def get_subnet_id(ec2_client: boto3.client) -> str:
    with Halo(text="Getting subnet\r\n", spinner="dots"):
        logger.debug("Getting subnet")
        try:
            describe_subnets_response = ec2_client.describe_subnets()
        except ClientError as error:
            logger.error("Error getting subnet", error)
            raise Exception("Error getting subnet", error)

        return describe_subnets_response["Subnets"][-1]["SubnetId"]


def get_default_vpc(ec2_client: boto3.client) -> str:
    with Halo(text="Looking for default VPC\r\n", spinner="dots"):
        logger.debug("Looking for default VPC")
        try:
            vpcs_response = ec2_client.describe_vpcs(
                Filters=[
                    {"Name": "isDefault", "Values": ["true"]},
                ],
            )
        except ClientError as error:
            logger.error("Error looking for default VPC", error)
            raise Exception("Error looking for default VPC", error)
        return vpcs_response["Vpcs"][0]["VpcId"]


def create_security_group(vpc_id: str, os_type: str, ec2_client: boto3.client) -> Any:
    security_group_name = f"{get_username()}-sg"

    with Halo(text="Creating security group\r\n", spinner="dots"):
        logger.debug("Creating security group")
        logger.debug("Describing current security groups")
        try:
            describe_security_groups_response = ec2_client.describe_security_groups(
                GroupNames=[
                    security_group_name,
                ]
            )
        except ClientError as error:
            if error.response["Error"]["Code"] == "InvalidGroup.NotFound":
                logger.debug(
                    f"Security group {security_group_name} not found, Trying to create new security group"
                )
                try:
                    create_security_group_response = ec2_client.create_security_group(
                        Description=f"Security group allowing access from {get_username()} laptop",
                        GroupName=security_group_name,
                        VpcId=vpc_id,
                    )
                    logger.debug(
                        f"Security group {security_group_name} created successfully"
                    )
                    return create_security_group_response
                except ClientError as error:
                    logger.error("Error creating security group", error)
                    raise Exception("Error creating security group", error)
            else:
                logger.error("Error describing current security groups", error)
                raise Exception("Error describing current security groups", error)

        security_group = describe_security_groups_response["SecurityGroups"][0]
        security_group_id = security_group["GroupId"]
        logger.debug("Authorizing ingress rule")
        try:
            ec2_client.authorize_security_group_ingress(
                GroupId=security_group_id,
                IpPermissions=[
                    {
                        "FromPort": get_connection_port(os_type=os_type),
                        "IpProtocol": "TCP",
                        "IpRanges": [
                            {
                                "CidrIp": f"{get_ip_address()}/32",
                                "Description": f"Access from {get_username()} computer",
                            },
                        ],
                        "ToPort": get_connection_port(os_type=os_type),
                    },
                ],
            )
            return security_group
        except ClientError as error:
            if error.response["Error"]["Code"] == "InvalidPermission.Duplicate":
                logger.debug("Security group rule already exist, proceeding")
                return security_group
            else:
                logger.error("Error authorizing security group ingress", error)
                raise Exception("Error authorizing security group ingress", error)


def get_latest_launch_template(os_type: str, ec2_client: boto3.client) -> Any:
    try:
        ec2_response = ec2_client.describe_launch_templates(
            LaunchTemplateNames=[
                get_launch_template_name(os_type=os_type),
            ],
        )
    except ClientError as error:
        logger.error(
            f"Error fetching launch template {get_launch_template_name(os_type=os_type)}, \
                please make sure that the launch template exist or run `secure_ec2 config` to generate it",
            error,
        )
        raise Exception(
            f"Error fetching launch template {get_launch_template_name(os_type=os_type)}, \
                please make sure that the launch template exist or run `secure_ec2 config` to generate it",
            error,
        )

    return ec2_response["LaunchTemplates"][0]


def get_latest_ami_id(os_type: str, ec2_client: any) -> str:
    os_regex = get_os_regex(os_type=os_type)

    with Halo(text=f"Getting latest {os_type} AMI\r\n", spinner="dots"):
        logger.debug(f"Getting latest {os_type} AMI")
        try:
            response = ec2_client.describe_images(
                Filters=[
                    {
                        "Name": "name",
                        "Values": [
                            os_regex,
                        ],
                    },
                    {
                        "Name": "owner-id",
                        "Values": [
                            AMAZON_AMI_OWNER_ID,
                        ],
                    },
                ],
            )
        except ClientError as error:
            print(error)
            logger.error("Error getting AMI", error)
            raise Exception("Error getting AMI", error)

        # Sort on Creation date Desc
        logger.debug("Sorting AMI results")
        image_details = sorted(
            response["Images"], key=itemgetter("CreationDate"), reverse=True
        )

        ami_id = image_details[0]["ImageId"]
        return ami_id


def create_launch_template(
    os_type: str,
    ec2_client: boto3.client,
) -> Any:
    image_id = get_latest_ami_id(os_type=os_type, ec2_client=ec2_client)
    vpc_id = get_default_vpc(ec2_client=ec2_client)
    subnet_id = get_subnet_id(ec2_client=ec2_client)
    security_group = create_security_group(
        vpc_id=vpc_id, os_type=os_type, ec2_client=ec2_client
    )
    logger.debug("Information gathering completed successfully")
    username = get_username()
    with Halo(text="Creating Launch Template\r\n", spinner="dots"):
        logger.debug("Creating Launch Template")
        try:
            ec2_response = ec2_client.create_launch_template(
                LaunchTemplateName=get_launch_template_name(os_type=os_type),
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
                            "SubnetId": subnet_id,
                            "DeviceIndex": 0,
                            "AssociatePublicIpAddress": True,
                            "Groups": [security_group["GroupId"]],
                        }
                    ],
                    "ImageId": image_id,
                    "Monitoring": {"Enabled": False},
                    "TagSpecifications": [
                        {
                            "ResourceType": "instance",
                            "Tags": [
                                {"Key": "Name", "Value": f"{username}-instance"},
                                {"Key": "Owner", "Value": username},
                            ],
                        },
                    ],
                },
                TagSpecifications=[
                    {
                        "ResourceType": "launch-template",
                        "Tags": [
                            {
                                "Key": "Name",
                                "Value": get_launch_template_name(os_type=os_type),
                            },
                            {"Key": "Owner", "Value": username},
                        ],
                    },
                ],
            )
            logger.debug("Launch template created successfully")
        except ClientError as error:
            if (
                error.response["Error"]["Code"]
                == "InvalidLaunchTemplateName.AlreadyExistsException"
            ):
                logger.debug("Launch template already exist, deploying new version")
                try:
                    ec2_response = ec2_client.create_launch_template_version(
                        LaunchTemplateName=get_launch_template_name(os_type=os_type),
                        VersionDescription=f"Secure launch template for {username}",
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
                                    "SubnetId": subnet_id,
                                    "DeviceIndex": 0,
                                    "AssociatePublicIpAddress": True,
                                    "Groups": [security_group["GroupId"]],
                                }
                            ],
                            "ImageId": image_id,
                            "Monitoring": {"Enabled": False},
                            "TagSpecifications": [
                                {
                                    "ResourceType": "instance",
                                    "Tags": [
                                        {
                                            "Key": "Name",
                                            "Value": f"{username}-instance",
                                        },
                                        {"Key": "Owner", "Value": username},
                                    ],
                                },
                            ],
                        },
                    )
                except ClientError as error:
                    logger.error("Error creating launch template version", error)
                    raise Exception("Error creating launch template version", error)
                logger.debug("Launch template version created successfully")
                launch_template_version = ec2_response["LaunchTemplateVersion"][
                    "VersionNumber"
                ]
                logger.debug(
                    "Updating launch template default version to the latest version"
                )
                try:
                    ec2_response = ec2_client.modify_launch_template(
                        LaunchTemplateName=get_launch_template_name(os_type=os_type),
                        DefaultVersion=str(launch_template_version),
                    )
                except ClientError as error:
                    logger.error(
                        "Error modifying launch template default version", error
                    )
                    raise Exception(
                        "Error modifying launch template default version", error
                    )
                logger.debug("Launch template default version updated successfully")
            else:
                logger.error("Error creating launch template", error)
                raise Exception("Error creating launch template", error)


def provision_ec2_instance(
    launch_template: any,
    num_instances: int,
    keypair: str,
    instance_type: str,
    ec2_client: boto3.client,
    iam_client: boto3.client,
    ec2_resource: boto3.resource,
    no_clip: bool = False,
) -> str:
    if keypair == "None":
        with Halo(text="Provisioning instance with SSM access\r\n", spinner="dots"):
            logger.debug("Provisioning instance with SSM access")
            ec2_response = ec2_client.run_instances(
                LaunchTemplate={
                    "LaunchTemplateName": launch_template["LaunchTemplateName"],
                },
                InstanceType=instance_type,
                MaxCount=num_instances,
                MinCount=num_instances,
            )
            instance_id = ec2_response["Instances"][0]["InstanceId"]
        with Halo(
            text="Waiting for instance to be in running state\r\n", spinner="dots"
        ):
            logger.debug("Waiting for instance to be in running state")
            ec2_resource.Instance(instance_id).wait_until_running()

        with Halo(
            text="Creating SSM instance profile and associating with the instance\r\n",
            spinner="dots",
        ):
            logger.debug(
                "Creating SSM instance profile and associating with the instance"
            )
            logger.debug("Creating SSM instance profile")
            try:
                instance_profile = create_ssm_instance_profile(iam_client=iam_client)
            except ClientError as error:
                logger.error("Error creating SSM instance profile", error)
                raise Exception("Error creating SSM instance profile", error)
            logger.debug("Associating instance profile with the instance")
            try:
                if not no_clip:
                    pyperclip.copy(
                        construct_session_manager_url(
                            instance_id=instance_id,
                            region=get_region_from_boto3_client(
                                boto3_client=ec2_client
                            ),
                        )
                    )
                    click.echo("The link is on your clipboard")
                ec2_client.associate_iam_instance_profile(
                    IamInstanceProfile={"Name": instance_profile},
                    InstanceId=instance_id,
                )
            except ClientError as error:
                logger.error(
                    "Error associating instance profile with the instance", error
                )
                raise Exception(
                    "Error associating instance profile with the instance", error
                )

    else:
        with Halo(text="Provisioning instance with Keypair access\r\n", spinner="dots"):
            logger.debug("Provisioning instance with Keypair access")
            try:
                ec2_response = ec2_client.run_instances(
                    LaunchTemplate={
                        "LaunchTemplateName": launch_template["LaunchTemplateName"],
                    },
                    InstanceType=instance_type,
                    MaxCount=num_instances,
                    MinCount=num_instances,
                    KeyName=keypair,
                )
            except ClientError as error:
                logger.error("Error provisioning instance with Keypair access", error)
                raise Exception(
                    "Error provisioning instance with Keypair access", error
                )
            instance_id = ec2_response["Instances"][0]["InstanceId"]

        with Halo(
            text="Waiting for instance to be in running state\r\n", spinner="dots"
        ):
            logger.debug("Waiting for instance to be in running state")
            ec2_resource.Instance(instance_id).wait_until_running()
        click.echo(
            f"Instance {instance_id} provisioned successfully. Connect securely using SSH / RDP and your KeyPair:\r\n{construct_console_connect_url(instance_id=instance_id, region=get_region_from_boto3_client(boto3_client=ec2_client))}"  # noqa: E501
        )
        if not no_clip:
            pyperclip.copy(
                construct_session_manager_url(
                    instance_id=instance_id,
                    region=get_region_from_boto3_client(boto3_client=ec2_client),
                )
            )
            click.echo("The link is on your clipboard")

    return instance_id
