# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import aws_cdk.core as cdk
import aws_cdk.aws_ec2 as ec2
from .configuration import (
    AVAILABILITY_ZONE_1, AVAILABILITY_ZONE_2, AVAILABILITY_ZONE_3, ROUTE_TABLE_1, ROUTE_TABLE_2, ROUTE_TABLE_3,
    SHARED_SECURITY_GROUP_ID, SUBNET_ID_1, SUBNET_ID_2, SUBNET_ID_3, VPC_CIDR, VPC_ID,
    get_environment_configuration, get_logical_id_prefix
)


class VpcStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, target_environment: str, **kwargs) -> None:
        """
        CloudFormation stack to create AWS KMS Key, Amazon S3 resources such as buckets and bucket policies.

        @param scope cdk.Construct:
            Parent of this stack, usually an App or a Stage, but could be any construct.:
        @param construct_id str:
            The construct ID of this stack. If stackName is not explicitly defined,
            this id (and any parent IDs) will be used to determine the physical ID of the stack.
        @param target_environment str: The target environment for stacks in the deploy stage
        """
        super().__init__(scope, construct_id, **kwargs)

        mappings = get_environment_configuration(target_environment)
        vpc_cidr = mappings[VPC_CIDR]
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

        # Stack Outputs that are programmatically synchronized
        cdk.CfnOutput(
            self,
            f'{target_environment}{logical_id_prefix}Vpc',
            value=vpc.vpc_id,
            export_name=mappings[VPC_ID],
        )
        cdk.CfnOutput(
            self,
            f'{target_environment}{logical_id_prefix}VpcAvailabilityZone1',
            value=vpc.availability_zones[0],
            export_name=mappings[AVAILABILITY_ZONE_1],
        )
        cdk.CfnOutput(
            self,
            f'{target_environment}{logical_id_prefix}VpcAvailabilityZone2',
            value=vpc.availability_zones[1],
            export_name=mappings[AVAILABILITY_ZONE_2],
        )
        cdk.CfnOutput(
            self,
            f'{target_environment}{logical_id_prefix}VpcAvailabilityZone3',
            value=vpc.availability_zones[2],
            export_name=mappings[AVAILABILITY_ZONE_3],
        )
        cdk.CfnOutput(
            self,
            f'{target_environment}{logical_id_prefix}VpcPrivateSubnet1',
            value=vpc.private_subnets[0].subnet_id,
            export_name=mappings[SUBNET_ID_1],
        )
        cdk.CfnOutput(
            self,
            f'{target_environment}{logical_id_prefix}VpcPrivateSubnet2',
            value=vpc.private_subnets[1].subnet_id,
            export_name=mappings[SUBNET_ID_2],
        )
        cdk.CfnOutput(
            self,
            f'{target_environment}{logical_id_prefix}VpcPrivateSubnet3',
            value=vpc.private_subnets[2].subnet_id,
            export_name=mappings[SUBNET_ID_3],
        )
        cdk.CfnOutput(
            self,
            f'{target_environment}{logical_id_prefix}VpcRouteTable1',
            value=vpc.private_subnets[0].route_table.route_table_id,
            export_name=mappings[ROUTE_TABLE_1],
        )
        cdk.CfnOutput(
            self,
            f'{target_environment}{logical_id_prefix}VpcRouteTable2',
            value=vpc.private_subnets[1].route_table.route_table_id,
            export_name=mappings[ROUTE_TABLE_2],
        )
        cdk.CfnOutput(
            self,
            f'{target_environment}{logical_id_prefix}VpcRouteTable3',
            value=vpc.private_subnets[2].route_table.route_table_id,
            export_name=mappings[ROUTE_TABLE_3],
        )
        cdk.CfnOutput(
            self,
            f'{target_environment}{logical_id_prefix}SharedSecurityGroup',
            value=shared_security_group_ingress.security_group_id,
            export_name=mappings[SHARED_SECURITY_GROUP_ID]
        )
