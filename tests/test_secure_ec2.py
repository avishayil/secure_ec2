from secure_ec2.secure_ec2 import main_


def test_main_(ec2_client_stub, ec2_resource_stub):
    response = main_(
        os_type="Demo",
        num_instances=1,
        keypair="demo-kp",
        instance_type="t2.micro",
        profile="default",
        region="us-east-1",
    )
    print(response)
    # assert isinstance(response, list)
