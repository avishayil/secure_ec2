import datetime
import json

from dateutil.tz import tzutc

from secure_ec2.src.constants import EC2_TRUST_RELATIONSHIP, SSM_ROLE_NAME
from secure_ec2.src.helpers import get_connection_port, get_username


def mock_get_ip_address():
    return "192.168.1.1"


describe_key_pairs_params = {}
describe_key_pairs_response = {
    "KeyPairs": [
        {
            "KeyPairId": "key-12345678901234567",
            "KeyFingerprint": "ea:a9:fc:51:b8:14:db:9d:0a:0c:4b:68:22:a2:a3:83:60:81:03:9c",
            "KeyName": "demo-kp",
            "Tags": [],
        },
        {
            "KeyPairId": "key-98765432109876543",
            "KeyFingerprint": "6b:a6:b4:f4:7d:7f:82:0f:74:65:bf:2f:ea:71:3e:23:a7:18:90:2f",
            "KeyName": "demo2-kp",
            "Tags": [],
        },
        {
            "KeyPairId": "key-01928374656473829",
            "KeyFingerprint": "d8:4f:7a:60:65:eb:fc:be:c3:1b:dc:b8:c1:e5:3a:ed:97:ee:a6:4d",
            "KeyName": "demo3-kp",
            "Tags": [],
        },
    ]
}

describe_subnets_params = {}
describe_subnets_response = {
    "Subnets": [
        {
            "AvailabilityZone": "eu-west-1a",
            "AvailabilityZoneId": "euw1-az3",
            "AvailableIpAddressCount": 4091,
            "CidrBlock": "172.31.32.0/20",
            "DefaultForAz": True,
            "MapPublicIpOnLaunch": True,
            "MapCustomerOwnedIpOnLaunch": False,
            "State": "available",
            "SubnetId": "subnet-abcd12e3",
            "VpcId": "vpc-123abcd",
            "OwnerId": "123456789012",
            "AssignIpv6AddressOnCreation": False,
            "Ipv6CidrBlockAssociationSet": [],
            "SubnetArn": "arn:aws:ec2:eu-west-1:123456789012:subnet/subnet-abcd12e3",
        }
    ],
}

describe_vpcs_params = {
    "Filters": [
        {"Name": "isDefault", "Values": ["true"]},
    ],
}

describe_vpcs_response = {
    "Vpcs": [
        {
            "CidrBlock": "172.31.0.0/16",
            "DhcpOptionsId": "dopt-4782b021",
            "State": "available",
            "VpcId": "vpc-123abcd",
            "OwnerId": "123456789012",
            "InstanceTenancy": "default",
            "CidrBlockAssociationSet": [
                {
                    "AssociationId": "vpc-cidr-assoc-57cc273d",
                    "CidrBlock": "172.31.0.0/16",
                    "CidrBlockState": {"State": "associated"},
                }
            ],
            "IsDefault": True,
        }
    ]
}

describe_images_params = {
    "Filters": [
        {
            "Name": "name",
            "Values": [
                "amzn2-ami-hvm-2.0*",
            ],
        },
    ],
    "Owners": ["amazon"],
}

describe_images_response = {
    "Images": [
        {
            "Architecture": "x86_64",
            "CreationDate": "2019-02-28T03:18:10.000Z",
            "ImageId": "ami-1abcd2e345fg6h78i",
            "ImageLocation": "amazon/amzn2-ami-hvm-2.0.20190228-x86_64-ebs",
            "ImageType": "machine",
            "Public": True,
            "OwnerId": "137112412989",
            "PlatformDetails": "Linux/UNIX",
            "UsageOperation": "RunInstances",
            "State": "available",
            "BlockDeviceMappings": [
                {
                    "DeviceName": "/dev/xvda",
                    "Ebs": {
                        "DeleteOnTermination": True,
                        "SnapshotId": "snap-025720ef1e0103702",
                        "VolumeSize": 8,
                        "VolumeType": "standard",
                        "Encrypted": False,
                    },
                }
            ],
            "Description": "Amazon Linux 2 AMI 2.0.20190228 x86_64 HVM ebs",
            "EnaSupport": True,
            "Hypervisor": "xen",
            "ImageOwnerAlias": "amazon",
            "Name": "amzn2-ami-hvm-2.0.20190228-x86_64-ebs",
            "RootDeviceName": "/dev/xvda",
            "RootDeviceType": "ebs",
            "SriovNetSupport": "simple",
            "VirtualizationType": "hvm",
        }
    ]
}

