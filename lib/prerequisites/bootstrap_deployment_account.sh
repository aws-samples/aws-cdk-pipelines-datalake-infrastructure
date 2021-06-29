# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

set -e

if aws sts get-caller-identity > /dev/null; then
    export CDK_NEW_BOOTSTRAP=1
    export IS_BOOTSTRAP=1
    read -r -p "Are you sure you want to bootstrap $(aws sts get-caller-identity)? (y/n)" response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        cdk bootstrap || (unset IS_BOOTSTRAP && unset CDK_NEW_BOOTSTRAP)
        unset IS_BOOTSTRAP && unset CDK_NEW_BOOTSTRAP
    fi
else
    echo "You must configure credentials for the *Central Deployment Account*"
fi
