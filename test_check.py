import boto3
import pytest
from botocore.exceptions import ClientError


@pytest.fixture(scope="session")
def iam_client():
    return boto3.client("iam")


@pytest.fixture(scope="session")
def cfn_client():
    return boto3.client("cloudformation")


@pytest.fixture(scope="session")
def s3_client():
    return boto3.client("s3")


@pytest.fixture(scope="session")
def ec2_client():
    # Uses the default region from AWS_REGION / AWS_DEFAULT_REGION
    return boto3.client("ec2")


def test_there_is_at_least_one_iam_user(iam_client):
    """
    Ensure there is at least one IAM user in the account,
    meaning root is not the only identity.
    """
    try:
        paginator = iam_client.get_paginator("list_users")
        users = []
        for page in paginator.paginate():
            users.extend(page.get("Users", []))
    except ClientError as e:
        pytest.fail(f"Failed to list IAM users: {e}")

    assert len(users) > 0, "Expected at least one IAM user, but none were found."


def test_there_is_at_least_one_cloudformation_stack(cfn_client):
    """
    Ensure there is at least one CloudFormation stack (in any non-deleted state).
    """
    try:
        paginator = cfn_client.get_paginator("list_stacks")
        stacks = []
        for page in paginator.paginate(
            StackStatusFilter=[
                "CREATE_COMPLETE",
                "UPDATE_COMPLETE",
            ]
        ):
            stacks.extend(page.get("StackSummaries", []))
    except ClientError as e:
        pytest.fail(f"Failed to list CloudFormation stacks: {e}")

    assert len(stacks) > 0, "Expected at least one CloudFormation stack, but none were found."


def test_there_is_at_least_one_s3_bucket(s3_client):
    """
    Ensure there is at least one S3 bucket in the account.
    """
    try:
        response = s3_client.list_buckets()
        buckets = response.get("Buckets", [])
    except ClientError as e:
        pytest.fail(f"Failed to list S3 buckets: {e}")

    assert len(buckets) > 0, "Expected at least one S3 bucket, but none were found."


def test_there_is_at_least_one_ec2_instance(ec2_client):
    """
    Ensure there is at least one EC2 instance in the region.
    """
    try:
        paginator = ec2_client.get_paginator("describe_instances")
        instance_count = 0
        for page in paginator.paginate():
            for reservation in page.get("Reservations", []):
                instance_count += len(reservation.get("Instances", []))
    except ClientError as e:
        pytest.fail(f"Failed to describe EC2 instances: {e}")

    assert (
        instance_count > 0
    ), "Expected at least one EC2 instance in this region, but none were found."
