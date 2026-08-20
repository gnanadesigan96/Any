from moto import mock_aws

from saas_pipeline.aws_auth import assume_role_s3_client


def test_assume_role_s3_client_can_read_write_s3():
    with mock_aws():
        s3_client = assume_role_s3_client(
            base_access_key_id="AKIAEXAMPLEBASE",
            base_secret_access_key="base-secret",
            role_arn="arn:aws:iam::692859928464:role/corestack-enable-linkedaccounts",
            role_session_name="clo",
            external_id="Snps-Corestack",
            region_name="us-east-1",
        )

        s3_client.create_bucket(Bucket="test-bucket")
        s3_client.put_object(Bucket="test-bucket", Key="a.txt", Body=b"hi")

        obj = s3_client.get_object(Bucket="test-bucket", Key="a.txt")
        assert obj["Body"].read() == b"hi"


def test_assume_role_s3_client_without_external_id():
    with mock_aws():
        s3_client = assume_role_s3_client(
            base_access_key_id="AKIAEXAMPLEBASE",
            base_secret_access_key="base-secret",
            role_arn="arn:aws:iam::692859928464:role/some-role-without-external-id",
            role_session_name="clo",
            region_name="us-east-1",
        )

        s3_client.create_bucket(Bucket="test-bucket-2")
        assert s3_client.list_buckets()["Buckets"]
