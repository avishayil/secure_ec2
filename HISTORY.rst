=======
History
=======

0.1.0 (unreleased)
------------------

* Enforce IMDSv2 (HttpTokens=required) on generated launch templates by default, with a
  ``--imds`` option to allow legacy IMDSv1 or disable IMDS entirely when no role is needed (#6)
* Support attaching a pre-defined IAM instance profile at launch time via ``--instance_profile`` (#11)
* Replace the abandoned ``PyInquirer`` with ``InquirerPy`` for the interactive prompts (#22)
* Bump ``requests`` (>=2.32.3), ``boto3`` (>=1.34) and add a modern ``urllib3`` floor for CVE fixes
* Drop exact ``==`` dependency pins in favor of ``>=``/``~=`` ranges
* Support Python 3.9 - 3.13 (dropped 3.6 - 3.8)
* Hardened PyPI publishing with OIDC Trusted Publishing (no long-lived token) and pinned actions
* Added Dependabot for pip and GitHub Actions

0.0.6 (2022-01-26)
------------------

* Added homebrew formula installation instructions
* Better logs handling and visibility
* Clarify version information in the CLI
* Generic fixes, docstrings, subnet id retrieval, pre-commit hooks

0.0.5 (2022-01-18)
------------------

* Allow connection via Session Manager, copying the Session Manager console link to the clipboard
* Create launch templates to create and persist configurations
* Refactor to the app logic

0.0.4 (2021-07-30)
------------------

* Bug fixes and improvements.


0.0.1 (2021-07-12)
------------------

* First release on PyPI.
