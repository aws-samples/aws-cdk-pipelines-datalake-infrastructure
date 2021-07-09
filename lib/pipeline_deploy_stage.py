# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import aws_cdk.core as cdk
from .vpc_stack import VpcStack
from .s3_bucket_zones_stack import S3BucketZonesStack
from .tagging import tag
from .configuration import get_logical_id_prefix


class PipelineDeployStage(cdk.Stage):
    def __init__(
        self, scope: cdk.Construct, construct_id: str,
        target_environment: str, deployment_account_id: str,
        **kwargs
    ):
        """
        Adds deploy stage to CodePipeline

        @param scope cdk.Construct: Parent of this stack, usually an App or a Stage, but could be any construct.
        @param construct_id str:
            The construct ID of this stack. If stackName is not explicitly defined,
            this id (and any parent IDs) will be used to determine the physical ID of the stack.
        @param target_environment str: The target environment for stacks in the deploy stage
        @param deployment_account_id: The id for the deployment account
        @param kwargs:
        """
        super().__init__(scope, construct_id, **kwargs)

        logical_id_prefix = get_logical_id_prefix()

        vpc_stack = VpcStack(
            self,
            f'{target_environment}{logical_id_prefix}InfrastructureVpc',
            target_environment=target_environment,
            **kwargs,
        )
        bucket_stack = S3BucketZonesStack(
            self,
            f'{target_environment}{logical_id_prefix}InfrastructureS3BucketZones',
            target_environment=target_environment,
            deployment_account_id=deployment_account_id,
            **kwargs,
        )

        tag(vpc_stack, target_environment)
        tag(bucket_stack, target_environment)
