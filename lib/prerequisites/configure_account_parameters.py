# Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0


import boto3
import re
import json

from lib.configuration import (
    ACCOUNT_ID, DEPLOYMENT, DEV, GITHUB_REPOSITORY_NAME, GITHUB_REPOSITORY_OWNER_NAME,
    LOGICAL_ID_PREFIX, REGION, RESOURCE_NAME_PREFIX, TEST, PROD, VPC_CIDR, get_path_mappings
)

all_parameters = {
    DEPLOYMENT: {
        ACCOUNT_ID: '',
        REGION: 'us-east-2',
        GITHUB_REPOSITORY_OWNER_NAME: '',
        GITHUB_REPOSITORY_NAME: '',
        LOGICAL_ID_PREFIX: '',
        # Important: Resource names may only contain Alphanumeric and hyphens and cannot contain trailing hyphens
        RESOURCE_NAME_PREFIX: '',
    },
    DEV: {
        ACCOUNT_ID: '',
        REGION: 'us-east-2',
        VPC_CIDR: '10.20.0.0/24'
    },
    TEST: {
        ACCOUNT_ID: '',
        REGION: 'us-east-2',
        VPC_CIDR: '10.10.0.0/24'
    },
    PROD: {
        ACCOUNT_ID: '',
        REGION: 'us-east-2',
        VPC_CIDR: '10.0.0.0/24'
    }
}


if __name__ == '__main__':
    for all_parameters_index, (target_environment, parameter_value_mapping) in enumerate(all_parameters.items()):
        for parameters_index, (parameter_key, parameter_value) in enumerate(parameter_value_mapping.items()):
            if not bool(parameter_value):
                raise Exception(f'You must provide a value for: {parameter_key}')
            elif parameter_key == RESOURCE_NAME_PREFIX and (
                not re.fullmatch('^[a-z|0-9|-]+', parameter_value or '-' in parameter_value[-1:] or '-' in parameter_value[1]
            )):
                raise Exception(f'Resource names may only contain lowercase Alphanumeric and hyphens, but cannot '
                                f'contain leading or trailing hyphens') 

    response = input((
        f'Are you sure you want to deploy:\n\n{json.dumps(all_parameters, indent=2)}\n\n'
        f'To account: {boto3.client("sts").get_caller_identity().get("Account")}? '
        'This should be Central Deployment Account Id\n\n'
        '(y/n)'
    ))

    if response.lower() == 'y':
        ssm_client = boto3.client('ssm')
        for all_parameters_index, (target_environment, parameter_value_mapping) in enumerate(all_parameters.items()):
            ssm_path_mappings = get_path_mappings()[target_environment]
            for parameters_index, (parameter_key, parameter_value) in enumerate(parameter_value_mapping.items()):
                ssm_path = ssm_path_mappings[parameter_key]
                print(f'Pushing Parameter: {ssm_path}')
                ssm_client.put_parameter(
                    Name=ssm_path,
                    Value=parameter_value,
                    Type='String',
                    Overwrite=True,
                )
