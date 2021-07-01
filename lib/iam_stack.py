# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import aws_cdk.core as cdk
from aws_cdk.aws_iam import AccountPrincipal, Effect, PolicyDocument, PolicyStatement, Role
from .configuration import (
    CROSS_ACCOUNT_DYNAMODB_ROLE, get_path_mapping, get_logical_id_prefix, get_resource_name_prefix
)


class IamStack(cdk.Stack):
    def __init__(
        self, scope: cdk.Construct, construct_id: str,
        target_environment: str, deployment_account_id: str,
        **kwargs
    ) -> None:
        """
        Creates a CloudFormation stack for AWS IAM resources. It includes an IAM role with DynamoDB permissions.

        @param scope cdk.Construct: Parent of this stack, usually an App or a Stage, but could be any construct.:
        @param construct_id str:
            The construct ID of this stack. If stackName is not explicitly defined,
            this id (and any parent IDs) will be used to determine the physical ID of the stack.
        @param target_environment str: The target environment for stacks in the deploy stage
        @param deployment_account_id:
        @param kwargs:
        """
        super().__init__(scope, construct_id, **kwargs)

        mappings = get_path_mapping(target_environment)
        logical_id_prefix = get_logical_id_prefix()
        resource_name_prefix = get_resource_name_prefix()

        cross_account_dynamodb_role = Role(
            self,
            f'{target_environment}{logical_id_prefix}CrossAccountDynamoDbRole',
            description='Cross Account Role used for managing DynamoDb tables and their records.',
            role_name=f'{target_environment.lower()}-{resource_name_prefix}-cross-account-dynamodb-role',
            assumed_by=AccountPrincipal(deployment_account_id),
            inline_policies=[PolicyDocument(
                statements=[
                    PolicyStatement(
                        sid='DynamoDbPolicy',
                        effect=Effect.ALLOW,
                        actions=[
                            'dynamodb:GetItem',
                            'dynamodb:PutItem',
                            'dynamodb:UpdateItem',
                        ],
                        resources=[
                            'arn:aws:dynamodb:*:*:table/*',
                        ],
                    ),
                ]
            )]
        )

        # Stack Outputs that are programmatically synchronized
        cdk.CfnOutput(
            self,
            f'{target_environment}{logical_id_prefix}CrossAccountDynamoDbRoleArn',
            value=cross_account_dynamodb_role.role_arn,
            export_name=mappings[CROSS_ACCOUNT_DYNAMODB_ROLE]
        )
