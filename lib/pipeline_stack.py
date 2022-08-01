# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import aws_cdk as cdk
from constructs import Construct
import aws_cdk.pipelines as Pipelines
import aws_cdk.aws_iam as iam
import aws_cdk.aws_codepipeline_actions as CodePipelineActions
import aws_cdk.aws_codebuild as CodeBuild

from .configuration import (
    ACCOUNT_ID, DEPLOYMENT, GITHUB_REPOSITORY_NAME, GITHUB_REPOSITORY_OWNER_NAME, GITHUB_TOKEN,
    get_logical_id_prefix, get_resource_name_prefix, get_all_configurations
)
from .pipeline_deploy_stage import PipelineDeployStage


class PipelineStack(cdk.Stack):

    def __init__(
        self, scope: Construct, construct_id: str,
        target_environment: str, target_branch: str, target_aws_env: dict,
        **kwargs
    ) -> None:
        """
        CloudFormation stack to create CDK Pipeline resources (Code Pipeline, Code Build, and ancillary resources).

        @param scope cdk.Construct: Parent of this stack, usually an App or a Stage, but could be any construct.
        @param construct_id str:
            The construct ID of this stack. If stackName is not explicitly defined,
            this id (and any parent IDs) will be used to determine the physical ID of the stack.
        @param target_environment str: The target environment for stacks in the deploy stage
        @param target_branch str: The source branch for polling
        @param target_aws_env dict: The CDK env variable used for stacks in the deploy stage
        """
        super().__init__(scope, construct_id, **kwargs)

        self.mappings = get_all_configurations()
        self.create_environment_pipeline(
            target_environment,
            target_branch,
            target_aws_env
        )

    def create_environment_pipeline(self, target_environment, target_branch, target_aws_env):
        """
        Creates CloudFormation stack to create CDK Pipeline resources such as:
        Code Pipeline, Code Build, and ancillary resources.

        @param target_environment str: The target environment for stacks in the deploy stage
        @param target_branch str: The source branch for polling
        @param target_aws_env dict: The CDK env variable used for stacks in the deploy stage
        """

        logical_id_prefix = get_logical_id_prefix()
        resource_name_prefix = get_resource_name_prefix()

        code_build_env = CodeBuild.BuildEnvironment(
            build_image= CodeBuild.LinuxBuildImage.STANDARD_5_0, #from_code_build_image_id("aws/codebuild/amazonlinux2-x86_64-standard:4.0"), #BuildImageConfig. .IBuildImage(),
            privileged = False
        )
        
        code_build_opt = Pipelines.CodeBuildOptions(
            build_environment=code_build_env,
            role_policy=[
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
                        sid='InfrastructurePipelineSTSAssumeRolePolicy',
                        effect=iam.Effect.ALLOW,
                        actions=[
                            'sts:AssumeRole',
                        ],
                        resources=[
                            '*',
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
                    )
            ]
        )

        pipeline = Pipelines.CodePipeline(
            self,
            f'{target_environment}{logical_id_prefix}InfrastructurePipeline',
            pipeline_name=f'{target_environment.lower()}-{resource_name_prefix}-infrastructure-pipeline',
            code_build_defaults=code_build_opt,
            self_mutation=True,
            synth=Pipelines.ShellStep(
                "Synth",
                input=Pipelines.CodePipelineSource.git_hub(
                    repo_string=f"{self.mappings[DEPLOYMENT][GITHUB_REPOSITORY_OWNER_NAME]}/{self.mappings[DEPLOYMENT][GITHUB_REPOSITORY_NAME]}",
                    branch=target_branch,
                    authentication=cdk.SecretValue.secrets_manager(
                    self.mappings[DEPLOYMENT][GITHUB_TOKEN]
                    ),
                    trigger=CodePipelineActions.GitHubTrigger.POLL,
                ),
                commands=["npm install -g aws-cdk",
                            "python -m pip install -r requirements.txt", 
                            "cdk synth"],
            ),
            cross_account_keys=True
        )

        pipeline.add_stage(
            PipelineDeployStage(
                self,
                target_environment,
                target_environment=target_environment,
                deployment_account_id=self.mappings[DEPLOYMENT][ACCOUNT_ID],
                env=cdk.Environment(
                    account=target_aws_env["account"],
                    region=target_aws_env["region"]
                )
            )
        )
