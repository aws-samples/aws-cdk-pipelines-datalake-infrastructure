# Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import aws_cdk.core as cdk
import aws_cdk.pipelines as pipelines
import aws_cdk.aws_iam as iam
import aws_cdk.aws_codepipeline as codepipeline
import aws_cdk.aws_codepipeline_actions as codepipeline_actions

from .configuration import (
    CROSS_ACCOUNT_DYNAMODB_ROLE, DEPLOYMENT, GITHUB_TOKEN, VPC_ID, AVAILABILITY_ZONES, SUBNET_IDS, ROUTE_TABLES,
    SHARED_SECURITY_GROUP_ID, S3_KMS_KEY, S3_ACCESS_LOG_BUCKET, S3_RAW_BUCKET, S3_CONFORMED_BUCKET,
    S3_PURPOSE_BUILT_BUCKET, get_logical_id_prefix, get_resource_name_prefix,
    get_path_mapping,  get_repository_name, get_repository_owner,
)
from .pipeline_deploy_stage import PipelineDeployStage


class PipelineStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, id: str, target_environment: str, target_branch: str, target_aws_env: dict, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.mappings = get_path_mapping(target_environment)

        self.create_environment_pipeline(
            target_environment,
            target_branch,
            target_aws_env
        )

    def create_environment_pipeline(self, target_environment, target_branch, target_aws_env):
        source_artifact = codepipeline.Artifact()
        cloud_assembly_artifact = codepipeline.Artifact()

        logical_id_prefix = get_logical_id_prefix()
        resource_name_prefix = get_resource_name_prefix()

        pipeline = pipelines.CdkPipeline(self, f'{target_environment}{logical_id_prefix}InfrastructurePipeline',
            pipeline_name=f'{target_environment.lower()}-{resource_name_prefix}-infrastructure-pipeline',
            cloud_assembly_artifact=cloud_assembly_artifact,
            source_action=codepipeline_actions.GitHubSourceAction(
                action_name='GitHub',
                branch=target_branch,
                output=source_artifact,
                oauth_token=cdk.SecretValue.secrets_manager(self.mappings[DEPLOYMENT][GITHUB_TOKEN]),
                trigger=codepipeline_actions.GitHubTrigger.POLL,
                owner=get_repository_owner(),
                repo=get_repository_name(),
            ),
            synth_action=pipelines.SimpleSynthAction.standard_npm_synth(
                source_artifact=source_artifact,
                cloud_assembly_artifact=cloud_assembly_artifact,
                install_command='npm install -g aws-cdk && pip3 install -r requirements.txt',
                role_policy_statements=[
                    iam.PolicyStatement(
                        sid='InfrastructurePipelineParameterStorePolicy',
                        effect=iam.Effect.ALLOW,
                        actions=[
                            'ssm:*',
                        ],
                        resources=[
                            f'arn:aws:ssm:{self.region}:{self.account}:parameter/DataLake/*',
                        ],
                    ),
                    iam.PolicyStatement(
                        sid='InfrastructurePipelineSecretsManagerPolicy',
                        effect=iam.Effect.ALLOW,
                        actions=[
                            'secretsmanager:*',
                        ],
                        resources=[
                            f'arn:aws:secretsmanager:{self.region}:{self.account}:secret:/DataLake/*',
                        ],
                    ),
                    iam.PolicyStatement(
                        sid='InfrastructurePipelineKmsPolicy',
                        effect=iam.Effect.ALLOW,
                        actions=[
                            'kms:*',
                        ],
                        resources=[
                            '*',
                        ],
                    ),
                    iam.PolicyStatement(
                        sid='InfrastructurePipelineVpcPolicy',
                        effect=iam.Effect.ALLOW,
                        actions=[
                            'vpc:*',
                        ],
                        resources=[
                            '*',
                        ],
                    ),
                    iam.PolicyStatement(
                        sid='InfrastructurePipelineEc2Policy',
                        effect=iam.Effect.ALLOW,
                        actions=[
                            'ec2:*',
                        ],
                        resources=[
                            '*',
                        ],
                    ),
                ],
                synth_command='cdk synth --verbose',
            ),
            cross_account_keys=True,
        )

        deploy_stage = PipelineDeployStage(self, target_environment,
            target_environment=target_environment,
            deployment_account_id=self.account,
            env=target_aws_env,
        )
        app_stage = pipeline.add_application_stage(deploy_stage)
        app_stage.add_actions(pipelines.ShellScriptAction(
            action_name='SyncParametersWithOutputsAction',
            run_order=app_stage.next_sequential_run_order(), # run after deploy
            additional_artifacts=[source_artifact],
            commands=[
                f"""
                    aws ssm put-parameter \
                        --name {self.mappings[target_environment][VPC_ID]} \
                        --description 'Id for Data Lake VPC' \
                        --value $VPC_ID \
                        --type String \
                        --overwrite
                """,
                f"""
                    aws ssm put-parameter \
                        --name {self.mappings[target_environment][AVAILABILITY_ZONES]} \
                        --description 'Names for Data Lake VPC Availability Zones' \
                        --value $AVAILABILITY_ZONES \
                        --type String \
                        --overwrite
                """,
                f"""
                    aws ssm put-parameter \
                        --name {self.mappings[target_environment][SUBNET_IDS]} \
                        --description 'Comma-seperated Ids for Data Lake VPC Private Subnets' \
                        --value $PRIVATE_SUBNETS \
                        --type String \
                        --overwrite
                """,
                f"""
                    aws ssm put-parameter \
                        --name {self.mappings[target_environment][ROUTE_TABLES]} \
                        --description 'Comma-seperated Ids for Data Lake VPC Private Subnets Route Tables' \
                        --value $ROUTE_TABLES \
                        --type String \
                        --overwrite
                """,
                f"""
                    aws ssm put-parameter \
                        --name {self.mappings[target_environment][SHARED_SECURITY_GROUP_ID]} \
                        --description 'Id for Shared SecurityGroup with self-referencing ingress rule' \
                        --value $SECURITY_GROUP_ID \
                        --type String \
                        --overwrite
                """,
                f"""
                    aws ssm put-parameter \
                        --name {self.mappings[target_environment][S3_KMS_KEY]} \
                        --description 'Arn for KMS Key used for securing S3 Buckets' \
                        --value $KMS_KEY \
                        --type String \
                        --overwrite
                """,
                f"""
                    aws ssm put-parameter \
                        --name {self.mappings[target_environment][S3_ACCESS_LOG_BUCKET]} \
                        --description 'Name of S3 Access Logs bucket' \
                        --value $ACCESS_LOGS_BUCKET_NAME \
                        --type String \
                        --overwrite
                """,
                f"""
                    aws ssm put-parameter \
                        --name {self.mappings[target_environment][S3_RAW_BUCKET]} \
                        --description 'Name of Raw bucket' \
                        --value $RAW_BUCKET_NAME \
                        --type String \
                        --overwrite
                """,
                f"""
                    aws ssm put-parameter \
                        --name {self.mappings[target_environment][S3_CONFORMED_BUCKET]} \
                        --description 'Name of Conformed bucket' \
                        --value $CONFORMED_BUCKET_NAME \
                        --type String \
                        --overwrite
                """,
                f"""
                    aws ssm put-parameter \
                        --name {self.mappings[target_environment][S3_PURPOSE_BUILT_BUCKET]} \
                        --description 'Name of Purpose Built bucket' \
                        --value $PURPOSE_BUILT_BUCKET_NAME \
                        --type String \
                        --overwrite
                """,
                f"""
                    aws ssm put-parameter \
                        --name {self.mappings[target_environment][CROSS_ACCOUNT_DYNAMODB_ROLE]} \
                        --description 'ARN of the cross account DynamoDb Role' \
                        --value $CROSS_ACCOUNT_DYNAMODB_ROLE \
                        --type String \
                        --overwrite
                """,
            ],
            use_outputs={
                'VPC_ID': pipeline.stack_output(deploy_stage.vpc_id),
                'AVAILABILITY_ZONES': pipeline.stack_output(deploy_stage.vpc_availability_zones),
                'PRIVATE_SUBNETS': pipeline.stack_output(deploy_stage.vpc_private_subnets),
                'ROUTE_TABLES': pipeline.stack_output(deploy_stage.vpc_route_tables),
                'SECURITY_GROUP_ID': pipeline.stack_output(deploy_stage.shared_security_group_ingress),
                'KMS_KEY': pipeline.stack_output(deploy_stage.s3_kms_key),
                'ACCESS_LOGS_BUCKET_NAME': pipeline.stack_output(deploy_stage.access_logs_bucket),
                'RAW_BUCKET_NAME': pipeline.stack_output(deploy_stage.raw_bucket),
                'CONFORMED_BUCKET_NAME': pipeline.stack_output(deploy_stage.conformed_bucket),
                'PURPOSE_BUILT_BUCKET_NAME': pipeline.stack_output(deploy_stage.purpose_built_bucket),
                'CROSS_ACCOUNT_DYNAMODB_ROLE': pipeline.stack_output(deploy_stage.cross_account_role),
            },
            role_policy_statements=[
                iam.PolicyStatement(
                    sid='InfrastructurePipelineParameterStorePolicy',
                    effect=iam.Effect.ALLOW,
                    actions=[
                        'ssm:*',
                    ],
                    resources=[
                        f'arn:aws:ssm:{self.region}:{self.account}:parameter/DataLake/*',
                    ],
                )]
            ))
