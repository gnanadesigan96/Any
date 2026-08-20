"""AWS STS assume-role helper.

Rather than using long-lived static credentials directly against S3, a base
IAM identity assumes a (possibly cross-account) role to get short-lived
session credentials - the STS default validity is 1 hour. Since each pipeline
invocation completes in seconds, there's no need to cache or refresh a
session across runs: just assume the role fresh at the start of every
invocation and use that client for the whole run.
"""
from __future__ import annotations

import boto3


def assume_role_s3_client(
    base_access_key_id: str,
    base_secret_access_key: str,
    role_arn: str,
    role_session_name: str,
    external_id: str | None = None,
    region_name: str | None = None,
):
    """Assume `role_arn` using the base credentials and return an S3 client
    scoped to the resulting temporary session credentials."""
    sts_client = boto3.client(
        "sts",
        aws_access_key_id=base_access_key_id,
        aws_secret_access_key=base_secret_access_key,
        region_name=region_name,
    )

    assume_role_kwargs = {"RoleArn": role_arn, "RoleSessionName": role_session_name}
    if external_id:
        assume_role_kwargs["ExternalId"] = external_id

    response = sts_client.assume_role(**assume_role_kwargs)
    credentials = response["Credentials"]

    return boto3.client(
        "s3",
        aws_access_key_id=credentials["AccessKeyId"],
        aws_secret_access_key=credentials["SecretAccessKey"],
        aws_session_token=credentials["SessionToken"],
        region_name=region_name,
    )
