# Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import boto3

# Environments (targeted at accounts)
DEPLOYMENT = 'Deployment'
DEV = 'Dev'
TEST = 'Test'
PROD = 'Prod'

# The following constants are used to map to parameter/secret paths
ENVIRONMENT = 'environment'
## Manual Inputs
GITHUB_REPOSITORY_OWNER_NAME = 'github_repository_owner_name'
GITHUB_REPOSITORY_NAME = 'github_repository_name'
GITHUB_TOKEN = 'github_token'
ACCOUNT_ID = 'account_id'
REGION = 'region'
LOGICAL_ID_PREFIX = 'logical_id_prefix'
RESOURCE_NAME_PREFIX = 'resource_name_prefix'
VPC_CIDR = 'vpc_cidr'
## Used in Automated Outputs
VPC_ID = 'vpc_id'
AVAILABILITY_ZONES = 'availability_zones'
SUBNET_IDS = 'subnet_ids'
ROUTE_TABLES = 'route_tables'
SHARED_SECURITY_GROUP_ID = 'shared_security_group_id'
S3_KMS_KEY = 's3_kms_key'
S3_ACCESS_LOG_BUCKET = 's3_access_log_bucket'
S3_RAW_BUCKET = 's3_raw_bucket'
S3_CONFORMED_BUCKET = 's3_conformed_bucket'
S3_PURPOSE_BUILT_BUCKET = 's3_purpose_built_bucket'


def get_path_mapping(environment: str) -> dict:
    return {
        ENVIRONMENT: environment,
        ACCOUNT_ID: f'/DataLake/{environment}/AccountId',
        REGION: f'/DataLake/{environment}/Region',
        VPC_CIDR: f'/DataLake/{environment}/VpcCidr',
        VPC_ID: f'/DataLake/{environment}/VpcId',
        AVAILABILITY_ZONES: f'/DataLake/{environment}/AvailabilityZones',
        SUBNET_IDS: f'/DataLake/{environment}/SubnetIds',
        ROUTE_TABLES: f'/DataLake/{environment}/RouteTables',
        SHARED_SECURITY_GROUP_ID: f'/DataLake/{environment}/SharedSecurityGroupId',
        S3_KMS_KEY: f'/DataLake/{environment}/S3KmsKeyArn',
        S3_ACCESS_LOG_BUCKET: f'/DataLake/{environment}/S3AccessLogBucket',
        S3_RAW_BUCKET: f'/DataLake/{environment}/RawBucketName',
        S3_CONFORMED_BUCKET: f'/DataLake/{environment}/ConformedBucketName',
        S3_PURPOSE_BUILT_BUCKET: f'/DataLake/{environment}/PurposeBuiltBucketName',
    }

def get_path_mappings() -> dict:
    """Returns a dict mapping of all keys used for configurations of environments.
    
    These keys correspond to Parameter Store or Secrets Manager (passwords only) records.
    """
    return {
        DEPLOYMENT: {
            ENVIRONMENT: DEPLOYMENT,
            ACCOUNT_ID: f'/DataLake/{DEPLOYMENT}/AccountId',
            REGION: f'/DataLake/{DEPLOYMENT}/Region',
            GITHUB_TOKEN: '/DataLake/GithubToken',
            GITHUB_REPOSITORY_OWNER_NAME: f'/DataLake/Infrastructure/RepositoryOwnerName',
            GITHUB_REPOSITORY_NAME: f'/DataLake/Infrastructure/RepositoryName',
            LOGICAL_ID_PREFIX: f'/DataLake/Infrastructure/CloudFormationLogicalIdPrefix',
            RESOURCE_NAME_PREFIX: f'/DataLake/Infrastructure/ResourceNamePrefix',
        },
        DEV: get_path_mapping(DEV),
        TEST: get_path_mapping(TEST),
        PROD: get_path_mapping(PROD),
    }

def get_ssm_parameter(parameter_key: str):
    return boto3.client('ssm').get_parameter(Name=parameter_key)['Parameter']['Value']

def get_logical_id_prefix() -> str:
    return get_ssm_parameter(get_path_mapping(DEPLOYMENT)[LOGICAL_ID_PREFIX])

def get_resource_name_prefix() -> str:
    return get_ssm_parameter(get_path_mapping(DEPLOYMENT)[RESOURCE_NAME_PREFIX])

def get_repository_owner() -> str:
    return get_ssm_parameter(get_path_mapping(DEPLOYMENT)[GITHUB_REPOSITORY_OWNER_NAME])

def get_repository_name() -> str:
    return get_ssm_parameter(get_path_mapping(DEPLOYMENT)[GITHUB_REPOSITORY_NAME])
