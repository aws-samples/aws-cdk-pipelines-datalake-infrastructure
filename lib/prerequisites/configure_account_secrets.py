# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0


import boto3

from lib.configuration import (
    DEPLOYMENT, GITHUB_TOKEN, get_all_configurations
)

MY_GITHUB_TOKEN = ''


if __name__ == '__main__':
    if not bool(MY_GITHUB_TOKEN):
        raise Exception(f'You must provide a value for: {MY_GITHUB_TOKEN}')

    response = input((
        f'Are you sure you want to add the secrets to AWS Secrets Manager '
        f'in account: {boto3.client("sts").get_caller_identity().get("Account")}?\n\n'
        'This should be the Central Deployment Account Id\n\n'
        '(y/n)'
    ))

    if response.lower() == 'y':
        secrets_client = boto3.client('secretsmanager')
        secret_id = get_all_configurations()[DEPLOYMENT][GITHUB_TOKEN]
        print(f'Pushing Secret: {secret_id}')
        secrets_client.create_secret(Name=secret_id, SecretString=MY_GITHUB_TOKEN)
