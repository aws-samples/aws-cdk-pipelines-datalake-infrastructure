# Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
#!/usr/bin/env python3

import os
import boto3
from aws_cdk import core

from lib.pipeline_stack import PipelineStack
from lib.empty_stack import EmptyStack
from lib.s3_bucket_zones_stack import S3BucketZonesStack
from lib.vpc_stack import VpcStack
from lib.configuration import (
    ACCOUNT_ID, DEPLOYMENT, DEV, TEST, PROD, REGION, 
    get_logical_id_prefix, get_path_mappings,
)
from lib.tagging import tag

app = core.App()

if bool(os.environ.get('IS_BOOTSTRAP')):
    EmptyStack(app, 'StackStub')
elif bool(os.environ.get('IS_DIRECT_DEPLOY')):
    # Retrieve current session values for direct deployments
    session = boto3.session.Session()
    identity = boto3.client("sts").get_caller_identity()
    account = identity.get('Account')
    region = session.region_name
    target_environment=DEV

    logical_id_prefix = get_logical_id_prefix

    vpc_stack = VpcStack(app,
        construct_id=f'{target_environment}-{logical_id_prefix}InfrastructureVpc',
        target_environment=target_environment,
        env={
            'account': account,
            'region': region,
        }
        )
    bucket_stack = S3BucketZonesStack(app,
        f'{target_environment}-{logical_id_prefix}InfrastructureS3BucketZones',
        target_environment=target_environment,
        # deployment_account_id=deployment_account_id,
        deployment_account_id=account,
        env={
            'account': account,
            'region': region,
        }
        )

    tag(vpc_stack, target_environment)
    tag(bucket_stack, target_environment)
else:
    # Get raw mappings for multiple environment/account deployments
    raw_mappings = get_path_mappings()

    # NOTE: Boto3 is required due to the CDK design where the environment parameter
    #       must be a static (non-contextual) value.
    #       Reference: https://github.com/aws/aws-cdk/issues/4096
    client = boto3.client('ssm')
    deployment_account = client.get_parameter(Name=raw_mappings[DEPLOYMENT][ACCOUNT_ID])['Parameter']['Value']
    deployment_region = client.get_parameter(Name=raw_mappings[DEPLOYMENT][REGION])['Parameter']['Value']
    dev_account = client.get_parameter(Name=raw_mappings[DEV][ACCOUNT_ID])['Parameter']['Value']
    dev_region = client.get_parameter(Name=raw_mappings[DEV][REGION])['Parameter']['Value']
    test_account = client.get_parameter(Name=raw_mappings[TEST][ACCOUNT_ID])['Parameter']['Value']
    test_region = client.get_parameter(Name=raw_mappings[TEST][REGION])['Parameter']['Value']
    prod_account=client.get_parameter(Name=raw_mappings[PROD][ACCOUNT_ID])['Parameter']['Value']
    prod_region=client.get_parameter(Name=raw_mappings[PROD][REGION])['Parameter']['Value']

    deployment_aws_env = {
        'account': deployment_account,
        'region': deployment_region,
    }
    dev_aws_env = {
        'account': dev_account,
        'region': dev_region,
    }
    test_aws_env = {
        'account': test_account,
        'region': test_region,
    }
    prod_aws_env = {
        'account': prod_account,
        'region': prod_region,
    }

    target_environment = DEV
    logical_id_prefix = get_logical_id_prefix()
    dev_pipeline_stack = PipelineStack(
        app,
        f'{target_environment}{logical_id_prefix}InfrastructurePipeline',
        target_environment=DEV,
        target_branch='main',
        target_aws_env=dev_aws_env,
        env=deployment_aws_env,
    )
    tag(dev_pipeline_stack, deployment_environment=DEPLOYMENT)

    target_environment = TEST
    logical_id_prefix = get_logical_id_prefix()
    test_pipeline_stack = PipelineStack(
        app,
        f'{target_environment}{logical_id_prefix}InfrastructurePipeline',
        target_environment=TEST,
        target_branch='test',
        target_aws_env=test_aws_env,
        env=deployment_aws_env,
    )
    tag(test_pipeline_stack, deployment_environment=DEPLOYMENT)

    target_environment = PROD
    logical_id_prefix = get_logical_id_prefix()
    prod_pipeline_stack = PipelineStack(
        app,
        f'{target_environment}{logical_id_prefix}InfrastructurePipeline',
        target_environment=PROD,
        target_branch='production',
        target_aws_env=prod_aws_env,
        env=deployment_aws_env,
    )
    tag(prod_pipeline_stack, deployment_environment=DEPLOYMENT)

app.synth()
