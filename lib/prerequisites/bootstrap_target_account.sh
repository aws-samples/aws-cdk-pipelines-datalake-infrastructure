# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

set -e

if [ -z $1 ] ; then
    echo "You must provide the Deployment AWS Account Id"
    exit 1
fi

if [ -z $2 ] ; then
    echo "You must provide cloudformation execution IAM policies "
    exit 1
fi


if aws sts get-caller-identity > /dev/null; then
    export CDK_NEW_BOOTSTRAP=1
    export IS_BOOTSTRAP=1 
    read -r -p "Are you sure you want to bootstrap $(aws sts get-caller-identity) providing a trust relationship to: $1 using policy $2? (y/n) " response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        cdk bootstrap --trust $1 --cloudformation-execution-policies $2 || (unset IS_BOOTSTRAP && unset CDK_NEW_BOOTSTRAP)
        unset IS_BOOTSTRAP && unset CDK_NEW_BOOTSTRAP
    fi
else
    echo "You must configure credentials for the *Target Account*"
fi


