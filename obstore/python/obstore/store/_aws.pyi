from typing import TypedDict, Unpack

import boto3
import boto3.session
import botocore
import botocore.session

from ._client import ClientConfig
from ._retry import RetryConfig

# Note: we removed `bucket` because it overlaps with an existing named arg in the
# constructors
class S3Config(TypedDict, total=False):
    """Configuration parameters returned from [S3Store.config][obstore.store.S3Store.config].

    Note that this is a strict subset of the keys allowed for _input_ into the store,
    see [S3ConfigInput][obstore.store.S3ConfigInput].
    """

    aws_access_key_id: str
    """AWS Access Key"""
    aws_bucket: str
    """Bucket name"""
    aws_checksum_algorithm: str
    """
    Sets the [checksum algorithm] which has to be used for object integrity check during upload.

    [checksum algorithm]: https://docs.aws.amazon.com/AmazonS3/latest/userguide/checking-object-integrity.html
    """
    aws_conditional_put: str
    """
    See [`S3ConfigInput.aws_conditional_put`][obstore.store.S3ConfigInput.aws_conditional_put].
    """
    aws_container_credentials_relative_uri: str
    """
    See [`S3ConfigInput.aws_container_credentials_relative_uri`][obstore.store.S3ConfigInput.aws_container_credentials_relative_uri].
    """
    aws_copy_if_not_exists: str
    """
    See [`S3ConfigInput.aws_copy_if_not_exists`][obstore.store.S3ConfigInput.aws_copy_if_not_exists].
    """
    aws_default_region: str
    """Default region"""
    aws_disable_tagging: bool
    """Disable tagging objects. This can be desirable if not supported by the backing store."""
    aws_endpoint: str
    """Sets custom endpoint for communicating with AWS S3."""
    aws_imdsv1_fallback: str
    """Fall back to ImdsV1"""
    aws_metadata_endpoint: str
    """Set the instance metadata endpoint"""
    aws_region: str
    """Region"""
    aws_request_payer: bool
    """If `True`, enable operations on requester-pays buckets."""
    aws_s3_express: bool
    """Enable Support for S3 Express One Zone"""
    aws_secret_access_key: str
    """Secret Access Key"""
    aws_server_side_encryption: str
    """
    See [`S3ConfigInput.aws_server_side_encryption`][obstore.store.S3ConfigInput.aws_server_side_encryption].
    """
    aws_session_token: str
    """Token to use for requests (passed to underlying provider)"""
    aws_skip_signature: bool
    """If `True`, S3Store will not fetch credentials and will not sign requests."""
    aws_sse_bucket_key_enabled: bool
    """
    If set to `True`, will use the bucket's default KMS key for server-side encryption.
    If set to `False`, will disable the use of the bucket's default KMS key for server-side encryption.
    """
    aws_sse_customer_key_base64: str
    """
    The base64 encoded, 256-bit customer encryption key to use for server-side
    encryption. If set, the server side encryption config value must be `"sse-c"`.
    """
    aws_sse_kms_key_id: str
    """
    The KMS key ID to use for server-side encryption.

    If set, the server side encryption config value must be `"aws:kms"` or `"aws:kms:dsse"`.
    """
    aws_token: str
    """Token to use for requests (passed to underlying provider)"""
    aws_unsigned_payload: bool
    """Avoid computing payload checksum when calculating signature."""
    aws_virtual_hosted_style_request: bool
    """If virtual hosted style request has to be used."""