describe_security_groups_params = {"GroupNames": [f"{get_username()}-sg"]}

describe_security_groups_response = {
    "SecurityGroups": [
        {
            "Description": f"Security group allowing access from {get_username()} laptop",
            "GroupName": f"{get_username()}-sg",
            "IpPermissions": [
                {
                    "FromPort": 22,
                    "IpProtocol": "tcp",
                    "IpRanges": [
                        {
                            "CidrIp": "192.168.1.1/32",
                            "Description": f"Access from {get_username()} computer",
                        }
                    ],
                    "Ipv6Ranges": [],
                    "PrefixListIds": [],
                    "ToPort": 22,
                    "UserIdGroupPairs": [],
                }
            ],
            "OwnerId": "123456789012",
            "GroupId": "sg-1234ab567c89de0g1",
            "IpPermissionsEgress": [
                {
                    "IpProtocol": "-1",
                    "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
                    "Ipv6Ranges": [],
                    "PrefixListIds": [],
                    "UserIdGroupPairs": [],
                }
            ],
            "VpcId": "vpc-123abcd",
        }
    ]
}

authorize_security_group_ingress_params = {
    "GroupId": describe_security_groups_response["SecurityGroups"][0]["GroupId"],
    "IpPermissions": [
        {
            "FromPort": get_connection_port(os_type="Linux"),
            "IpProtocol": "TCP",
            "IpRanges": [
                {
                    "CidrIp": "192.168.1.1/32",
                    "Description": f"Access from {get_username()} computer",
                },
            ],
            "ToPort": get_connection_port(os_type="Linux"),
        },
    ],
}

authorize_security_group_ingress_response = {
    "Return": True,
    "SecurityGroupRules": [
        {
            "SecurityGroupRuleId": "sgr-00a1879f3e54b9e16",
            "GroupId": "sg-1234ab567c89de0g1",
            "GroupOwnerId": "123456789012",
            "IsEgress": False,
            "IpProtocol": "tcp",
            "FromPort": 22,
            "ToPort": 22,
            "CidrIpv4": "192.168.1.1/32",
            "Description": f"Access from {get_username()} computer",
        }
    ],
}

run_instances_params = {
    "BlockDeviceMappings": [
        {
            "DeviceName": "/dev/xvda",
            "Ebs": {
                "DeleteOnTermination": True,
                "VolumeSize": 30,
                "VolumeType": "gp2",
            },
        }
    ],
    "ImageId": "ami-1abcd2e345fg6h78i",
    "InstanceType": "t2.micro",
    "KeyName": "demo-kp",
    "MaxCount": 1,
    "MinCount": 1,
    "Monitoring": {"Enabled": False},
    "NetworkInterfaces": [
        {
            "AssociatePublicIpAddress": True,
            "DeviceIndex": 0,
            "Groups": ["sg-1234ab567c89de0g1"],
            "SubnetId": "subnet-abcd12e3",
        }
    ],
    "TagSpecifications": [
        {
            "ResourceType": "instance",
            "Tags": [
                {"Key": "Name", "Value": f"{get_username()}-instance"},
                {"Key": "Owner", "Value": f"{get_username()}"},
            ],
        }
    ],
}

