# Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import aws_cdk.core as cdk
from .vpc_stack import VpcStack
from .s3_bucket_zones_stack import S3BucketZonesStack
from .iam_stack import IamStack
from .tagging import tag
from .configuration import get_logical_id_prefix


class PipelineDeployStage(cdk.Stage):
    def __init__(self, scope: cdk.Construct, id: str, target_environment: str, deployment_account_id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        logical_id_prefix = get_logical_id_prefix()

        self.vpc_stack = VpcStack(self,
            f'{target_environment}{logical_id_prefix}InfrastructureVpc',
            target_environment=target_environment,
            **kwargs,
        )
        self.bucket_stack = S3BucketZonesStack(self,
            f'{target_environment}{logical_id_prefix}InfrastructureS3BucketZones',
            target_environment=target_environment,
            deployment_account_id=deployment_account_id,
            **kwargs,
        )
        self.iam_stack = IamStack(self,
            f'{target_environment}{logical_id_prefix}InfrastructureIam',
            target_environment=target_environment,
            deployment_account_id=deployment_account_id,
        )

        # Stack Outputs that are programmatically synchronized with Parameter Store
        self.vpc_id = cdk.CfnOutput(self.vpc_stack,
            f'{target_environment}{logical_id_prefix}Vpc',
            value=self.vpc_stack.vpc.vpc_id,
        )
        self.vpc_availability_zones = cdk.CfnOutput(self.vpc_stack,
            f'{target_environment}{logical_id_prefix}VpcAvailabilityZones',
            value=",".join(self.vpc_stack.vpc.availability_zones),
        )
        self.vpc_private_subnets = cdk.CfnOutput(self.vpc_stack,
            f'{target_environment}{logical_id_prefix}VpcPrivateSubnets',
            value=",".join(map(lambda subnet: subnet.subnet_id, self.vpc_stack.vpc.private_subnets)),
        )
        self.vpc_route_tables = cdk.CfnOutput(self.vpc_stack,
            f'{target_environment}{logical_id_prefix}VpcRouteTables',
            value=",".join(map(lambda subnet: subnet.route_table.route_table_id, self.vpc_stack.vpc.private_subnets)),
        )
        self.shared_security_group_ingress = cdk.CfnOutput(self.vpc_stack,
            f'{target_environment}{logical_id_prefix}SharedSecurityGroup',
            value=self.vpc_stack.shared_security_group_ingress.security_group_id,
        )
        self.s3_kms_key = cdk.CfnOutput(self.bucket_stack,
            f'{target_environment}{logical_id_prefix}KmsKey',
            value=self.bucket_stack.s3_kms_key,
        )
        self.access_logs_bucket = cdk.CfnOutput(self.bucket_stack,
            f'{target_environment}{logical_id_prefix}AccessLogsBucketName',
            value=self.bucket_stack.access_logs_bucket,
        )
        self.raw_bucket = cdk.CfnOutput(self.bucket_stack,
            f'{target_environment}{logical_id_prefix}RawBucketName',
            value=self.bucket_stack.raw_bucket.bucket_name,
        )
        self.conformed_bucket = cdk.CfnOutput(self.bucket_stack,
            f'{target_environment}{logical_id_prefix}ConformedBucketName',
            value=self.bucket_stack.conformed_bucket.bucket_name,
        )
        self.purpose_built_bucket = cdk.CfnOutput(self.bucket_stack,
            f'{target_environment}{logical_id_prefix}PurposeBuiltBucketName',
            value=self.bucket_stack.purpose_built_bucket.bucket_name,
            )
        self.cross_account_role = cdk.CfnOutput(self.iam_stack,
            f'{target_environment}{logical_id_prefix}CrossAccountDynamoDbRole',
            value=self.iam_stack.cross_account_dynamodb_role.role_arn,
        )

        tag(self.vpc_stack, target_environment)
        tag(self.bucket_stack, target_environment)
        tag(self.iam_stack, target_environment)
