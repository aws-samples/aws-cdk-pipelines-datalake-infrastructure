# Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
# Treat app as single account deployment
export IS_DIRECT_DEPLOY=1
cdk $@ || unset IS_DIRECT_DEPLOY
unset IS_DIRECT_DEPLOY
