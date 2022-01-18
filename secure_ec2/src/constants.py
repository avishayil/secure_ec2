MODULE_NAME = "secure_ec2"
LAUNCH_TEMPLATE_SUFFIX = "tpl"
SSM_ROLE_NAME = "SessionManagerInstanceProfile"
AMAZON_AMI_OWNER_ID = "801119661308"
EC2_TRUST_RELATIONSHIP = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {"Service": "ec2.amazonaws.com"},
            "Action": "sts:AssumeRole",
        }
    ],
}
