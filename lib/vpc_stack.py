# Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import aws_cdk.core as cdk
import aws_cdk.aws_ec2 as ec2
from .configuration import VPC_CIDR, get_logical_id_prefix, get_path_mapping, get_ssm_parameter


class VpcStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, target_environment: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        mappings = get_path_mapping(target_environment)
        vpc_cidr = get_ssm_parameter(mappings[VPC_CIDR])
        logical_id_prefix = get_logical_id_prefix()
        vpc = ec2.Vpc(self, f'{logical_id_prefix}Vpc', cidr=vpc_cidr)
        shared_security_group_ingress = ec2.SecurityGroup(
            self,
            f'{target_environment}{logical_id_prefix}SharedIngressSecurityGroup',
            vpc=vpc,
            description='Shared Security Group for Data Lake resources with self-referencing ingress rule.',
            security_group_name=f'{target_environment}{logical_id_prefix}SharedIngressSecurityGroup',
        )
        shared_security_group_ingress.add_ingress_rule(
            peer=shared_security_group_ingress,
            connection=ec2.Port.all_traffic(),
            description='Self-referencing ingress rule',
        )
        vpc.add_gateway_endpoint(
            f'{target_environment}{logical_id_prefix}S3Endpoint',
            service=ec2.GatewayVpcEndpointAwsService.S3
        )
        vpc.add_gateway_endpoint(
            f'{target_environment}{logical_id_prefix}DynamoEndpoint',
            service=ec2.GatewayVpcEndpointAwsService.DYNAMODB
        )
        vpc.add_interface_endpoint(
            f'{target_environment}{logical_id_prefix}GlueEndpoint',
            service=ec2.InterfaceVpcEndpointAwsService.GLUE,
            security_groups=[shared_security_group_ingress],
        )
        vpc.add_interface_endpoint(
            f'{target_environment}{logical_id_prefix}KmsEndpoint',
            service=ec2.InterfaceVpcEndpointAwsService.KMS,
            security_groups=[shared_security_group_ingress],
        )
        vpc.add_interface_endpoint(
            f'{target_environment}{logical_id_prefix}SsmEndpoint',
            service=ec2.InterfaceVpcEndpointAwsService.SSM,
            security_groups=[shared_security_group_ingress],
        )
        vpc.add_interface_endpoint(
            f'{target_environment}{logical_id_prefix}SecretsManagerEndpoint',
            service=ec2.InterfaceVpcEndpointAwsService.SECRETS_MANAGER,
            security_groups=[shared_security_group_ingress],
        )
        vpc.add_interface_endpoint(
            f'{target_environment}{logical_id_prefix}StepFunctionsEndpoint',
            service=ec2.InterfaceVpcEndpointAwsService.STEP_FUNCTIONS,
            security_groups=[shared_security_group_ingress],
        )

        # Assign resources for export to SSM Parameter Store
        self.vpc = vpc
        self.shared_security_group_ingress = shared_security_group_ingress
