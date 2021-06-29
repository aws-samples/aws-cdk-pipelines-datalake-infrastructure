# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import aws_cdk.core as cdk


class EmptyStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        """
        This stack is intentionally left empty
        @param scope: 
        @param construct_id: 
        @param kwargs: 
        """
        super().__init__(scope, construct_id, **kwargs)
        pass
