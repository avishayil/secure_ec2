=====
Usage
=====

Example for launching a Linux instance with Keypair:

.. code-block:: bash

    § secure_ec2 launch

      ? What type of OS?  Linux
      ? How many instances?  1
      ? Keypair  demo-kp
      ? Instance Type  t2.micro

Example for launching a Windows instance with Session Manager access:

.. code-block:: bash

    § secure_ec2 launch

      ? What type of OS?  Windows
      ? How many instances?  1
      ? Keypair  None
      ? Instance Type  t2.micro

Command Line Usage:

.. code-block:: bash

  § secure_ec2 config -t Linux # Generate launch template for Linux instances
  § secure_ec2 config -t Windows # Generate launch template for Windows instances
  § secure_ec2 launch -t Linux -n 3 -k None -i t2.micro # Provision 3 Linux instance with Session Manager access
  § secure_ec2 launch -t Windows -n 1 -k demo-kp -i t2.micro # Provision a Windows instance with Keypair