run_instances_response = {
    "Groups": [],
    "Instances": [
        {
            "AmiLaunchIndex": 0,
            "ImageId": "ami-1abcd2e345fg6h78i",
            "InstanceId": "i-07e9abc13ae4c1dcb",
            "InstanceType": "t2.micro",
            "KeyName": "demo-kp",
            "LaunchTime": datetime.datetime(2021, 7, 18, 21, 56, 19, tzinfo=tzutc()),
            "Monitoring": {"State": "disabled"},
            "Placement": {
                "AvailabilityZone": "eu-west-1b",
                "GroupName": "",
                "Tenancy": "default",
            },
            "Platform": "windows",
            "PrivateDnsName": "ip-172-31-12-178.eu-west-1.compute.internal",
            "PrivateIpAddress": "172.31.12.178",
            "ProductCodes": [],
            "PublicDnsName": "",
            "State": {"Code": 0, "Name": "pending"},
            "StateTransitionReason": "",
            "SubnetId": "subnet-063c0060",
            "VpcId": "vpc-970fccee",
            "Architecture": "x86_64",
            "BlockDeviceMappings": [],
            "ClientToken": "2c8421be-c8f6-43ba-9813-6b0ec9b92e5c",
            "EbsOptimized": False,
            "EnaSupport": True,
            "Hypervisor": "xen",
            "NetworkInterfaces": [
                {
                    "Attachment": {
                        "AttachTime": datetime.datetime(
                            2021, 7, 18, 21, 56, 19, tzinfo=tzutc()
                        ),
                        "AttachmentId": "eni-attach-0c16bb9aa80dc9cc2",
                        "DeleteOnTermination": True,
                        "DeviceIndex": 0,
                        "Status": "attaching",
                        "NetworkCardIndex": 0,
                    },
                    "Description": "",
                    "Groups": [
                        {
                            "GroupName": f"{get_username()}-sg",
                            "GroupId": "sg-1234ab567c89de0g1",
                        }
                    ],
                    "Ipv6Addresses": [],
                    "MacAddress": "02:d1:82:bb:cb:69",
                    "NetworkInterfaceId": "eni-02733716595438d24",
                    "OwnerId": "123456789012",
                    "PrivateDnsName": "ip-172-31-12-178.eu-west-1.compute.internal",
                    "PrivateIpAddress": "172.31.12.178",
                    "PrivateIpAddresses": [
                        {
                            "Primary": True,
                            "PrivateDnsName": "ip-172-31-12-178.eu-west-1.compute.internal",
                            "PrivateIpAddress": "172.31.12.178",
                        }
                    ],
                    "SourceDestCheck": True,
                    "Status": "in-use",
                    "SubnetId": "subnet-063c0060",
                    "VpcId": "vpc-970fccee",
                    "InterfaceType": "interface",
                }
            ],
            "RootDeviceName": "/dev/sda1",
            "RootDeviceType": "ebs",
            "SecurityGroups": [
                {
                    "GroupName": f"{get_username()}-sg",
                    "GroupId": "sg-1234ab567c89de0g1",
                }
            ],
            "SourceDestCheck": True,
            "StateReason": {"Code": "pending", "Message": "pending"},
            "Tags": [
                {"Key": "Name", "Value": f"{get_username()}-instance"},
                {"Key": "Owner", "Value": f"{get_username()}"},
            ],
            "VirtualizationType": "hvm",
            "CpuOptions": {"CoreCount": 1, "ThreadsPerCore": 1},
            "CapacityReservationSpecification": {
                "CapacityReservationPreference": "open"
            },
            "MetadataOptions": {
                "State": "pending",
                "HttpTokens": "optional",
                "HttpPutResponseHopLimit": 1,
                "HttpEndpoint": "enabled",
            },
            "EnclaveOptions": {"Enabled": False},
        }
    ],
    "OwnerId": "123456789012",
    "ReservationId": "r-01871733e1fcccf65",
}

create_role_params = {
    "RoleName": SSM_ROLE_NAME,
    "AssumeRolePolicyDocument": json.dumps(EC2_TRUST_RELATIONSHIP),
    "Description": "IAM Role for connecting to EC2 instance with Session Manager",
}

create_role_response = {
    "Role": {
        "Path": "/",
        "RoleName": "SessionManagerInstanceProfile",
        "RoleId": "AROA4RFNPJUHURXSC7Z44",
        "Arn": "arn:aws:iam::123456789012:role/SessionManagerInstanceProfile",
        "CreateDate": datetime.datetime(2021, 7, 19, 7, 35, 53, tzinfo=tzutc()),
        "AssumeRolePolicyDocument": json.dumps(
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"Service": "ec2.amazonaws.com"},
                        "Action": "sts:AssumeRole",
                    }
                ],
            }
        ),
    }
}

attach_role_policy_params = {
    "RoleName": create_role_response["Role"]["RoleName"],
    "PolicyArn": "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore",
}

attach_role_policy_response = {}

create_instance_profile_params = {"InstanceProfileName": SSM_ROLE_NAME}

create_instance_profile_response = {
    "InstanceProfile": {
        "Path": "/",
        "InstanceProfileName": "SessionManagerInstanceProfile",
        "InstanceProfileId": "AIPA4RFNPJUH63ZYMLWYN",
        "Arn": "arn:aws:iam::123456789012:instance-profile/SessionManagerInstanceProfile",
        "CreateDate": datetime.datetime(2021, 7, 19, 7, 43, 31, tzinfo=tzutc()),
        "Roles": [],
    }
}

add_role_to_instance_profile_params = {
    "InstanceProfileName": SSM_ROLE_NAME,
    "RoleName": SSM_ROLE_NAME,
}

add_role_to_instance_profile_response = {}