class S3ConfigInput(TypedDict, total=False):
    access_key_id: str
    """AWS Access Key"""
    aws_access_key_id: str
    """AWS Access Key"""
    aws_bucket_name: str
    """Bucket name"""
    aws_bucket: str
    """Bucket name"""
    aws_checksum_algorithm: str
    """
    Sets the [checksum algorithm] which has to be used for object integrity check during upload.

    [checksum algorithm]: https://docs.aws.amazon.com/AmazonS3/latest/userguide/checking-object-integrity.html
    """
    aws_conditional_put: str
    """Configure how to provide conditional put support

    Supported values:

    - `"etag"`: Supported for S3-compatible stores that support conditional
        put using the standard [HTTP precondition] headers `If-Match` and
        `If-None-Match`.

        [HTTP precondition]: https://datatracker.ietf.org/doc/html/rfc9110#name-preconditions

    - `"dynamo:<TABLE_NAME>"` or `"dynamo:<TABLE_NAME>:<TIMEOUT_MILLIS>"`: The name of a DynamoDB table to use for coordination.

        This will use the same region, credentials and endpoint as configured for S3.
    """
    aws_container_credentials_relative_uri: str
    """Set the container credentials relative URI

    <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task-iam-roles.html>
    """
    aws_copy_if_not_exists: str
    """Configure how to provide "copy if not exists".

    Supported values:

    - `"multipart"`:

        Native Amazon S3 supports copy if not exists through a multipart upload
        where the upload copies an existing object and is completed only if the
        new object does not already exist.

        !!! warning
            When using this mode, `copy_if_not_exists` does not copy tags
            or attributes from the source object.

        !!! warning
            When using this mode, `copy_if_not_exists` makes only a best
            effort attempt to clean up the multipart upload if the copy operation
            fails. Consider using a lifecycle rule to automatically clean up
            abandoned multipart uploads.

    - `"header:<HEADER_NAME>:<HEADER_VALUE>"`:

        Some S3-compatible stores, such as Cloudflare R2, support copy if not exists
        semantics through custom headers.

        If set, `copy_if_not_exists` will perform a normal copy operation with the
        provided header pair, and expect the store to fail with `412 Precondition
        Failed` if the destination file already exists.

        For example `header: cf-copy-destination-if-none-match: *`, would set
        the header `cf-copy-destination-if-none-match` to `*`.

    - `"header-with-status:<HEADER_NAME>:<HEADER_VALUE>:<STATUS>"`:

        The same as the header variant above but allows custom status code checking, for
        object stores that return values other than 412.

    - `"dynamo:<TABLE_NAME>"` or `"dynamo:<TABLE_NAME>:<TIMEOUT_MILLIS>"`:

        The name of a DynamoDB table to use for coordination.

        The default timeout is used if not specified. This will use the same region,
        credentials and endpoint as configured for S3.
    """
    aws_default_region: str
    """Default region"""
    aws_disable_tagging: bool
    """Disable tagging objects. This can be desirable if not supported by the backing store."""
    aws_endpoint_url: str
    """Sets custom endpoint for communicating with AWS S3."""
    aws_endpoint: str
    """Sets custom endpoint for communicating with AWS S3."""
    aws_imdsv1_fallback: str
    """Fall back to ImdsV1"""
    aws_metadata_endpoint: str
    """Set the instance metadata endpoint"""
    aws_region: str
    """Region"""
    aws_request_payer: bool
    """If `True`, enable operations on requester-pays buckets."""
    aws_s3_express: bool
    """Enable Support for S3 Express One Zone"""
    aws_secret_access_key: str
    """Secret Access Key"""
    aws_server_side_encryption: str
    """Type of encryption to use.

    If set, must be one of:

    - `"AES256"` (SSE-S3)
    - `"aws:kms"` (SSE-KMS)
    - `"aws:kms:dsse"` (DSSE-KMS)
    - `"sse-c"`
    """
    aws_session_token: str
    """Token to use for requests (passed to underlying provider)"""
    aws_skip_signature: bool
    """If `True`, S3Store will not fetch credentials and will not sign requests."""
    aws_sse_bucket_key_enabled: bool
    """
    If set to `True`, will use the bucket's default KMS key for server-side encryption.
    If set to `False`, will disable the use of the bucket's default KMS key for server-side encryption.
    """
    aws_sse_customer_key_base64: str
    """
    The base64 encoded, 256-bit customer encryption key to use for server-side
    encryption. If set, the server side encryption config value must be `"sse-c"`.
    """
    aws_sse_kms_key_id: str
    """
    The KMS key ID to use for server-side encryption.

    If set, the server side encryption config value must be `"aws:kms"` or `"aws:kms:dsse"`.
    """
    aws_token: str
    """Token to use for requests (passed to underlying provider)"""
    aws_unsigned_payload: bool
    """Avoid computing payload checksum when calculating signature."""
    aws_virtual_hosted_style_request: bool
    """If virtual hosted style request has to be used."""

    bucket_name: str
    """Bucket name"""
    checksum_algorithm: str
    """
    Sets the [checksum algorithm] which has to be used for object integrity check during upload.

    [checksum algorithm]: https://docs.aws.amazon.com/AmazonS3/latest/userguide/checking-object-integrity.html
    """
    conditional_put: str
    """Configure how to provide conditional put support

    Supported values:

    - `"etag"`: Supported for S3-compatible stores that support conditional
        put using the standard [HTTP precondition] headers `If-Match` and
        `If-None-Match`.

        [HTTP precondition]: https://datatracker.ietf.org/doc/html/rfc9110#name-preconditions

    - `"dynamo:<TABLE_NAME>"` or `"dynamo:<TABLE_NAME>:<TIMEOUT_MILLIS>"`: The name of a DynamoDB table to use for coordination.

        This will use the same region, credentials and endpoint as configured for S3.
    """
    copy_if_not_exists: str
    """Configure how to provide "copy if not exists".

    Supported values:

    - `"multipart"`:

        Native Amazon S3 supports copy if not exists through a multipart upload
        where the upload copies an existing object and is completed only if the
        new object does not already exist.

        !!! warning
            When using this mode, `copy_if_not_exists` does not copy tags
            or attributes from the source object.

        !!! warning
            When using this mode, `copy_if_not_exists` makes only a best
            effort attempt to clean up the multipart upload if the copy operation
            fails. Consider using a lifecycle rule to automatically clean up
            abandoned multipart uploads.

    - `"header:<HEADER_NAME>:<HEADER_VALUE>"`:

        Some S3-compatible stores, such as Cloudflare R2, support copy if not exists
        semantics through custom headers.

        If set, `copy_if_not_exists` will perform a normal copy operation with the
        provided header pair, and expect the store to fail with `412 Precondition
        Failed` if the destination file already exists.

        For example `header: cf-copy-destination-if-none-match: *`, would set
        the header `cf-copy-destination-if-none-match` to `*`.

    - `"header-with-status:<HEADER_NAME>:<HEADER_VALUE>:<STATUS>"`:

        The same as the header variant above but allows custom status code checking, for
        object stores that return values other than 412.

    - `"dynamo:<TABLE_NAME>"` or `"dynamo:<TABLE_NAME>:<TIMEOUT_MILLIS>"`:

        The name of a DynamoDB table to use for coordination.

        The default timeout is used if not specified. This will use the same region,
        credentials and endpoint as configured for S3.
    """
    default_region: str
    """Default region"""
    disable_tagging: bool
    """Disable tagging objects. This can be desirable if not supported by the backing store."""
    endpoint_url: str
    """Sets custom endpoint for communicating with AWS S3."""
    endpoint: str
    """Sets custom endpoint for communicating with AWS S3."""
    imdsv1_fallback: str
    """Fall back to ImdsV1"""
    metadata_endpoint: str
    """Set the instance metadata endpoint"""
    region: str
    """Region"""
    request_payer: bool
    """If `True`, enable operations on requester-pays buckets."""
    s3_express: bool
    """Enable Support for S3 Express One Zone"""
    secret_access_key: str
    """Secret Access Key"""
    session_token: str
    """Token to use for requests (passed to underlying provider)"""
    skip_signature: bool
    """If `True`, S3Store will not fetch credentials and will not sign requests."""
    token: str
    """Token to use for requests (passed to underlying provider)"""
    unsigned_payload: bool
    """Avoid computing payload checksum when calculating signature."""
    virtual_hosted_style_request: bool
    """If virtual hosted style request has to be used."""
    ACCESS_KEY_ID: str
    """AWS Access Key"""
    AWS_ACCESS_KEY_ID: str
    """AWS Access Key"""
    AWS_BUCKET_NAME: str
    """Bucket name"""
    AWS_BUCKET: str
    """Bucket name"""
    AWS_CHECKSUM_ALGORITHM: str
    """
    Sets the [checksum algorithm] which has to be used for object integrity check during upload.

    [checksum algorithm]: https://docs.aws.amazon.com/AmazonS3/latest/userguide/checking-object-integrity.html
    """
    AWS_CONDITIONAL_PUT: str
    """Configure how to provide conditional put support

    Supported values:

    - `"etag"`: Supported for S3-compatible stores that support conditional
        put using the standard [HTTP precondition] headers `If-Match` and
        `If-None-Match`.

        [HTTP precondition]: https://datatracker.ietf.org/doc/html/rfc9110#name-preconditions

    - `"dynamo:<TABLE_NAME>"` or `"dynamo:<TABLE_NAME>:<TIMEOUT_MILLIS>"`: The name of a DynamoDB table to use for coordination.

        This will use the same region, credentials and endpoint as configured for S3.
    """
    AWS_CONTAINER_CREDENTIALS_RELATIVE_URI: str
    """Set the container credentials relative URI

    <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task-iam-roles.html>
    """
    AWS_COPY_IF_NOT_EXISTS: str
    """Configure how to provide "copy if not exists".

    Supported values:

    - `"multipart"`:

        Native Amazon S3 supports copy if not exists through a multipart upload
        where the upload copies an existing object and is completed only if the
        new object does not already exist.

        !!! warning
            When using this mode, `copy_if_not_exists` does not copy tags
            or attributes from the source object.

        !!! warning
            When using this mode, `copy_if_not_exists` makes only a best
            effort attempt to clean up the multipart upload if the copy operation
            fails. Consider using a lifecycle rule to automatically clean up
            abandoned multipart uploads.

    - `"header:<HEADER_NAME>:<HEADER_VALUE>"`:

        Some S3-compatible stores, such as Cloudflare R2, support copy if not exists
        semantics through custom headers.

        If set, `copy_if_not_exists` will perform a normal copy operation with the
        provided header pair, and expect the store to fail with `412 Precondition
        Failed` if the destination file already exists.

        For example `header: cf-copy-destination-if-none-match: *`, would set
        the header `cf-copy-destination-if-none-match` to `*`.

    - `"header-with-status:<HEADER_NAME>:<HEADER_VALUE>:<STATUS>"`:

        The same as the header variant above but allows custom status code checking, for
        object stores that return values other than 412.

    - `"dynamo:<TABLE_NAME>"` or `"dynamo:<TABLE_NAME>:<TIMEOUT_MILLIS>"`:

        The name of a DynamoDB table to use for coordination.

        The default timeout is used if not specified. This will use the same region,
        credentials and endpoint as configured for S3.
    """
    AWS_DEFAULT_REGION: str
    """Default region"""
    AWS_DISABLE_TAGGING: bool
    """Disable tagging objects. This can be desirable if not supported by the backing store."""
    AWS_ENDPOINT_URL: str
    """Sets custom endpoint for communicating with AWS S3."""
    AWS_ENDPOINT: str
    """Sets custom endpoint for communicating with AWS S3."""
    AWS_IMDSV1_FALLBACK: str
    """Fall back to ImdsV1"""
    AWS_METADATA_ENDPOINT: str
    """Set the instance metadata endpoint"""
    AWS_REGION: str
    """Region"""
    AWS_REQUEST_PAYER: bool
    """If `True`, enable operations on requester-pays buckets."""
    AWS_S3_EXPRESS: str
    """Enable Support for S3 Express One Zone"""
    AWS_SECRET_ACCESS_KEY: str
    """Secret Access Key"""
    AWS_SERVER_SIDE_ENCRYPTION: str
    """Type of encryption to use.

    If set, must be one of:

    - `"AES256"` (SSE-S3)
    - `"aws:kms"` (SSE-KMS)
    - `"aws:kms:dsse"` (DSSE-KMS)
    - `"sse-c"`
    """
    AWS_SESSION_TOKEN: str
    """Token to use for requests (passed to underlying provider)"""
    AWS_SKIP_SIGNATURE: bool
    """If `True`, S3Store will not fetch credentials and will not sign requests."""
    AWS_SSE_BUCKET_KEY_ENABLED: bool
    """
    If set to `True`, will use the bucket's default KMS key for server-side encryption.
    If set to `False`, will disable the use of the bucket's default KMS key for server-side encryption.
    """
    AWS_SSE_CUSTOMER_KEY_BASE64: str
    """
    The base64 encoded, 256-bit customer encryption key to use for server-side
    encryption. If set, the server side encryption config value must be `"sse-c"`.
    """
    AWS_SSE_KMS_KEY_ID: str
    """
    The KMS key ID to use for server-side encryption.

    If set, the server side encrypting config value must be `"aws:kms"` or `"aws:kms:dsse"`.
    """
    AWS_TOKEN: str
    """Token to use for requests (passed to underlying provider)"""
    AWS_UNSIGNED_PAYLOAD: bool
    """Avoid computing payload checksum when calculating signature."""
    AWS_VIRTUAL_HOSTED_STYLE_REQUEST: bool
    """If virtual hosted style request has to be used."""
    BUCKET_NAME: str
    """Bucket name"""
    BUCKET: str
    """Bucket name"""
    CHECKSUM_ALGORITHM: str
    """
    Sets the [checksum algorithm] which has to be used for object integrity check during upload.

    [checksum algorithm]: https://docs.aws.amazon.com/AmazonS3/latest/userguide/checking-object-integrity.html
    """
    CONDITIONAL_PUT: str
    """Configure how to provide conditional put support

    Supported values:

    - `"etag"`: Supported for S3-compatible stores that support conditional
        put using the standard [HTTP precondition] headers `If-Match` and
        `If-None-Match`.

        [HTTP precondition]: https://datatracker.ietf.org/doc/html/rfc9110#name-preconditions

    - `"dynamo:<TABLE_NAME>"` or `"dynamo:<TABLE_NAME>:<TIMEOUT_MILLIS>"`: The name of a DynamoDB table to use for coordination.

        This will use the same region, credentials and endpoint as configured for S3.
    """
    COPY_IF_NOT_EXISTS: str
    """Configure how to provide "copy if not exists".

    Supported values:

    - `"multipart"`:

        Native Amazon S3 supports copy if not exists through a multipart upload
        where the upload copies an existing object and is completed only if the
        new object does not already exist.

        !!! warning
            When using this mode, `copy_if_not_exists` does not copy tags
            or attributes from the source object.

        !!! warning
            When using this mode, `copy_if_not_exists` makes only a best
            effort attempt to clean up the multipart upload if the copy operation
            fails. Consider using a lifecycle rule to automatically clean up
            abandoned multipart uploads.

    - `"header:<HEADER_NAME>:<HEADER_VALUE>"`:

        Some S3-compatible stores, such as Cloudflare R2, support copy if not exists
        semantics through custom headers.

        If set, `copy_if_not_exists` will perform a normal copy operation with the
        provided header pair, and expect the store to fail with `412 Precondition
        Failed` if the destination file already exists.

        For example `header: cf-copy-destination-if-none-match: *`, would set
        the header `cf-copy-destination-if-none-match` to `*`.

    - `"header-with-status:<HEADER_NAME>:<HEADER_VALUE>:<STATUS>"`:

        The same as the header variant above but allows custom status code checking, for
        object stores that return values other than 412.

    - `"dynamo:<TABLE_NAME>"` or `"dynamo:<TABLE_NAME>:<TIMEOUT_MILLIS>"`:

        The name of a DynamoDB table to use for coordination.

        The default timeout is used if not specified. This will use the same region,
        credentials and endpoint as configured for S3.
    """
    DEFAULT_REGION: str
    """Default region"""
    DISABLE_TAGGING: bool
    """Disable tagging objects. This can be desirable if not supported by the backing store."""
    ENDPOINT_URL: str
    """Sets custom endpoint for communicating with AWS S3."""
    ENDPOINT: str
    """Sets custom endpoint for communicating with AWS S3."""
    IMDSV1_FALLBACK: str
    """Fall back to ImdsV1"""
    METADATA_ENDPOINT: str
    """Set the instance metadata endpoint"""
    REGION: str
    """Region"""
    REQUEST_PAYER: bool
    """If `True`, enable operations on requester-pays buckets."""
    S3_EXPRESS: str
    """Enable Support for S3 Express One Zone"""
    SECRET_ACCESS_KEY: str
    """Secret Access Key"""
    SESSION_TOKEN: str
    """Token to use for requests (passed to underlying provider)"""
    SKIP_SIGNATURE: bool
    """If `True`, S3Store will not fetch credentials and will not sign requests."""
    TOKEN: str
    """Token to use for requests (passed to underlying provider)"""
    UNSIGNED_PAYLOAD: bool
    """Avoid computing payload checksum when calculating signature."""
    VIRTUAL_HOSTED_STYLE_REQUEST: bool
    """If virtual hosted style request has to be used."""

