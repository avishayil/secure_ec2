import json
from operator import itemgetter

import boto3
import botocore
from halo import Halo

from secure_ec2.src.constants import EC2_TRUST_RELATIONSHIP, SSM_ROLE_NAME
from secure_ec2.src.helpers import get_connection_port, get_ip_address, get_username

ec2_client = boto3.client("ec2")
ec2_resource = boto3.resource("ec2")
sts_client = boto3.client("sts")
iam_client = boto3.client("iam")


def get_current_account_id():
    return sts_client.get_caller_identity().get("Account")


def create_ssm_instance_profile():
    try:
        with Halo(text="Creating IAM role", spinner="dots"):
            create_role_response = iam_client.create_role(
                RoleName=SSM_ROLE_NAME,
                AssumeRolePolicyDocument=json.dumps(EC2_TRUST_RELATIONSHIP),
                Description="IAM Role for connecting to EC2 instance with Session Manager",
            )

        with Halo(text="Attaching SSM policy to role", spinner="dots"):
            iam_client.attach_role_policy(
                RoleName=create_role_response["Role"]["RoleName"],
                PolicyArn="arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore",
            )

        with Halo(text="Creating instance profile", spinner="dots"):
            iam_client.create_instance_profile(InstanceProfileName=SSM_ROLE_NAME)

        with Halo(text="Attaching instance profile to IAM role", spinner="dots"):
            iam_client.add_role_to_instance_profile(
                InstanceProfileName=SSM_ROLE_NAME, RoleName=SSM_ROLE_NAME
            )
        return SSM_ROLE_NAME

    except botocore.exceptions.ClientError as error:
        if error.response["Error"]["Code"] != "EntityAlreadyExists":
            raise error
        else:
            return SSM_ROLE_NAME


def get_key_pairs():
    key_pair_list = []
    with Halo(text="Getting keypairs", spinner="dots"):
        try:
            describe_key_pairs_response = ec2_client.describe_key_pairs()
        except botocore.exceptions.ClientError as error:
            raise Exception("Error utilizing AWS credentials", error)
    for key_pair in describe_key_pairs_response.get("KeyPairs"):
        key_pair_list.append(key_pair.get("KeyName"))
    return key_pair_list


def get_subnet_id():
    with Halo(text="Getting subnet", spinner="dots"):
        describe_subnets_response = ec2_client.describe_subnets()
        return describe_subnets_response["Subnets"][-1]["SubnetId"]


def get_default_vpc():
    with Halo(text="Looking for default VPC", spinner="dots"):
        vpcs_response = ec2_client.describe_vpcs(
            Filters=[
                {"Name": "isDefault", "Values": ["true"]},
            ],
        )
        return vpcs_response["Vpcs"][0]["VpcId"]


def create_security_group(vpc_id: str, os_type: str):
    security_group_name = f"{get_username()}-sg"

    with Halo(text="Creating security group", spinner="dots"):
        try:
            describe_security_groups_response = ec2_client.describe_security_groups(
                GroupNames=[
                    security_group_name,
                ]
            )

            security_group_id = describe_security_groups_response["SecurityGroups"][0][
                "GroupId"
            ]
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

            except botocore.exceptions.ClientError as error:
                if error.response["Error"]["Code"] != "InvalidPermission.Duplicate":
                    raise error

            return security_group_id
        except botocore.exceptions.ClientError as error:
            if error.response["Error"]["Code"] == "InvalidGroup.NotFound":
                try:
                    create_security_group_response = ec2_client.create_security_group(
                        Description=f"Security group allowing access from {get_username()} laptop",
                        GroupName=security_group_name,
                        VpcId=vpc_id,
                    )
                    return create_security_group_response["GroupId"]
                except botocore.exceptions.ClientError as error:
                    raise error
            else:
                raise error


def get_latest_ami(os_type: str):
    if os_type.lower() == "windows":
        os_regex = "Windows_Server-2019-English-Full-Base-*"
    else:
        os_regex = "amzn2-ami-hvm-2.0*"

    with Halo(text=f"Getting latest {os_type.lower()} AMI", spinner="dots"):
        response = ec2_client.describe_images(
            Filters=[
                {
                    "Name": "name",
                    "Values": [
                        os_regex,
                    ],
                },
            ],
            Owners=["amazon"],
        )

        # Sort on Creation date Desc
        image_details = sorted(
            response["Images"], key=itemgetter("CreationDate"), reverse=True
        )
        ami_id = image_details[0]["ImageId"]
        return ami_id


def provision_ec2_instance(
    image_id: str,
    subnet_id: str,
    security_group_id: str,
    keypair: str,
    instance_type: str,
    num_instances: int,
):
    username = get_username()
    if keypair == "None":
        with Halo(text="Provisioning instance with SSM access", spinner="dots"):
            ec2_response = ec2_client.run_instances(
                BlockDeviceMappings=[
                    {
                        "DeviceName": "/dev/xvda",
                        "Ebs": {
                            "DeleteOnTermination": True,
                            "VolumeSize": 30,
                            "VolumeType": "gp2",
                        },
                    },
                ],
                NetworkInterfaces=[
                    {
                        "SubnetId": subnet_id,
                        "DeviceIndex": 0,
                        "AssociatePublicIpAddress": True,
                        "Groups": [security_group_id],
                    }
                ],
                TagSpecifications=[
                    {
                        "ResourceType": "instance",
                        "Tags": [
                            {"Key": "Name", "Value": f"{username}-instance"},
                            {"Key": "Owner", "Value": username},
                        ],
                    },
                ],
                ImageId=image_id,
                InstanceType="t3.micro",
                MaxCount=num_instances,
                MinCount=num_instances,
                Monitoring={"Enabled": False},
            )
            instance_id = ec2_response["Instances"][0]["InstanceId"]
        with Halo(text="Waiting for instance to be in running state", spinner="dots"):
            ec2_resource.Instance(instance_id).wait_until_running()

        with Halo(
            text="Creating SSM instance profile and associating with the instance",
            spinner="dots",
        ):
            instance_profile = create_ssm_instance_profile()
            ec2_client.associate_iam_instance_profile(
                IamInstanceProfile={"Name": instance_profile}, InstanceId=instance_id
            )

    else:
        with Halo(text="Provisioning instance with KeyPair access", spinner="dots"):
            ec2_response = ec2_client.run_instances(
                BlockDeviceMappings=[
                    {
                        "DeviceName": "/dev/xvda",
                        "Ebs": {
                            "DeleteOnTermination": True,
                            "VolumeSize": 30,
                            "VolumeType": "gp2",
                        },
                    },
                ],
                NetworkInterfaces=[
                    {
                        "SubnetId": subnet_id,
                        "DeviceIndex": 0,
                        "AssociatePublicIpAddress": True,
                        "Groups": [security_group_id],
                    }
                ],
                TagSpecifications=[
                    {
                        "ResourceType": "instance",
                        "Tags": [
                            {"Key": "Name", "Value": f"{get_username()}-instance"},
                            {"Key": "Owner", "Value": get_username()},
                        ],
                    },
                ],
                ImageId=image_id,
                InstanceType=instance_type,
                MaxCount=num_instances,
                MinCount=num_instances,
                Monitoring={"Enabled": False},
                KeyName=keypair,
            )
            instance_id = ec2_response["Instances"][0]["InstanceId"]

        with Halo(text="Waiting for instance to be in running state", spinner="dots"):
            ec2_resource.Instance(instance_id).wait_until_running()

    return instance_id
