=====
Usage
=====

Wizard Usage:

.. code-block:: bash

  § secure_ec2

Command Line Usage:

.. code-block:: bash

  § secure_ec2 --os_type Linux --num_instances 3 --keypair None --instance_type t2.micro # Session Manager access
  § secure_ec2 --os_type Windows --num_instances 1 --keypair demo-kp --instance_type t2.micro # SSH access with Keypair