class S3Store:
    """Interface to an Amazon S3 bucket.

    All constructors will check for environment variables. All environment variables
    starting with `AWS_` will be evaluated. Names must match keys from
    [`S3ConfigInput`][obstore.store.S3ConfigInput]. Only upper-case environment
    variables are accepted.

    Some examples of variables extracted from environment:

    - `AWS_ACCESS_KEY_ID` -> access_key_id
    - `AWS_SECRET_ACCESS_KEY` -> secret_access_key
    - `AWS_DEFAULT_REGION` -> region
    - `AWS_ENDPOINT` -> endpoint
    - `AWS_SESSION_TOKEN` -> token
    - `AWS_CONTAINER_CREDENTIALS_RELATIVE_URI` -> <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task-iam-roles.html>
    - `AWS_REQUEST_PAYER` -> set to "true" to permit requester-pays connections.

    **Examples**:

    **Using requester-pays buckets**:

    Pass `request_payer=True` as a keyword argument or have `AWS_REQUESTER_PAYS=True`
    set in the environment.

    **Anonymous requests**:

    Pass `skip_signature=True` as a keyword argument or have `AWS_SKIP_SIGNATURE=True`
    set in the environment.
    """

    def __init__(
        self,
        bucket: str | None = None,
        *,
        prefix: str | None = None,
        config: S3Config | S3ConfigInput | None = None,
        client_options: ClientConfig | None = None,
        retry_config: RetryConfig | None = None,
        **kwargs: Unpack[S3ConfigInput],
    ) -> None:
        """Create a new S3Store.

        Args:
            bucket: The AWS bucket to use.

        Keyword Args:
            prefix: A prefix within the bucket to use for all operations.
            config: AWS Configuration. Values in this config will override values inferred from the environment. Defaults to None.
            client_options: HTTP Client options. Defaults to None.
            retry_config: Retry configuration. Defaults to None.

        Returns:
            S3Store
        """

    @classmethod
    def _from_native(
        cls,
        bucket: str | None = None,
        *,
        prefix: str | None = None,
        config: S3Config | None = None,
        client_options: ClientConfig | None = None,
        retry_config: RetryConfig | None = None,
        **kwargs: Unpack[S3Config],
    ) -> S3Store:
        """Create a new S3Store, using the native AWS SDK to find credentials.

        This supports deeper integration with AWS credentials, including but not limited to:

        - Reading from disk-based authentication such as `~/.aws/profile`, `~/.aws/credentials`.
        - Respecting AWS profiles.
        - Refreshing temporary credentials before expiration.

        !!! warning "Provisional API"
            This is a provisional API and may change in the future.
            If you have any feedback, please [open an issue](https://github.com/developmentseed/obstore/issues/new/choose).

        !!! warning "Pickling class instance not supported"
            For any `S3Store` created via this `_from_native` constructor, any credentials found from the environment are expected to be lost when pickling.

        Args:
            bucket: The AWS bucket to use.

        Keyword Args:
            prefix: A prefix within the bucket to use for all operations.
            config: AWS Configuration. Values in this config will override values inferred from the environment. Defaults to None.
            client_options: HTTP Client options. Defaults to None.
            retry_config: Retry configuration. Defaults to None.

        Returns:
            S3Store
        """
    @classmethod
    def from_session(
        cls,
        session: boto3.session.Session | botocore.session.Session,
        bucket: str | None = None,
        *,
        prefix: str | None = None,
        config: S3Config | S3ConfigInput | None = None,
        client_options: ClientConfig | None = None,
        retry_config: RetryConfig | None = None,
        **kwargs: Unpack[S3ConfigInput],
    ) -> S3Store:
        """Construct a new S3Store with credentials inferred from a boto3 Session.

        This can be useful to read S3 credentials from [disk-based credentials sources](https://docs.aws.amazon.com/cli/v1/userguide/cli-configure-files.html).

        !!! note
            This is a convenience function for users who are already using `boto3` or
            `botocore`. If you're not already using `boto3` or `botocore`, use other
            constructors, which do not need `boto3` or `botocore` to be installed.

        !!! note
            This will retrieve "frozen" credentials from the boto3 config. That is, the
            values of `"aws_access_key_id"`, `"aws_secret_access_key"`, and
            `"aws_session_token"` are static and will not be updated. Consider using the
            `from_native` constructor to automatically refresh credentials.

        Examples:

        ```py
        import boto3

        session = boto3.Session()
        store = S3Store.from_session(session, "bucket-name", region="us-east-1")
        ```

        Args:
            session: The boto3.Session or botocore.session.Session to infer credentials from.
            bucket: The AWS bucket to use.

        Keyword Args:
            prefix: A prefix within the bucket to use for all operations.
            config: AWS Configuration. Values in this config will override values inferred from the session. Defaults to None.
            client_options: HTTP Client options. Defaults to None.
            retry_config: Retry configuration. Defaults to None.

        Returns:
            S3Store
        """
    @classmethod
    def from_url(
        cls,
        url: str,
        *,
        config: S3Config | S3ConfigInput | None = None,
        client_options: ClientConfig | None = None,
        retry_config: RetryConfig | None = None,
        **kwargs: Unpack[S3ConfigInput],
    ) -> S3Store:
        """Parse available connection info from a well-known storage URL.

        The supported url schemes are:

        - `s3://<bucket>/<path>`
        - `s3a://<bucket>/<path>`
        - `https://s3.<region>.amazonaws.com/<bucket>`
        - `https://<bucket>.s3.<region>.amazonaws.com`
        - `https://ACCOUNT_ID.r2.cloudflarestorage.com/bucket`

        Args:
            url: well-known storage URL.

        Keyword Args:
            config: AWS Configuration. Values in this config will override values inferred from the url. Defaults to None.
            client_options: HTTP Client options. Defaults to None.
            retry_config: Retry configuration. Defaults to None.


        Returns:
            S3Store
        """

    def __getnewargs_ex__(self): ...
    def __repr__(self) -> str: ...
    @property
    def prefix(self) -> str | None:
        """Get the prefix applied to all operations in this store, if any."""
    @property
    def config(self) -> S3Config:
        """Get the underlying S3 config parameters."""
    @property
    def client_options(self) -> ClientConfig | None:
        """Get the store's client configuration."""
    @property
    def retry_config(self) -> RetryConfig | None:
        """Get the store's retry configuration."""
