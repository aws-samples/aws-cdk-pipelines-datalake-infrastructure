# Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from aws_cdk.core import Construct, Stack
from aws_cdk.aws_iam import AccountPrincipal, Effect, PolicyDocument, PolicyStatement, Role
from .configuration import (
    get_path_mapping, get_logical_id_prefix, get_resource_name_prefix
)


class IamStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, target_environment: str, deployment_account_id: str,
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.mappings = get_path_mapping(target_environment)
        logical_id_prefix = get_logical_id_prefix()
        resource_name_prefix = get_resource_name_prefix()

        cross_account_dynamodb_role = Role(self,
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
                                                           'dynamodb:*',
                                                       ],
                                                       resources=[
                                                           f'arn:aws:dynamodb:*:*:table/*',
                                                       ],
                                                   ),
                                               ]
                                           )]
                                           )
        self.cross_account_dynamodb_role = cross_account_dynamodb_role
