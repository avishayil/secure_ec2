from secure_ec2.src.aws import (
    create_security_group,
    create_ssm_instance_profile,
    get_default_vpc,
    get_key_pairs,
    get_latest_ami,
    get_subnet_id,
    provision_ec2_instance,
)
from secure_ec2.src.constants import SSM_ROLE_NAME
from tests.mocks import (
    add_role_to_instance_profile_params,
    add_role_to_instance_profile_response,
    attach_role_policy_params,
    attach_role_policy_response,
    authorize_security_group_ingress_params,
    authorize_security_group_ingress_response,
    create_instance_profile_params,
    create_instance_profile_response,
    create_role_params,
    create_role_response,
    describe_images_params,
    describe_images_response,
    describe_key_pairs_params,
    describe_key_pairs_response,
    describe_security_groups_params,
    describe_security_groups_response,
    describe_subnets_params,
    describe_subnets_response,
    describe_vpcs_params,
    describe_vpcs_response,
    run_instances_params,
    run_instances_response,
)


def test_get_key_pairs(ec2_client_stub):

    ec2_client_stub.add_response(
        "describe_key_pairs", describe_key_pairs_response, describe_key_pairs_params
    )

    key_pairs = get_key_pairs()
    assert isinstance(key_pairs, list)
    assert key_pairs[0] == "demo-kp"


def test_get_subnet_id(ec2_client_stub):

    ec2_client_stub.add_response(
        "describe_subnets", describe_subnets_response, describe_subnets_params
    )

    subnet_id = get_subnet_id()
    assert isinstance(subnet_id, str)


def test_get_default_vpc(ec2_client_stub):

    ec2_client_stub.add_response(
        "describe_vpcs", describe_vpcs_response, describe_vpcs_params
    )

    vpc_id = get_default_vpc()
    assert isinstance(vpc_id, str)


def test_get_latest_ami(ec2_client_stub):

    ec2_client_stub.add_response(
        "describe_images", describe_images_response, describe_images_params
    )

    image_id = get_latest_ami("Linux")
    assert isinstance(image_id, str)


def test_create_security_group(ec2_client_stub):
    ec2_client_stub.add_response(
        "describe_security_groups",
        describe_security_groups_response,
        describe_security_groups_params,
    )
    ec2_client_stub.add_response(
        "authorize_security_group_ingress",
        authorize_security_group_ingress_response,
        authorize_security_group_ingress_params,
    )

    security_group_id = create_security_group(vpc_id="vpc-123abcd", os_type="Linux")
    assert isinstance(security_group_id, str)


def test_provision_ec2_instance(ec2_client_stub, ec2_resource_stub):
    ec2_client_stub.add_response(
        "run_instances", run_instances_response, run_instances_params
    )
    instance_id = provision_ec2_instance(
        image_id="ami-1abcd2e345fg6h78i",
        subnet_id="subnet-abcd12e3",
        security_group_id="sg-1234ab567c89de0g1",
        keypair="demo-kp",
        instance_type="t2.micro",
        num_instances=1,
    )
    assert isinstance(instance_id, str)


def test_create_ssm_instance_profile(iam_client_stub):
    iam_client_stub.add_response(
        "create_role", create_role_response, create_role_params
    )
    iam_client_stub.add_response(
        "attach_role_policy", attach_role_policy_response, attach_role_policy_params
    )
    iam_client_stub.add_response(
        "create_instance_profile",
        create_instance_profile_response,
        create_instance_profile_params,
    )
    iam_client_stub.add_response(
        "add_role_to_instance_profile",
        add_role_to_instance_profile_response,
        add_role_to_instance_profile_params,
    )
    instance_profile = create_ssm_instance_profile()
    assert isinstance(instance_profile, str)
    assert instance_profile == SSM_ROLE_NAME
