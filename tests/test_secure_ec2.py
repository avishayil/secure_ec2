from secure_ec2.secure_ec2 import main_


def test_main_(ec2_client_stub, ec2_resource_stub):
    main_response = main_(
        os_type="Demo",
        num_instances=1,
        keypair="demo-kp",
        instance_type="t2.micro",
    )
    assert isinstance(main_response, str)
