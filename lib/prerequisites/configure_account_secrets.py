# Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import boto3

from lib.configuration import (
    DEPLOYMENT, GITHUB_TOKEN, get_path_mapping
)

all_secrets = {
    DEPLOYMENT: {
        GITHUB_TOKEN: '',
    },
}


if __name__ == '__main__':
    for all_secrets_index, (target_environment, secret_value_mapping) in enumerate(all_secrets.items()):
        for secrets_index, (secret_key, secret_value) in enumerate(secret_value_mapping.items()):
            if not bool(secret_value):
                raise Exception(f'You must provide a value for: {secret_key}')

    response = input((
        f'Are you sure you want to deploy:\n\n{all_secrets}\n\n'
        f'To account: {boto3.client("sts").get_caller_identity().get("Account")}?\n\n'
        'Note: should be Central Deployment Account Id\n\n'
        '(y/n)'
    ))

    if response.lower() == 'y':
        secrets_client = boto3.client('secretsmanager')
        for all_secrets_index, (target_environment, secret_value_mapping) in enumerate(all_secrets.items()):
            ssm_path_mappings = get_path_mapping(target_environment)
            for secrets_index, (secret_key, secret_value) in enumerate(secret_value_mapping.items()):
                secret_id = ssm_path_mappings[secret_key]
                print(f'Pushing Secret: {secret_id} {secret_value}')
                secrets_client.put_secret_value(
                    SecretId=secret_id,
                    SecretString=secret_value,
                )
