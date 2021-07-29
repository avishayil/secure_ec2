==========
Secure EC2
==========


.. image:: https://img.shields.io/pypi/v/secure_ec2.svg
        :target: https://pypi.python.org/pypi/secure_ec2

.. image:: https://github.com/avishayil/secure_ec2/actions/workflows/test.yml/badge.svg
        :target: https://github.com/avishayil/secure_ec2/actions/workflows/test.yml

.. image:: https://readthedocs.org/projects/secure-ec2/badge/?version=latest
        :target: https://secure-ec2.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status
        
.. image:: coverage.svg
        :target: https://coverage.readthedocs.io/
        :alt: Coverage

A project that helps you to provision EC2 instance securely


* Free software: MIT license
* Documentation: https://secure-ec2.readthedocs.io.


TL;DR
--------
Installation:

.. code-block:: bash

    § pip install secure_ec2

Wizard Usage:

.. code-block:: bash

  § secure_ec2

Command Line Usage:

.. code-block:: bash

  § secure_ec2 --os_type Linux --num_instances 3 --keypair None --instance_type t2.micro # Session Manager access
  § secure_ec2 --os_type Windows --num_instances 1 --keypair demo-kp --instance_type t2.micro # SSH access with KeyPair


Features
--------

* Provision EC2 instance with keypair securely
* Provision EC2 instance without keypair (Session Manager access) securely


Demo
----

Linux
=====

.. image:: screenshots/linux.gif
        :alt: Linux Example

Windows
=======

.. image:: screenshots/windows.gif
        :alt: Windows Example


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
