# Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import aws_cdk.aws_iam as iam
import aws_cdk.core as cdk
import aws_cdk.aws_kms as kms
import aws_cdk.aws_s3 as s3

from .configuration import (
    PROD, TEST, get_logical_id_prefix,
    get_resource_name_prefix,
)


class S3BucketZonesStack(cdk.Stack):
    def __init__(
        self, scope: cdk.Construct, construct_id: str, target_environment: str, deployment_account_id: str, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.target_environment = target_environment
        logical_id_prefix = get_logical_id_prefix()
        resource_name_prefix = get_resource_name_prefix()
        self.removal_policy = cdk.RemovalPolicy.DESTROY
        if (target_environment == PROD or target_environment == TEST):
            self.removal_policy = cdk.RemovalPolicy.RETAIN

        s3_kms_key = self.create_kms_key(
            deployment_account_id,
            logical_id_prefix,
        )
        access_logs_bucket = self.create_access_logs_bucket(
            f'{target_environment}{logical_id_prefix}AccessLogsBucket',
            f'{target_environment.lower()}-{resource_name_prefix}-{self.account}-{self.region}-access-logs',
            s3_kms_key,
        )
        raw_bucket = self.create_data_lake_zone_bucket(
            f'{target_environment}{logical_id_prefix}RawBucket',
            f'{target_environment.lower()}-{resource_name_prefix}-{self.account}-{self.region}-raw',
            access_logs_bucket,
            s3_kms_key,
        )
        conformed_bucket = self.create_data_lake_zone_bucket(
            f'{target_environment}{logical_id_prefix}ConformedBucket',
            f'{target_environment.lower()}-{resource_name_prefix}-{self.account}-{self.region}-conformed',
            access_logs_bucket,
            s3_kms_key,
        )
        purpose_built_bucket = self.create_data_lake_zone_bucket(
            f'{target_environment}{logical_id_prefix}PurposeBuiltBucket',
            f'{target_environment.lower()}-{resource_name_prefix}-{self.account}-{self.region}-purpose-built',
            access_logs_bucket,
            s3_kms_key,
        )
        # Assign resources for export to SSM Parameter Store
        self.s3_kms_key = s3_kms_key
        self.access_logs_bucket = access_logs_bucket
        self.raw_bucket = raw_bucket
        self.conformed_bucket = conformed_bucket
        self.purpose_built_bucket = purpose_built_bucket

    def create_kms_key(self, deployment_account_id, logical_id_prefix) -> kms.Key:
        s3_kms_key = kms.Key(
            self,
            f'{self.target_environment}{logical_id_prefix}KmsKey',
            admins=[iam.AccountPrincipal(self.account)],  # Gives account users admin access to the key
            description='Key used for encrypting Data Lake S3 Buckets',
            removal_policy=self.removal_policy
        )
        # Gives account users and deployment account users access to use the key
        s3_kms_key.add_to_resource_policy(
            iam.PolicyStatement(
                principals=[
                    iam.AccountPrincipal(self.account),
                    iam.AccountPrincipal(deployment_account_id),
                ],
                actions=[
                    'kms:Encrypt',
                    'kms:Decrypt',
                    'kms:ReEncrypt*',
                    'kms:GenerateDataKey*',
                    'kms:DescribeKey',
                ],
                resources=["*"],
            )
        )

        return s3_kms_key

    def create_data_lake_zone_bucket(self, logical_id, bucket_name, access_logs_bucket, s3_kms_key) -> s3.Bucket:
        lifecycle_rules = [
            s3.LifecycleRule(
                enabled=True,
                expiration=cdk.Duration.days(60),
                noncurrent_version_expiration=cdk.Duration.days(30),
            )
        ]
        if self.target_environment == PROD:
            lifecycle_rules = [
                s3.LifecycleRule(
                    enabled=True,
                    expiration=cdk.Duration.days(2555),
                    noncurrent_version_expiration=cdk.Duration.days(90),
                    transitions=[
                        s3.Transition(
                            storage_class=s3.StorageClass.GLACIER,
                            transition_after=cdk.Duration.days(365),
                        )
                    ]
                )
            ]
        bucket = s3.Bucket(
            self,
            id=logical_id,
            access_control=s3.BucketAccessControl.PRIVATE,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            bucket_key_enabled=True,
            bucket_name=bucket_name,
            encryption=s3.BucketEncryption.KMS,
            encryption_key=s3_kms_key,
            lifecycle_rules=lifecycle_rules,
            public_read_access=False,
            removal_policy=self.removal_policy,
            versioned=True,
            object_ownership=s3.ObjectOwnership.OBJECT_WRITER,
            server_access_logs_bucket=access_logs_bucket,
            server_access_logs_prefix=bucket_name,
        )
        bucket.node.add_dependency(s3_kms_key)
        bucket.node.add_dependency(access_logs_bucket)
        bucket.node.add_dependency
        policy_document_statements = [
            iam.PolicyStatement(
                sid='OnlyAllowSecureTransport',
                effect=iam.Effect.DENY,
                principals=[iam.AnyPrincipal()],
                actions=[
                    's3:GetObject',
                    's3:PutObject',
                ],
                resources=[f'{bucket.bucket_arn}/*'],
                conditions=[{'Bool': {'aws:SecureTransport': 'false'}}]
            )
        ]
        # Prevents user deletion of buckets
        if self.target_environment == PROD or self.target_environment == TEST:
            policy_document_statements.append(
                iam.PolicyStatement(
                    sid='BlockUserDeletionOfBucket',
                    effect=iam.Effect.DENY,
                    principals=[iam.AnyPrincipal()],
                    actions=[
                        's3:DeleteBucket',
                    ],
                    resources=[bucket.bucket_arn],
                    conditions=[{'StringLike': {'aws:userId': f'arn:aws:iam::{self.account}:user/*'}}]
                )
            )
        for statement in policy_document_statements:
            bucket.add_to_resource_policy(statement)

        return bucket

    def create_access_logs_bucket(self, logical_id, bucket_name, s3_kms_key) -> s3.Bucket:
        bucket = s3.Bucket(
            self,
            id=logical_id,
            access_control=s3.BucketAccessControl.LOG_DELIVERY_WRITE,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            bucket_key_enabled=True,
            bucket_name=bucket_name,
            encryption=s3.BucketEncryption.KMS,
            encryption_key=s3_kms_key,
            public_read_access=False,
            removal_policy=cdk.RemovalPolicy.RETAIN,
            versioned=True,
            object_ownership=s3.ObjectOwnership.BUCKET_OWNER_PREFERRED,
        )
        bucket.node.add_dependency(s3_kms_key)
        
        return bucket
