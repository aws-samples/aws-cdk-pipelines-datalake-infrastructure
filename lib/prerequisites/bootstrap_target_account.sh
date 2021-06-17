# Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

set -e

if [ -z $1 ] ; then
    echo "You must provide the Deployment AWS Account Id"
    exit 1
fi


if aws sts get-caller-identity > /dev/null; then
    export CDK_NEW_BOOTSTRAP=1
    export IS_BOOTS
    
    read -r -p "Are you sure you want to bootstrap $(aws sts get-caller-identity) providing a trust relationship to: $1? (y/n) " response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        cdk bootstrap --trust $1 || (unset IS_BOOTSTRAP && unset CDK_NEW_BOOTSTRAP)
        unset IS_BOOTSTRAP && unset CDK_NEW_BOOTSTRAP
    fi
else
    echo "You must configure credentials for the *Target Account*"
fi


