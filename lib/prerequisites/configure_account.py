# Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import sys
import boto3

from lib.configuration import (
    ACCOUNT_ID, DEPLOYMENT, DEV, GITHUB_TOKEN, REGION, TEST, PROD, VPC_CIDR, get_path_mapping
)

all_parameters = {
    DEPLOYMENT: {
        ACCOUNT_ID: '',
        REGION: 'us-west-2',
        GITHUB_TOKEN: '',
    },
    DEV: {
        ACCOUNT_ID: '',
        REGION: 'us-west-2',
        VPC_CIDR: '10.0.0.0/16'
    },
    TEST: {
        ACCOUNT_ID: '',
        REGION: 'us-west-2',
        VPC_CIDR: '10.0.0.0/16'
    },
    PROD: {
        ACCOUNT_ID: '',
        REGION: 'us-west-2',
        VPC_CIDR: '10.0.0.0/16'
    }
}


if __name__ == '__main__':
    target_environment = None
    if bool(len(sys.argv[1:])) and sys.argv[1] in [DEPLOYMENT,DEV,TEST,PROD]:
        target_environment = sys.argv[1]
    else:
        error_msg = (
            'To configure an account you must provide a valid environment identifier argument.\n\n'
            'Options: Deployment, Dev, Test, or Prod\n\n'
            'Example: python lib/prerequisites/configure_account.py Dev'
        )
        raise Exception(error_msg)

    mappings = get_path_mapping(target_environment)
    parameters = all_parameters[target_environment]
    response = input((
        f'Are you sure you want to deploy:\n\n{parameters}\n\n'
        f'To account: {boto3.client("sts").get_caller_identity().get("Account")}?\n\n'
        '(y/n)'
    ))

    if response.lower() == 'y':
        ssm_client = boto3.client('ssm')
        for i, (k,v) in enumerate(parameters.items()):
            parameter_key = mappings[k]
            print(f'{parameter_key} {v}')
            if bool(v):
                print(f'Pushing Parameter: {parameter_key} {v}')
                ssm_client.put_parameter(
                    Name=parameter_key,
                    Value=v,
                    Type='String',
                    Overwrite=True,
                )
            else:
                print(f'Skipping empty value for: {parameter_key}')