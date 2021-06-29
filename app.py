# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

# !/usr/bin/env python3

import os
import aws_cdk.core as cdk

from lib.pipeline_stack import PipelineStack
from lib.empty_stack import EmptyStack
from lib.configuration import (
    ACCOUNT_ID, DEPLOYMENT, DEV, TEST, PROD, REGION,
    get_logical_id_prefix, get_path_mappings, get_ssm_parameter
)
from lib.tagging import tag

app = cdk.App()

if bool(os.environ.get('IS_BOOTSTRAP')):
    EmptyStack(app, 'StackStub')
else:
    raw_mappings = get_path_mappings()

    # NOTE: Boto3 is required due to CDK design where the environment parameter
    #       must be a static (non-contextual) value.
    #       Reference: https://github.com/aws/aws-cdk/issues/4096
    deployment_account = get_ssm_parameter(raw_mappings[DEPLOYMENT][ACCOUNT_ID])
    deployment_region = get_ssm_parameter(raw_mappings[DEPLOYMENT][REGION])
    deployment_aws_env = {
        'account': deployment_account,
        'region': deployment_region,
    }
    logical_id_prefix = get_logical_id_prefix()
    
    if os.environ.get('ENV', DEV) == DEV:
        target_environment = DEV
        dev_account = get_ssm_parameter(raw_mappings[DEV][ACCOUNT_ID])
        dev_region = get_ssm_parameter(raw_mappings[DEV][REGION])
        dev_aws_env = {
            'account': dev_account,
            'region': dev_region,
        }
        dev_pipeline_stack = PipelineStack(
            app,
            f'{target_environment}{logical_id_prefix}InfrastructurePipeline',
            target_environment=DEV,
            target_branch='main',
            target_aws_env=dev_aws_env,
            env=deployment_aws_env,
        )
        tag(dev_pipeline_stack, DEPLOYMENT)

    if os.environ.get('ENV', TEST) == TEST:
        target_environment = TEST
        test_account = get_ssm_parameter(raw_mappings[TEST][ACCOUNT_ID])
        test_region = get_ssm_parameter(raw_mappings[TEST][REGION])
        test_aws_env = {
            'account': test_account,
            'region': test_region,
        }
        test_pipeline_stack = PipelineStack(
            app,
            f'{target_environment}{logical_id_prefix}InfrastructurePipeline',
            target_environment=TEST,
            target_branch='test',
            target_aws_env=test_aws_env,
            env=deployment_aws_env,
        )
        tag(test_pipeline_stack, DEPLOYMENT)

    if os.environ.get('ENV', PROD) == PROD:
        target_environment = PROD
        prod_account = get_ssm_parameter(raw_mappings[PROD][ACCOUNT_ID])
        prod_region = get_ssm_parameter(raw_mappings[PROD][REGION])
        prod_aws_env = {
            'account': prod_account,
            'region': prod_region,
        }
        prod_pipeline_stack = PipelineStack(
            app,
            f'{target_environment}{logical_id_prefix}InfrastructurePipeline',
            target_environment=PROD,
            target_branch='production',
            target_aws_env=prod_aws_env,
            env=deployment_aws_env,
        )
        tag(prod_pipeline_stack, DEPLOYMENT)

app.synth()
